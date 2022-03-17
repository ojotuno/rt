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
