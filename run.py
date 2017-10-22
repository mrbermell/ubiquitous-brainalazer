from HomeDataGetter import HomeGetter
from django.core.validators import URLValidator
import json
from time import sleep
from random import randint


def urlValid(url):
	urlValid = URLValidator()
	try:
		urlValid(url)
	except:
		return False
	return True


## Init things from files 
hg = HomeGetter("Homes.db") 

#Config file
with open("config.json","r") as file:
	config = json.load(file)
if urlValid(config["url"]):
	url_root = config["url"]
else: 
	print("Not valid url")



page = 1



while True:
	if page == 1:
		url = url_root
	else:
		url = url_root + "?page=" + str(page)

	print("Getting:", url)
	return_status = hg.GetListingPage(url=url)		
	

	#Todo make this a more logical check. 
	if type(return_status) == bool:  
		print("Failed to interpret in GetListingPage()")
		break

	page += 1

	sleep_seconds = randint(5,50) 
	print("Added", return_status," houses. Sleeping", sleep_seconds,"s.")
	sleep(sleep_seconds)


#Get first page

#Do the while loop 