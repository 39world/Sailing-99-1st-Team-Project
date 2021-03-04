import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient
# client = MongoClient('localhost', 27017)
client = MongoClient('mongodb://test:test@localhost', 27017)
db = client.dbsparta_plus_week4


url = "http://ticket.interpark.com/TPGoodsList.asp?Ca=Eve&SubCa=Eve_O&Sort=1"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get(url, headers=headers)

req = data.text
soup = BeautifulSoup(req, 'html.parser')

shows = soup.select('div > table > tbody > tr')

for show in shows:

    name = show.select_one('td.RKtxt > span > a')
    if name is not None:
        title = name.text
        location = show.select_one('td:nth-child(3) > a').text
        location_url = show.select_one('td:nth-child(3) > a')["href"]

        date = show.select_one('td:nth-child(4)').text
        title_url = show.select_one('td.RKtxt > span > a')["href"]
        title_fix = ('http://ticket.interpark.com') + title_url
        img = show.select_one('td.RKthumb > a > img')["src"]

        doc = {
            'title': title,
            'location': location,
            'date': date,
            'img': img,
            'location_url': location_url,
            'title_fix': title_fix
        }
        db.exhibition.insert_one(doc)
