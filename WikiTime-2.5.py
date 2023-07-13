
"""
This visulization tool is based on a gantt chart template from plotly:
https://plotly.com/python/gantt/
Some variables and functions have not been further standardised in naming.
"""

import plotly as py
import plotly.figure_factory as ff
import requests
import json
import datetime
import math
import wikipedia


def generate_params(name, direction, prop):
    return {
        "action": "query",
        "prop": "revisions",
        "titles": name,
        "format": "json",
        "rvlimit": 1,
        "rvdir": direction,
        "rvprop": prop,
    }

def createdat(name, lang):
    S = requests.Session()
    name = name.replace(" ", "_")
    URL = f"https://{lang}.wikipedia.org/w/api.php"
    PARAMS = generate_params(name, "newer", "timestamp")
    R = S.get(url=URL, params=PARAMS)
    DATA = R.json()
    PAGES = DATA["query"]["pages"]
    for k, v in PAGES.items():
        timestamp = v["revisions"][0]["timestamp"]
        dt = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%Y-%m-%d")

def modifiedat(name, lang):
    S = requests.Session()
    name = name.replace(" ", "_")
    URL = f"https://{lang}.wikipedia.org/w/api.php"
    PARAMS = generate_params(name, "older", "timestamp")
    R = S.get(url=URL, params=PARAMS)
    DATA = R.json()
    PAGES = DATA["query"]["pages"]
    for k, v in PAGES.items():
        timestamp = v["revisions"][0]["timestamp"]
        dt = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%Y-%m-%d")

def get_first_last_revision_id(name, lang='en'):
    S = requests.Session()
    name = name.replace(" ", "_")
    URL = f"https://{lang}.wikipedia.org/w/api.php"
    PARAMS_1 = generate_params(name, "newer", "ids")
    R1 = S.get(url=URL, params=PARAMS_1)
    DATA_1 = R1.json()
    PAGES_1 = DATA_1["query"]["pages"]
    for k, v in PAGES_1.items():
        first_revision_id = v["revisions"][0]["revid"]
    PARAMS_2 = generate_params(name, "older", "ids")
    R2 = S.get(url=URL, params=PARAMS_2)
    DATA_2 = R2.json()
    PAGES_2 = DATA_2["query"]["pages"]
    for k, v in PAGES_2.items():
        last_revision_id = v["revisions"][0]["revid"]
    return first_revision_id, last_revision_id

def revisions(name, lang='en'):
    first_revision_id, last_revision_id = get_first_last_revision_id(name, lang)
    url = f'https://{lang}.wikipedia.org/w/rest.php/v1/page/{name.replace(" ", "_")}/history/counts/edits'
    headers = {'User-Agent': 'OpenAI ChatGPT example/0.1 (https://openai.com)'}
    response = requests.get(url, headers=headers, params={'from': first_revision_id, 'to': last_revision_id})
    if response.status_code == 200:
        data = response.json()
        return data['count']
    else:
        return None

def duration(name, lang):
    created_time = datetime.datetime.strptime(createdat(name, lang), "%Y-%m-%d")
    modified_time = datetime.datetime.strptime(modifiedat(name, lang), "%Y-%m-%d")
    delta = modified_time - created_time
    duration = delta.days
    return duration

def frequency(name,lang):
    F=float(revisions(name,lang)/duration(name,lang))
    return F

def langname(enname,lang):
    if lang == 'en':
        return enname
    else:
        url = 'https://en.wikipedia.org/w/api.php?action=query&titles='+enname+'&prop=langlinks&lllang='+lang+'&format=json'
        r = requests.get(url)
        jsonData = r.json()
        langlinks = list(jsonData['query']['pages'].values())[0]["langlinks"]
        for i in range(len(langlinks)):
            langname = langlinks[i]["*"]
        return langname

searchname = input('Please type the key words for the article name in English: ')

namelist=wikipedia.search(searchname)

listcount=0
for i in namelist:
    listcount=listcount+1
    print(str(listcount)+". "+i)
titlename=namelist[int(input('Please type a number to select from the listed articles: '))-1]

#Define the langcodes list for the visulization
langs = [] 

# To set a variable to keep looping
var=1 
while var==1:
  userinput=input("Please type the langcode, use empty input to break")
  langs.append(userinput)
  if userinput == "":
    langs.pop() #Delete the empty input for the list
    break


print('Progressing...')
print('###',end='\r')

#Find the correspond names from the language list.
langnames=[]
try:
  for lang in langs:
      temp = langname(titlename,str(lang))
      langnames.append(temp)
  print('#####',end='\r')
except:
  print("Missing language versions, please look up and try again!")

createdats=[]
for a,b in zip(langnames,langs):
    temp=createdat(a,b)
    createdats.append(temp)
print('########',end='\r')

modifiedats=[]
for a,b in zip(langnames,langs):
    temp=modifiedat(a,b)
    modifiedats.append(temp)



print('###############',end='\r')

M=[]
for a,b in zip(langnames,langs):
    temp=frequency(a,b)
    M.append(temp)
c=100/max(M)

completes=[i*c for i in M]

pyplt = py.offline.plot
df = []
for c,d,e,f,g in zip(langnames,langs,createdats,modifiedats,completes):
        data=[dict(Task=c+" "+str.upper(d),Start=e,Finish=f,Complete=round(g))]
        df.extend(data)

color = ['rgb(255,255,255)', 'rgb(0,0,0)']

F=input('Finished, Please press enter to generate the chart.')

fig = ff.create_gantt(df,colors= color, index_col='Complete', title= 'WikiTime for '+ str.title(titlename) , show_colorbar=False)
fig.update(layout_xaxis_rangeselector_visible=False)

pyplt(fig)
