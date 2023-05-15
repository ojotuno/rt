import env_var as env
import re # regular expresions

def getFullExt(str):
   index = str.find(".")
   return str[index:]

def rm_backslah_from_path(path):
   szPath = len(path)

   if path[szPath -1] == "/":
      return path[:szPath-1]
   else:
      return path

def concat_tokens(tokens):
   result = ""
   for token in tokens:
      result += token + " "
   return result

# resolve a environments vars inside of "$()"" expresion like $(HOME)/$(USER)/dev/projects
def resolve_env_vars(path):
   pattern = r'\$\((\w+)\)'
   matches = re.findall(pattern, path)

   for match in matches:
      env_variable = match
      env_value = env.get(env_variable)
      if env_value:
         path = path.replace(f'$({env_variable})', env_value)
      else:
         print("ERROR: " + env_variable + "environment variable not found")
   return path
   