from HomeDataGetter import HomeGetter, HtmlInterpretter
import json
from time import sleep
from random import randint

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

if not HtmlInterpretter.urlValid(url_root):
	print("Not valid URL")
	exit()


# Main loop
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

	sleep_seconds = randint(5,15) 
	print("Added", return_status," houses. Sleeping", sleep_seconds,"s.")
	config["startPage"] = page
	with open("config.json","w") as file:
		json.dump(config,file)
	sleep(sleep_seconds)

with open("config.json","w") as file:
	config["startPage"] = 1
	json.dump(config,file)