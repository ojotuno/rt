import env_var as env

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
      result = result + token + " "
   return result

def resolve_url(url):
  if url[0] == "$":
      arg = url.split("/")
      solvedPath = ""
      for token in arg:
          if token[0] == "$":
              envVar = token[1:]
              solvedPath = solvedPath + env.get(envVar)
          else:
              solvedPath = solvedPath + "/" + token
      return solvedPath
  else:
      return url
