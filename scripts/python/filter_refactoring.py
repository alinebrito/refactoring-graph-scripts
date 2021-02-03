from modules import filter
import sys

def graph_generator(option):
  options = {
    0: sys.exit,
    1: filter.filter_core_elements
  }
  options[option]()
  return

def menu():
  print('\n\n0 - Exit')
  print('1 - Filter core refactorings  (remove packages test, sample, example...)')

def run():
  option = 10
  while option != 0:
    menu()
    option = int(input('\nOption: '))
    graph_generator(option)
  return

run()