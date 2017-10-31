#HomeNet data getter class

from bs4 import BeautifulSoup
#from datetime import date
from time import sleep
import urllib3
from tinydb import TinyDB, Query
from urllib.parse import urlparse
from django.core.validators import URLValidator

#TODO: 
# Implement ways to handle 'New productions' with "fr. <price>" and 'X-Y rooms' etc. 
# Implement usage of insert_multiple() instead of insert. 


class HtmlInterpretter: 
	"""docstringbject HtmlInterpretter"""
	parseArray = [	
		["li",{"class":"price"},	"price",int],
		["li",{"class":"fee"},		"fee",int],
		["h2",{"class":"property-address"},		"address"],
		["li",{"class":"friendly-property-type--mobile-only"},	"type"],
		["li",{"class":"city"},		"city"],
		["li",{"class":"area"},		"area"],
		["li",{"class":"living-area"},			"living-area",float],
		["li",{"class":"rooms"},				"rooms",float],
		["li",{"class":"supplemental-area"},	"sup-area",float],
		["li",{"class":"price-per-m2"},			"price-per-m2",int]]
		#["a" ,{"class":"item-link-container"},"url"]]
	
	replaceTexts = [" ","kr","/","mån","\n","\xa0","m²","rum","biarea"]

	def urlValid(url):
		urlValid = URLValidator()
		try:
			urlValid(url)
		except:
			return False
		return True

	def clearLine(s):
		r=s 

		for replace in HtmlInterpretter.replaceTexts:
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
				try: 
					value = operation[3](value)
				except:
					print("Couldn't apply", operation[3], "to",value)

			item[operation[2]] = value
		return item

class HomeGetter(object):
	"""docstringbject HomeGetter"""
	def __init__(self,database):
		self.db = TinyDB(database)
		self.urls = [ item["url"] for item in self.db.all() ]  

	def URL_already_in_DB(self,url):
		return url in self.urls

	def GetListingPage(self, url= "", file=""):
		if url:
			http = urllib3.PoolManager()
			r = http.request('GET', url) 
			soup = BeautifulSoup(r.data, 'html.parser')
		elif file:   
			with open(file,"r") as f:
				soup = BeautifulSoup(f.read(), 'html.parser')
			url = "http://www.nolink.com" 

		else: 
			return("No argument passed to GetListingPage()")
			
		resultDiv = soup.find("div",{"id":"result"})

		if resultDiv == None: 
			return("Couldn't find 'Results div'")
			
		Houses = resultDiv.findAll("li", {"class": "results__normal-item"})
		
		parsed_url = urlparse( url )
		url_root = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_url)

		unique_entries = []
		inserted = 0

		for house in Houses:
			item = HtmlInterpretter.CompleteParse(house)
			url_tag = house.find("a",{"class": "item-link-container"})
			
			if item and url_tag: #is not empty dict or empty url_tag
				item["url"] = url_root + url_tag.get("href")
				
				if not self.URL_already_in_DB( item["url"] ):
					self.urls.append( item["url"] )
					inserted += 1
					unique_entries.append(item)
		
		self.db.insert_multiple( unique_entries )

		return inserted
