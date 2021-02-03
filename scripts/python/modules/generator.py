from modules import datasetconfig
from modules import util
import pandas as pd
import re
import logging
import os.path
import networkx as nx
from graphviz import Digraph
import io

#----------------------------  
def extract_graph_data_from_csv(language, csv_file_name):
  dataset = util.read_csv(csv_file_name)
  node_number = 0
  edge_number = 0
  nodes = {}
  edges = {}
  dictionary = datasetconfig.get_dictionary()
  
  for index, row in dataset.iterrows():
    refactoring = row.get('refactoring_name')
    entity_before = row.get('entity_before_full_name').replace(" ", "")
    entity_after = row.get('entity_after_full_name').replace(" ", "")   

    if entity_before not in nodes: 
      nodes[entity_before] = node_number
      node_number += 1
      
    if entity_after not in nodes: 
      nodes[entity_after] = node_number
      node_number += 1     
    
    #Edges properties
    edge = {}
    edge['node_before_number'] = nodes.get(entity_before)
    edge['node_before_entity'] = entity_before
    edge['node_after_number'] = nodes.get(entity_after)
    edge['node_after_entity'] = entity_after
    edge['edge_number'] = edge_number
    edge['refactoring_code'] = dictionary.get(refactoring)

    # Add refactoring and commits properties
    refactoring_and_commit_fields = datasetconfig.get_refactoring_and_commit_fields()
    for field in refactoring_and_commit_fields:
      edge[field] = row.get(field)

    key = util.get_edge_key(edge.get('node_before_number'), edge.get('node_after_number'))
    if key not in edges:
      edges[key] = [] #Iniatize new edge
    edges[key].append(edge)#Including new refactoring
    edge_number += 1  # update edge number

  return {'nodes': nodes, 'edges': edges}

#----------------------------
def create_directed_graph(data):
  
  DG = nx.DiGraph()
  
  nodes = data['nodes']
  edges = data['edges']
  
  #Adding nodes
  for entity in nodes:
    node_index = nodes[entity]
    DG.add_node(node_index)
   
  #Adding edges
  for key in edges:
    list_edges = edges[key]
    for edge in list_edges:#arestas no mesmo sentido.
        DG.add_edge(edge['node_before_number'], edge['node_after_number'])
    
  return {'digraph': DG}

#----------------------------
def get_edges_by_nodes(node_number_1, node_number_2, graph_data):
  
  edges = graph_data['edges']
  edges_selected = []
  
  #loooking for edges in the directed graph
  edge_key_1 = util.get_edge_key(node_number_1, node_number_2)
  edge_key_2 = util.get_edge_key(node_number_2, node_number_1)
  
  if edge_key_1 in edges:
    edges_selected.append(edges[edge_key_1])
    
  if ((edge_key_2) in edges) and (edge_key_1 != edge_key_2):#para arestas entrando e saindo do mesmo vertice
    edges_selected.append(edges[edge_key_2])
    
  return {'edges': edges_selected}

#----------------------------
def extract_subgraphs(name_project, digraph, graph_data):
  
  directed_subgraphs = []
  
  # undirected digraph
  UG = digraph.to_undirected()

  # extract subgraphs
  subgraphs = nx.connected_component_subgraphs(UG)

  #create transactions
  for i, subgraph in enumerate(subgraphs):
    
    directed_subgraph  = {}
    directed_subgraph['id_intra_project'] = i
    directed_subgraph['name_project'] = name_project
    
    #add nodes
    nodes = []
    nodes.extend(subgraph.nodes())
    directed_subgraph['nodes'] = nodes
    
    #add adges
    edges = []
    
    for edge in subgraph.edges():
      node_number_1 = edge[0]
      node_number_2 = edge[1]
      directed_edges = get_edges_by_nodes(node_number_1, node_number_2, graph_data)['edges']
      edges.extend(directed_edges)

    directed_subgraph['edges'] = edges
    
    directed_subgraphs.append(directed_subgraph)
    
  #for i, sg in enumerate(subgraphs):
  #    print ("subgraph {} has {} nodes".format(i, sg.number_of_nodes()))
  #    print ("\tNodes:", sg.nodes(data=True))
  #    print ("\tEdges:", sg.edges(data=True))
  return {'directed_subgraphs': directed_subgraphs}

#----------------------------
def split_supgraphs_atomic_and_overtime(subgraphs):
  subgraphs_same_commit = []
  subgraphs_different_commit = []
  for subgraph in subgraphs:
    subgraph_contains_different_commits = contains_different_commits(subgraph)
    if subgraph_contains_different_commits:
      subgraph['label_group'] = 'overtime' 
      subgraphs_different_commit.append(subgraph)
    else:
      subgraph['label_group'] = 'atomic' 
      subgraphs_same_commit.append(subgraph)
  return {'subgraphs_same_commit': subgraphs_same_commit, 'subgraphs_different_commit': subgraphs_different_commit}

#----------------------------
def contains_different_commits(subgraph):
  edges = subgraph['edges']
  list_commits = []
  for edge in edges:
    for refactoring in edge:
      commit = refactoring['sha1']
      if (len(list_commits) > 0) and (commit not in list_commits): #is a new and different commit
        return True
      list_commits.append(commit)
  return False

#-------------------------------------------------------------
def save_graph_to_html(language, config_graphviz):
  path = '../../dataset/saner-2020/graphviz/{}'.format(config_graphviz.get('project'))
  file_name = '{}_{}_{}.html'.format(config_graphviz.get('label_group'), util.get_name_project_formated(config_graphviz.get('project')), config_graphviz.get('id'))
  if os.path.exists('{}/{}'.format(path,file_name)):
    print('ERRO: File exists {}/{}'.format(path,file_name))
  else:
    if not os.path.exists(path):
      print('Creating path {}'.format(path))
      os.makedirs(path)
    print('Creating {}/{}'.format(path,file_name))
    with io.open((path + '/' + file_name), 'w', encoding='utf8') as f:
      f.write(config_graphviz.get('diggraph').pipe().decode('utf-8'))
  return  

#-------------------------------------------------------------
def create_visualization(language, project_name, subgraphs):
    
  for subgraph in subgraphs:

    diggraph = Digraph(format='svg')
    diggraph.attr('node', shape='point', fixedsize='true', width='0.15')
    id = subgraph.get('id_intra_project')
    label_group = subgraph.get('label_group')

    edges = subgraph.get('edges')

    for edge in edges:
      for refactoring in edge:
        refactoring_name = refactoring.get('refactoring_name')
        entity_before_full_name = refactoring.get('entity_before_full_name')
        entity_after_full_name = refactoring.get('entity_after_full_name')
        diggraph.edge(entity_before_full_name, entity_after_full_name, color='red', label=refactoring_name, len='0.1')
  
    label_text = '\n\nProject: {}, ID: {}, Group: {}'.format(project_name, id, label_group)
    diggraph.attr(bgcolor='gainsboro', label=label_text, fontcolor='black', rankdir='LR', ratio='auto', pad="0.5,0.5")

    config_graphviz = {}
    config_graphviz['project'] = project_name
    config_graphviz['diggraph'] = diggraph
    config_graphviz['id'] = id
    config_graphviz['label_group'] = label_group

    save_graph_to_html(language, config_graphviz)    

  return

#----------------------------
def find_disconnected_subgraphs():

  language = 'java'

  for project_name in datasetconfig.get_java_projects():
    #Read CSV files
    refactorings_file = '../../dataset/saner-2020/refactorings/refactorings_{}_selected_operations.csv'.format(util.get_name_project_formated(project_name))
    graph_data = extract_graph_data_from_csv(language, refactorings_file)
    
    #Create refactoring graphs
    digraph = create_directed_graph(graph_data)['digraph']
    
    #Separate overtime and atomic subgraphs
    subgraphs = extract_subgraphs(project_name, digraph, graph_data)['directed_subgraphs']
    groups_subgraph = split_supgraphs_atomic_and_overtime(subgraphs)
    
    #Save results
    util.write_json(groups_subgraph.get('subgraphs_same_commit'), '../../dataset/saner-2020/graphs/', 'atomic_subgraphs_{}.json'.format(util.get_name_project_formated(project_name)))
    util.write_json(groups_subgraph.get('subgraphs_different_commit'), '../../dataset/saner-2020/graphs/', 'overtime_subgraphs_{}.json'.format(util.get_name_project_formated(project_name)))

  return
  
#----------------------------
def create_views():

  language = 'java'

  for project_name in datasetconfig.get_java_projects():
    #over time graphs
    json_graphs_different_commit = '../../dataset/saner-2020/graphs/overtime_subgraphs_{}.json'.format(util.get_name_project_formated(project_name))
    subgraphs_different_commit = util.read_json(json_graphs_different_commit)
    create_visualization(language, project_name, subgraphs_different_commit)

    #atomic graphs
    json_graphs_same_commit = '../../dataset/saner-2020/graphs/atomic_subgraphs_{}.json'.format(util.get_name_project_formated(project_name))
    subgraphs_same_commit = util.read_json(json_graphs_same_commit)
    create_visualization(language, project_name, subgraphs_same_commit)

  return

