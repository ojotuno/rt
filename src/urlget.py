import wget
import messages as msg

def download_file(url):
    return wget.download(url)
