import pandas as pd
from datetime import datetime
import json
import os.path
import math
import csv
from modules import datasetconfig

CONST_LABEL_GROUP_OVER_TIME = 'over_time'
CONST_LABEL_GROUP_ATOMIC = 'atomic'

def read_json(file_name):
  data = ""
  if not os.path.isfile(file_name):
    print('ERRO: File not found %s' % file_name)
  else:
    # print("Reading json %s..." % file_name)
    with open(file_name) as json_file:
        data = json.load(json_file)
  return data

def get_name_project_formated(name_project):
  return str(name_project.replace("/", "_").replace("-", "_"))

def get_name_project_as_path(name_project):
  return str(name_project.replace("/", ".").replace("-", "."))

def get_complete_path(name_project, entity_full_name):
  return get_name_project_as_path(name_project) + '.' + entity_full_name.replace(" ", "")

def write_json(file_json, path, file_name):
  if os.path.isfile(os.path.join(path, file_name)):
    print('ERRO: File exists %s' % os.path.join(path, file_name))
  else:
    if not os.path.exists(path):
      os.makedirs(path)
    file = open(os.path.join(path, file_name), 'w+')
    print('Creating %s ' % os.path.join(path, file_name))
    json.dump(file_json, file)
    file.close()
  return 

def write_file_to_json(file_json, file_name):
  if os.path.isfile(file_name):
    print('ERRO: File exists %s' % file_name)
  else:
    file = open(file_name, 'w+')
    print('Creating %s ' % file_name)
    json.dump(file_json, file)
    file.close()
  return 

def get_file_name(path, name_project):
  name_project_formated = get_name_project_formated(name_project)
  return path.replace('PROJECT', name_project_formated)

def get_edge_key(node_before_number, node_after_number):
  return str(node_before_number) + "_" + str(node_after_number)

def read_csv(file_name):
  # print("Reading %s..." % file_name)
  dataset = ""
  if not os.path.isfile(file_name):
    print('ERRO: File not found %s' % file_name)
  else:
    dataset = pd.read_csv(file_name, sep=";", keep_default_na=False)
  return dataset

def write_csv_2(file_name, head, lines_map):
  if os.path.isfile(file_name):
    print('ERRO: File exists %s' % file_name)
  else:
    with open(file_name, mode='w+') as csv_file:
      print('Creating %s ...' % file_name)
      writer = csv.DictWriter(csv_file, fieldnames=head)
      for line in lines_map:
        writer.writerow(line)
  pass 

def write_csv(file_name, head, lines_list):
  if os.path.isfile(file_name):
    print('ERRO: File exists %s' % file_name)
  else:
    csvfile = open(file_name,'w+')
    print('Creating %s ...' % file_name)
    csvfile.write(head + '\n')
    for line in lines_list:
      csvfile.write(line + '\n')
    csvfile.close()
  pass 

def write_text(path, file_name, message):
  if os.path.isfile(os.path.join(path, file_name)):
    print('ERRO: File exists %s' % file_name)
  else:
    txtfile = open(os.path.join(path, file_name),'w+')
    print('Creating %s ...' % os.path.join(path, file_name))
    txtfile.write(message)
    txtfile.close()
  pass 

def get_complete_name_language(language):
  return "JavaScript" if language == "js" else "Java"

def get_graph_by_id (id, subgraphs):
  for subgraph in subgraphs:
    if id == subgraph.get('id_intra_project'):
      return subgraph
  return None

def find_subgraph_by_id(language, project_name, subgraph_id):
  return get_graph_by_id(subgraph_id, get_all_subgraphs(language, project_name))
