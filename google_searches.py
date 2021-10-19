from googlesearch import search
import requests

# search(query, tld='com', lang='en', num=10, start=0, stop=None, pause=2.0)
query = "does not cross the blood brain barrier"

for result in search(query, tld="com", lang='en', num=10, stop=10, pause=2):
    print(result)
