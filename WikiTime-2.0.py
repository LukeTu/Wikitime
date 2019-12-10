import plotly as py
import plotly.figure_factory as ff
import requests
import json
import datetime
import math
import wikipedia


def createdat(name,lang):
    url = 'https://xtools.wmflabs.org/api/page/articleinfo/'+lang+'.wikipedia.org/'+name
    r = requests.get(url)
    raw_info = r.json()
    createdat=str(raw_info['created_at'])
    return createdat

def modifiedat(name,lang):
    url = 'https://xtools.wmflabs.org/api/page/articleinfo/'+lang+'.wikipedia.org/'+name
    r = requests.get(url)
    raw_info = r.json()
    modifiedat=str(raw_info['modified_at'])
    return modifiedat

def revisions(name,lang):
    url = 'https://xtools.wmflabs.org/api/page/articleinfo/'+lang+'.wikipedia.org/'+name
    r = requests.get(url)
    raw_info = r.json()
    revisions=float(raw_info['revisions'])
    return revisions

def duration(name,lang):
    url = 'https://xtools.wmflabs.org/api/page/articleinfo/'+lang+'.wikipedia.org/'+name
    r = requests.get(url)
    raw_info = r.json()
    md = str(raw_info['modified_at'])
    cd = str(raw_info['created_at'])
    d1 = datetime.datetime.strptime(md, '%Y-%m-%d %H:%M')
    d2 = datetime.datetime.strptime(cd, '%Y-%m-%d')
    delta = d1 - d2
    duration=float(str(delta.days))
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

sname = input('Please type the key words for the article name in English: ')
list1=wikipedia.search(sname)
a=0
for i in list1:
    a=a+1
    print(str(a)+". "+i)
name=list1[int(input('Please type a number to select from the listed articles: '))-1]
num = input('How many language versions do you want to analyse : ')
intnum=int(num)
langs = []

z=0

for i in range(intnum):
    z=z+1
    lang = input('Please type the langcode for lang'+str(z)+':')
    langs.append(lang)

print('Progressing...')
print('###',end='\r')

langnames=[]
for enname in langs:
    temp = langname(name,str(enname))
    langnames.append(temp)
print('#####',end='\r')


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
for a,b,c,d,e in zip(langnames,langs,createdats,modifiedats,completes):
        data=[dict(Task=a+" "+str.upper(b),Start=c,Finish=d,Complete=round(e))]
        df.extend(data)

color = ['rgb(255,255,255)', 'rgb(0,0,0)']

F=input('Finished, Please press enter to generate the chart.')
 
fig = ff.create_gantt(df,colors= color, index_col='Complete', title= 'WikiTime for '+ str.title(name) , show_colorbar=False)
fig.update(layout_xaxis_rangeselector_visible=False)

pyplt(fig)




    
    
