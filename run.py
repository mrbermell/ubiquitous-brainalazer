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

#Init configuration variables
page = 1
url_root = ""


## Init things from files 
hg = HomeGetter("Homes.db") 

#Config file
with open("config.json","r") as file:
	config = json.load(file)
if "url" in config:
	url_root = config["url"]

if "startPage" in config:
	page = config["startPage"]


if not urlValid(url_root):
	print("Not valid URL")
	exit()


while True:
	if page == 1:
		url = url_root
	else:
		url = url_root + "?page=" + str(page)

	print("Getting:", url)
	return_status = hg.GetListingPage(url=url)		
	

	#Todo make this a more logical check. 
	if type(return_status) == str:  
		print(return_status)
		break

	#Nothing new? Exit! 
	if type(return_status) == int and return_status == 0:
		print("zero houses added. Exiting")
		exit() 

	page += 1

	sleep_seconds = randint(5,50) 
	print("Added", return_status," houses. Sleeping", sleep_seconds,"s.")
	sleep(sleep_seconds)