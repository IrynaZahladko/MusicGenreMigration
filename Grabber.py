
import urllib.request

def Get(url):
    f = urllib.request.urlopen(url)
    page = f.read().decode('utf-8')
    return page

