from modules import util

dictionary = {}
dictionary["RENAME"] = 101
dictionary["PULL_UP"] = 102
dictionary["PUSH_DOWN"] = 103
dictionary["MOVE"] = 104
dictionary["MOVE_RENAME"] = 105
dictionary["EXTRACT"] = 106
dictionary["EXTRACT_MOVE"] = 107
dictionary["INLINE"] = 108
# dictionary["INTERNAL_MOVE"] = 109
# dictionary["INTERNAL_MOVE_RENAME"] = 110

config = {}

config['java_projects'] = {'elastic/elasticsearch', 'ReactiveX/RxJava', 'square/okhttp', 'square/retrofit', 'spring-projects/spring-framework', 'apache/dubbo', 'PhilJay/MPAndroidChart', 'bumptech/glide', 'airbnb/lottie-android', 'facebook/fresco'}

config['refdiff_fields'] = ['name_project', 'sha1', 'entity_before_full_name', 'entity_before_simple_name', 'entity_before_location', 'entity_after_full_name', 'entity_after_simple_name', 'entity_after_location', 'refactoring_level', 'refactoring_name']
#'url', 'entity_before_is_internal_level', 'entity_after_is_internal_level', 'entity_before_parameters', 'entity_after_parameters', 'entity_before_line', 'entity_after_line']


config['commit_fields'] = ['sha1', 'author_name', 'author_email', 'author_date', 'author_date_unix_timestamp']
#, 'abbreviated_commit_hash', 'committer_name', 'committer_email', 'committer_date', 'committer_date_unix_timestamp']
  
config['js_refactoring_level'] = 'Function'
config['js_refactoring_level_formated'] = 'Function'

config['java_refactoring_level'] = 'MethodDeclaration'
config['java_refactoring_level_formated'] = 'Method'

def get_dictionary():
  return dictionary

def get_java_projects():
  return config.get('java_projects')

def get_commit_fields():
  return config.get('commit_fields')

def get_refdiff_fields():
  return config.get('refdiff_fields')

def get_refactoring_and_commit_fields():
  return config.get('refdiff_fields') + config.get('commit_fields')

def check_language(language):
  if (language != 'js') and (language != 'java'):
    print('Invalid language, usage js or java')
  return

def get_refactoring_level(language):
  check_language(language)
  return config.get(language + '_refactoring_level')

def get_refactoring_level_formated(language):
  check_language(language)
  return config.get(language + '_refactoring_level_formated')