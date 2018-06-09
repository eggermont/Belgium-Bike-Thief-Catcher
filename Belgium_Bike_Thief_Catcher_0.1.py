
# coding: utf-8

# In[209]:

from bs4 import BeautifulSoup
import requests
import urllib.request
from datetime import datetime
import pickle
import pandas as pd
import glob
import os
import seaborn as sns
from matplotlib import pyplot as plt

get_ipython().magic('matplotlib inline')


# In[221]:

#parameters
project_folder = '/Users/alexiseggermont/Dropbox (Personal)/01. Personal/04. Models/30. Bike thieves must die/'
weekdays = {0:'1 - Monday',1:'2 - Tuesday',2:'3 - Wednesday',3:'4 - Thursday',4:'5 - Friday',5:'6 - Saturday',6:'7 - Sunday'}
distance = 100 #searches for bikes in that radius from your IP's location, in km
pagesToDownload = 5 #classified are ranked with most recently posted first. Each page contains 35 classifieds.
filename = 'list'


# In[222]:

def findAllItemsInPage(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    mydivs = soup.find_all('div', class_='listed-adv-item') 
    return mydivs


# In[223]:

def getDateForOneItem(item):
    d={}
    d['observed_datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    d['data-adv-id'] = item.attrs['data-adv-id']
    d['data-adv-link'] = item.attrs['data-adv-link']
    img = item.find('img')
    d['price'] = item.find_all('div', class_='listed-item-price')[0].text
    d['description'] = item.find_all('p', class_='description')[0].text
    
    d['seller_link'] = item.find_all('a', class_='listed-adv-item-seller-link')[0].attrs['href']
    d['seller_name'] = item.find_all('a', class_='listed-adv-item-seller-link')[0].text.strip()
    d['listed_datetime'] = item.find_all('time', class_='listed-item-date')[0].attrs['datetime']
    d['address'] = item.find_all('address', class_='listed-item-place')[0].text.strip()
    filename = item.attrs['data-adv-id']+".jpg"
    if filename in not_suspect_ads:
        d['status'] = 'not suspect'
    elif filename in suspect_ads:
        d['status'] = 'suspect'
    else:
        d['status'] = 'not processed'

    try:
        img_link = img.attrs['src']
        if filename not in not_suspect_ads and filename not in suspect_ads:
            urllib.request.urlretrieve(img_link,  project_folder+'Photos/'+filename)
    except:
        img_link = 'no image'
    d['image_link'] = img_link

    return d


# In[224]:

def savedata(filename):
    try:
        with open(project_folder+filename+'.pickle', 'wb') as fp:
            pickle.dump(ls, fp)
    except:
        pass
    df = pd.DataFrame(ls)
    df = df.sort_values('observed_datetime', ascending = False)
    df = df.drop_duplicates(subset = ['data-adv-id'], keep = 'first')
    df = df.sort_values('listed_datetime', ascending = False)
    df.to_excel(project_folder+filename+'.xlsx')
    print(str(len(df))+" bike ads downloaded overall")


# In[225]:

not_suspect_ads = [] #Create a Not suspect folder where you can dump all pictures that you verified aren't your bike
os.chdir(project_folder+"Photos/Not suspect/") #Create a Suspect folder where you can dump all pictures that look like your bike
for file in glob.glob("*.jpg"):
    not_suspect_ads.append(file)

suspect_ads = []
os.chdir(project_folder+"Photos/Suspect/")
for file in glob.glob("*.jpg"):
    not_suspect_ads.append(file)
    
with open (project_folder+'list.pickle', 'rb') as fp:
    ls = pickle.load(fp)
for i in range(pagesToDownload):
    url = 'https://www.2ememain.be/v%C3%A9los/?distance=110000&offset='+str(35*i)
    items = findAllItemsInPage(url)
    for item in items:
        try:
            d = getDateForOneItem(item)
            ls.append(d)
        except Exception as e:
            print('item failed')
            print(e)
            print(item)
savedata(filename)


# In[219]:

#Stats just for fun
df['listed_datetime'] = pd.to_datetime(df['listed_datetime'])
df['weekday'] = df['listed_datetime'].dt.weekday.map(weekdays)
df['hour'] = df['listed_datetime'].dt.hour
df_gb = df.groupby(['hour','weekday'], as_index=False).agg('count')
plt.figure(figsize = (16,5))
sns.heatmap(df_gb.pivot("weekday", "hour", "data-adv-id"), annot=False, cmap="plasma")


# In[220]:

df


# In[ ]:



