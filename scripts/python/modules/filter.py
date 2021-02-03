from modules import datasetconfig
from modules import util
import re
import os.path
import hashlib

import sys

#----------------------------
def contains_test_package(path):
  path = path.split("#")[0]
  test_package = re.findall(r'(test.+?|test)\.', path, re.IGNORECASE)
  contains_test_package = bool(re.search(r'(test.+?|test)\.', path, re.IGNORECASE))
  return contains_test_package

#----------------------------
def contains_sample_package(path):
  path = path.split("#")[0]
  sample_package = re.findall(r'(sample.+?|sample)\.', path, re.IGNORECASE)
  contains_sample_package = bool(re.search(r'(sample.+?|sample)\.', path, re.IGNORECASE))
  return contains_sample_package

#----------------------------
def contains_example_package(path):
  path = path.split("#")[0]
  example_package = re.findall(r'(example.+?|example)\.', path, re.IGNORECASE)
  contains_example_package = bool(re.search(r'(example.+?|example)\.', path, re.IGNORECASE))
  return contains_example_package

#----------------------------
def entity_contains_package(name_package, entity):
  return bool(re.search(r'(^' + name_package + '.|\.' + name_package + '\.|\.' + name_package + '#)', entity, re.IGNORECASE))

#----------------------------
def get_duplicated_edges(dataset):
  list_occurrence_edges = {}
  list_duplicated_edges = []
  separator = '||'
  for index, row in dataset.iterrows():
    entity_before = row.get('entity_before_full_name').replace(" ", "")
    entity_after = row.get('entity_after_full_name').replace(" ", "")   
    sha1 = row.get('sha1')
    key_edge = entity_before + separator + entity_after
    #new edge
    if key_edge not in list_occurrence_edges:
      list_occurrence_edges[key_edge] = 0
    list_occurrence_edges[key_edge] += 1 #new ID
  for key in list_occurrence_edges:
    #is duplicated edge
    if (list_occurrence_edges[key] > 1):
      list_duplicated_edges.append(key)
  return list_duplicated_edges

#----------------------------
def equals_entities(row):
  entity_before = row.get('entity_before_full_name').replace(" ", "")
  entity_after = row.get('entity_after_full_name').replace(" ", "")   
  refactoring_level = row.get('refactoring_level')
  refactoring_name = row.get('refactoring_name')
  sha1 = row.get('sha1')
  is_equals_entities = (entity_before == entity_after)
  return is_equals_entities

#----------------------------
def contains_constructor(row):
  entity_before = row.get('entity_before_full_name').replace(" ", "")
  entity_after = row.get('entity_after_full_name').replace(" ", "")  
  sha1 = row.get('sha1')
  edge_contains_constructor = ("#new(" in entity_before) or ("#new(" in entity_after)
  return edge_contains_constructor

#----------------------------
def contains_duplicated_edges(row, list_duplicated_edges):
  entity_before = row.get('entity_before_full_name').replace(" ", "")
  entity_after = row.get('entity_after_full_name').replace(" ", "")
  sha1 = row.get('sha1')  
  refactoring = row.get('refactoring_name')
  key_edge_1 = entity_before + "||" + entity_after
  key_edge_2 = entity_after + "||" + entity_before
  #Desconecta os dois vértices completamente, para evitar fluxos sem sentido (ida e volta da aresta)
  is_duplicated = (key_edge_1 in list_duplicated_edges) or (key_edge_2 in list_duplicated_edges)
  return is_duplicated

#----------------------------
def entity_contains_exports_keyword(entity):
  return bool(re.search(r'(^exports.|^exports#|\.exports\.|\.exports#|#exports$)', entity, re.IGNORECASE))

#----------------------------
def contains_exports_keyword(row):
  entity_before = row.get('entity_before_full_name').replace(" ", "")
  entity_after = row.get('entity_after_full_name').replace(" ", "")
  return entity_contains_exports_keyword(entity_before) or entity_contains_exports_keyword(entity_after)

#----------------------------
def is_valid_package(path_before, path_after):
  test_package = contains_test_package(path_before) or contains_test_package(path_after)
  sample_package = contains_sample_package(path_before) or contains_sample_package(path_after)
  example_package = contains_example_package(path_before) or contains_example_package(path_after)
  return ((not test_package) and (not sample_package) and (not example_package))

#----------------------------
def is_valid_refactoring(refactoring, list_duplicated_edges):
  is_constructor = contains_constructor(refactoring)  
  is_equals_entities = equals_entities(refactoring)
  is_duplicated_edges = contains_duplicated_edges(refactoring, list_duplicated_edges)
  return ((not is_constructor) and (not is_equals_entities) and (not is_duplicated_edges))

#----------------------------
def is_core_element(list_duplicated_edges, language, name_project, refactoring):
  path_before = refactoring.get('entity_before_full_name')
  path_after = refactoring.get('entity_after_full_name')
  selected_refactoring_level =  datasetconfig.get_refactoring_level(language)
  is_selected_level = (refactoring.get('refactoring_level') == datasetconfig.get_refactoring_level(language))
  is_selected_refactoring_type = (refactoring.get('refactoring_name') in datasetconfig.get_dictionary())
  return (is_valid_package(path_before, path_after) and (is_selected_level) and (is_selected_refactoring_type) and (is_valid_refactoring(refactoring, list_duplicated_edges)))

#----------------------------
def get_key_commit(name_project, sha1):
  return util.get_name_project_formated(name_project) + "_" + str(sha1)

#----------------------------
def write_core_refactorings_to_csv(file_name, refactorings):
  name_output_file =  file_name.replace('.csv', '_selected_operations.csv')
  if os.path.isfile(name_output_file):
    print('ERROR: File %s exist' % name_output_file)
    return
  file = open(name_output_file,'w+')
  commit_fields = datasetconfig.get_commit_fields()
  refdiff_fields = datasetconfig.get_refdiff_fields()
  head_list = refdiff_fields + commit_fields
  head = (";".join(head_list)) + '\n'
  file.write(head)
  separator = ";"
  for refactoring in refactorings:
    line_list = []
    for field in head_list:
      line_list.append(('' if refactoring.get(field) is None else str(refactoring.get(field))))
    line = (";".join(line_list)) + '\n'
    file.write(line)
  file.close()
  print('Creating %s' % name_output_file)
  return

#----------------------------
def add_commit_properties(language, name_project, filtered_refactoring, commits):
  refactorings = []
  commit_fields = datasetconfig.get_commit_fields()
  for refactoring in filtered_refactoring:
    commit_key = get_key_commit(name_project, refactoring.get('sha1'))
    commit = commits.get(commit_key)
    if commit:
      for commit_field in commit_fields: #Adding commit properties (author, date, etc)
        refactoring[commit_field] = commit[commit_field]
      refactorings.append(refactoring)
    else:
      print('Commit {} not found'.format(commit_key))
  return refactorings

#----------------------------
def filter_refactorings(list_duplicated_edges, language, name_project, refactorings, commits):
  filtered_refactoring = []
  for refactoring in refactorings:
    if (is_core_element(list_duplicated_edges, language, name_project, refactoring)):
      filtered_refactoring.append(refactoring)
  return filtered_refactoring

#----------------------------
def extract_refactorings_from_csv(file_name):
  dataset = util.read_csv(file_name)
  refactorings = []
  for index, row in dataset.iterrows():
    refactoring = {}
    fields = datasetconfig.get_refdiff_fields()
    for field in fields:
      refactoring[field] = row.get(field)
    refactorings.append(refactoring)
  return refactorings

#----------------------------
def extract_commits_from_csv(file_name):
  dataset = util.read_csv(file_name)
  commits = {}
  for index, row in dataset.iterrows():
    commit_info = {}
    commit_fields = datasetconfig.get_commit_fields()
    for commit_field in commit_fields:
      commit_info[commit_field] = row.get(commit_field)
    
    #Change author name and email to MD5.
    commit_info['author_name'] = hashlib.md5((commit_info.get('author_name')).encode("utf-8")).hexdigest() 
    commit_info['author_email'] = hashlib.md5((commit_info.get('author_email')).encode("utf-8")).hexdigest() 
    key = get_key_commit(row.get('name_project'), row.get('sha1'))
    commits[key] = commit_info
  return commits

#----------------------------
def filter_core_elements():

  language = 'java'
  for project_name in datasetconfig.get_java_projects():
    commits_file = '../../dataset/saner-2020/commits/commits_{}.csv'.format(util.get_name_project_formated(project_name))
    refactorings_file = '../../dataset/saner-2020/refactorings/refactorings_{}.csv'.format(util.get_name_project_formated(project_name))

    #process commits    
    commits = extract_commits_from_csv(commits_file)    

    #process refactorings
    all_refactorings = extract_refactorings_from_csv(refactorings_file)
    list_duplicated_edges = get_duplicated_edges(util.read_csv(refactorings_file))
    selected_refactorings = filter_refactorings(list_duplicated_edges, language, project_name, all_refactorings, commits)

    #join refactorings and commits
    refactorings_and_commits = add_commit_properties(language, project_name, selected_refactorings, commits)

    #output
    write_core_refactorings_to_csv(refactorings_file, refactorings_and_commits)

  return