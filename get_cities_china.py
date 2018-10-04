import re

import pandas as pd

from bs4 import BeautifulSoup
import requests

url = 'http://aqicn.org/city/all'

html = requests.get(url)

df = pd.DataFrame(columns=['city', 'idx', 'url'])

if html.ok:
    infos = BeautifulSoup(re.findall('CHINA.*MACAO', html.text)[0], 'lxml')

    city_url = []
    cities = infos.find_all('a', href=True)

    name = re.compile('"name":.(\w*\s*\w*)')
    idx = re.compile('"idx":(\d+)')
    i = 0
    print(len(cities))
    for city in cities:
        city_url = city['href']
        
        try:
            city_html = BeautifulSoup(requests.get(city_url).text)

            city_str = city_html(text=idx)
            
            df.loc[i, 'city'] = re.findall(name, city_str[0])[0]
            df.loc[i, 'idx'] = re.findall(idx, city_str[0])[0]
            df.loc[i, 'url'] = city_url

            i+=1
        except:
            print(city_url)

    df.to_csv('cities_china_url.csv')
