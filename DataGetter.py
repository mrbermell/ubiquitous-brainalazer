from bs4 import BeautifulSoup
from datetime import date
from time import sleep
import urllib3
import sys
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from tinydb import TinyDB, Query
from random import randint

url = ""


use_file = True

if use_file:
	f = open("example_firstpage.html","r")
	data = f.read()
	f.close()
	soup = BeautifulSoup(data, 'html.parser')
else:
	http = urllib3.PoolManager()
	r = http.request('GET', url)
	soup = BeautifulSoup(r.data, 'html.parser')

	f = open("example_firstpage.html","w")
	f.write(soup.prettify())
	f.close()

resultDiv = soup.find("div",{"id":"result"})

print("resultDiv == None: ", resultDiv == None)

Houses = resultDiv.findAll("li", {"class": "results__normal-item"})

print("len(SalesItems) =",len(Houses))

for house in Houses[3:10]:
	
	print("-------")
	price = house.find("ul", {"class": "attributes prices"}).getText()
	
	price_info = [line.strip() for line in price.splitlines() 
					if not line.isspace() and len(line)>0]


	price = int(price_info[0].split("kr")[0].strip().replace(" ",""))
	print("price: ", price, "kr")

	if len(price_info)>1:
		

		monthly = int(price_info[1].split("kr")[0].strip().replace("\xa0",""))
		print("monthly:", monthly,"kr")

	
