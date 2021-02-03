import json
import sys
from modules import util
from modules import datasetconfig 
import pandas
import calendar
import time
import sys

def get_vertices(subgraph):
  return subgraph.get('nodes')

def get_edges_id(subgraph):
  edges_id = []
  edges = subgraph.get('edges')
  for edge in edges:
    for refactoring in edge:
      edges_id.append(refactoring['edge_number'])
  return edges_id

def get_distinct_refactorings(subgraph):
  edges = subgraph.get('edges')
  refactorings = set()
  for edge in edges:
    for refactoring in edge:
      refactorings.add(refactoring.get('refactoring_name'))
  return refactorings

def get_commits(subgraph):
  list_commits = set()
  edges = subgraph.get('edges')
  for edge in edges:
    for refactoring in edge:
      list_commits.add(refactoring.get('sha1'))
  return list_commits

def distinct_commits(subgraph):
  list_commits = []
  edges = subgraph.get('edges')
  for edge in edges:
    for refactoring in edge:
      commit = refactoring.get('sha1')
      if (commit not in list_commits):
        list_commits.append({'sha1': commit, 'author_date_unix_timestamp': refactoring.get('author_date_unix_timestamp')})      
  return list_commits

def get_first_and_last_commit(subgraph):  
  list_commits = distinct_commits(subgraph)
  date_last_commit = 0
  date_first_commit = calendar.timegm(time.gmtime())#timestamp now
  last_commit = {}
  first_commit = {}
  for commit in list_commits:
    date = commit.get('author_date_unix_timestamp')
    if date > date_last_commit:
      date_last_commit = date
      last_commit = commit
    if date < date_first_commit:
      date_first_commit = date
      first_commit = commit
  return {'last_commit': last_commit, 'first_commit': first_commit}

def get_age_in_days(subgraph):
    result = get_first_and_last_commit(subgraph)
    last_commit = result.get('last_commit')
    first_commit =  result.get('first_commit')
    interval = last_commit.get('author_date_unix_timestamp') -  first_commit.get('author_date_unix_timestamp')
    days = interval/86400
    return days

def get_distinct_developers(subgraph):
  edges = subgraph.get('edges')
  list_developers = set()
  for edge in edges:
    for refactoring in edge:
      list_developers.add(refactoring.get('author_email'))
  return list_developers