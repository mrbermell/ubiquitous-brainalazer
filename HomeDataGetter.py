#HomeNet data getter class

from bs4 import BeautifulSoup
#from datetime import date
from time import sleep
import urllib3
from tinydb import TinyDB, Query
from urllib.parse import urlparse


class HtmlInterpretter: 
	def clearBlanks(s):
		res = ""
		for line in s.splitlines():
			if not line.isspace() and not line =="":
				res += line.strip() + "\n"
		return res.strip()	

	def PriceText(item, bs):
	
		lines = HtmlInterpretter.clearBlanks(bs.getText()).splitlines()

		SellPriceeStr = lines[0]
		SellPriceeStr = SellPriceeStr.replace(" ","")
		SellPriceeStr = SellPriceeStr.replace("kr","")
		
		try:
			item["price"] = int(SellPriceeStr)
		except ValueError:
			item["price"] = "No price info"

		if len(lines)>1:
			monthlyStr = lines[1]
			monthlyStr = monthlyStr.replace(" ","")
			monthlyStr = monthlyStr.split("kr")[0]
			item["monthly"] = int(monthlyStr.replace("\xa0",""))
		
		return True

	def LocationText(item, bs):
		s = HtmlInterpretter.clearBlanks(bs.getText())
		s = s.splitlines()
		
		item["address"] = s[2]
		item["type"] = s[4]
		item["city"] = s[5]
		try:
			item["district"] = s[6]
		except:
			item["district"] = "<no district>" 
		return True

	def Size(item, bs):
		s = HtmlInterpretter.clearBlanks(bs.getText())
		s = s.replace(",",".")
		
		lines = s.splitlines()

		item["sq meters"] = float(lines[0].split(" ")[0])
		item["rooms"] = float(lines[1].split(" ")[0])

		# Size of ground plot
		groundText = [line for line in lines if line.find("tomt")>0 ]
		if len(groundText):
			groundText = groundText[0]
			groundText = groundText.replace(" ","")
			groundText = groundText.replace("\xa0","")
			s = ""
			for c in groundText:
				if c.isdigit():
					s += c 
				else:
					break 

			item["land area"] = float(s)

			if groundText.find("ha")>0:
				item["land area"] = item["land area"] * 1e4 


		#size of biarea
		biAreaText = [line for line in lines if line.find("biarea")>0 ]
		if len(biAreaText):
			biAreaText = biAreaText[0]
			item["biarea"] = float(biAreaText.split(" ")[0])

class HomeGetter(object):
	"""docstringbject HomeGetter"""
	def __init__(self,database):
		self.db = TinyDB(database)
		pass

	def __DB_insert(self, item):
		#Check for duplicates and insert if there are none
		
		same_url_items = self.db.search(s.url == item["url"])
		if not same_url_items: #no items with same url
			self.db.insert(item)
			return True
		else:
			return False
		

	def ParseHtml(self,li_tag,url_root):
		dict_item = {}

		try: 
			#Link, 
			dict_item["url"] = url_root + li_tag.find("a",{"class": "item-link-container"}).get("href")

			#price and monthly
			priceContainer = li_tag.find("ul", {"class": "attributes prices"})
			HtmlInterpretter.PriceText(dict_item, priceContainer)

			# Location 
			locationContainer = li_tag.find("ul", {"class": "location-type"})
			HtmlInterpretter.LocationText(dict_item, locationContainer)

			# Size 
			sizeContainer = li_tag.find("ul", {"class": "size"})
			HtmlInterpretter.Size(dict_item, sizeContainer)

		except Exception as e:
			print("-"*20, HtmlInterpretter.clearBlanks(house.getText()))
			print("CAUGHT UNHANDLED ERROR:", type(e))
			exit()

		return dict_item

	def GetListingPage(self, url= "", file=""):


		if url:
			http = urllib3.PoolManager()
			r = http.request('GET', url) 
			soup = BeautifulSoup(r.data, 'html.parser')
		
		if file:   
			f = open("example_firstpage.html","r")
			data = f.read()
			f.close()
			soup = BeautifulSoup(data, 'html.parser')
		
		else: #No argument passed
			return False
		
		resultDiv = soup.find("div",{"id":"result"})

		if resultDiv == None: 
			return False

		Houses = resultDiv.findAll("li", {"class": "results__normal-item"})
		
		parsed_uri = urlparse( url )
		url_root = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)

		for house in Houses:
			item = self.ParseHtml(house, url_root)
			if item: #is not empty dict
				self.__DB_insert(item)
		
		return True




			


