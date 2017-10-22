#HomeNet data getter class

from bs4 import BeautifulSoup
#from datetime import date
from time import sleep
import urllib3
from tinydb import TinyDB, Query
from urllib.parse import urlparse


#print("{:,}".format(value))


class HtmlInterpretter: 
	
	parseArray = [	["li",{"class":"price"},"price",int],
					["li",{"class":"fee"},"fee",int],
					["h2",{"class":"property-address"},"address"],
					["h2",{"class":"friendly-property-type--mobile-only"},"type"],
					["li",{"class":"city"},"city"],
					["li",{"class":"area"},"area"],
					["li",{"class":"living-area"},"living-area",float],
					["li",{"class":"rooms"},"rooms",float],
					["li",{"class":"supplemental-area"},"sup-area",float],
					["li",{"class":"price-per-m2"},"price-per-m2",int]]
					#["a" ,{"class":"item-link-container"},"url"]]
	
	replaceTexts=[" ","kr","/","mån","\n","\xa0","m²","rum","biarea"]

	def clearLine(s,replaceTextArray=[]):
		r=s 
		if not replaceTextArray:
			replaceTextArray = HtmlInterpretter.replaceTexts

		for replace in replaceTextArray:
			r = r.replace(replace,"")
		
		r = r.replace(",",".")
		return r



	def CompleteParse(bs):
		item = {}

		for operation in HtmlInterpretter.parseArray:
			tag = bs.find(operation[0], operation[1])
			if tag == None:
				continue
			
			value = tag.getText().strip()
			
			if value == "":
				continue

			if len(operation) == 4:
				value = HtmlInterpretter.clearLine(value)
				value = operation[3](value)
			
			item[operation[2]] = value

		return item

class HomeGetter(object):
	"""docstringbject HomeGetter"""
	def __init__(self,database):
		self.db = TinyDB(database)
		pass

	def __DB_insert(self, item):
		#Check for duplicates and insert if there are none
		s=Query()
		same_url_items = self.db.search(s.url == item["url"])
		if not same_url_items: #no items with same url
			self.db.insert(item)
			return True
		else:
			return False

	def GetListingPage(self, url= "", file=""):


		if url:
			http = urllib3.PoolManager()
			r = http.request('GET', url) 
			soup = BeautifulSoup(r.data, 'html.parser')
		elif file:   
			f = open(file,"r")
			data = f.read()
			f.close()
			soup = BeautifulSoup(data, 'html.parser')
		else: #No argument passed
			print("lol")
			return False
		
		resultDiv = soup.find("div",{"id":"result"})

		if resultDiv == None: 
			print("lol2")
			return False

		Houses = resultDiv.findAll("li", {"class": "results__normal-item"})
		
		parsed_uri = urlparse( url )
		url_root = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)

		inserted = 0

		for house in Houses:
			item = HtmlInterpretter.CompleteParse(house)
			a_tag = house.find("a",{"class": "item-link-container"})
			
			if item and a_tag: #is not empty dict
				item["url"] = url_root + a_tag.get("href")
				self.__DB_insert(item)
				inserted += 1

		return inserted
