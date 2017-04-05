import requests
import pymysql
import sys
from bs4 import BeautifulSoup
#import bottle_index

#urls
relatedScholars = []
relatedScholars2ndDegree = []
		
#A breadth first search pattern has been implemented to find unique scholars who are related to the input scholar

def breathFirstSearch(url, conn):
	#print parent node name
	r = requests.get(url)
	soup = BeautifulSoup(r.content, "html.parser")
	name_data = soup.find_all("div", {"id": "gsc_prf_in"})[0]
	currentName = name_data.text.encode('ascii', 'ignore').decode('ascii')
	
	cur = conn.cursor()
	
	try:
		cur.execute("INSERT into nodes (scholarName) VALUES ('%s')" % (currentName))
		conn.commit()
	except ValueError:
		print("Failed inserting....")	
	
	#first degree - scholars the input scholar has collaborated with
	for link in soup.find_all("a", {"class": "gsc_rsb_aa"}):
		name = link.text.encode('ascii', 'ignore').decode('ascii')
		print(currentName + " " + name)
		
		#insert name of scholar and current node scholar into db
		try:
			cur.execute("INSERT into connections (sourceScholar, targetScholar) VALUES ('%s','%s')" % (currentName, name))
			conn.commit()
		except ValueError:
			print("Failed inserting....")	
		
		link = "https://scholar.google.co.uk" + link.get('href')
		relatedScholars.append(link)
		
	for link1stDegree in relatedScholars:
		secondDegree(link1stDegree, cur)

	for link2ndDegree in relatedScholars2ndDegree:
		thirdDegree(link2ndDegree, cur)
		
	cur.close()

#second degree - scholars the first degree scholar has collaborated with		
def secondDegree(url, cur):
	r = requests.get(url)
	soup = BeautifulSoup(r.content, "html.parser")
	
	#print parent node name
	r = requests.get(url)
	soup = BeautifulSoup(r.content, "html.parser")
	name_data = soup.find_all("div", {"id": "gsc_prf_in"})[0]
	currentName = name_data.text.encode('ascii', 'ignore').decode('ascii')
	
	try:
		cur.execute("INSERT into nodes (scholarName) VALUES ('%s')" % (currentName))
		conn.commit()
	except ValueError:
		print("Failed inserting....")
	
	for link in soup.find_all("a", {"class": "gsc_rsb_aa"}):
		#print name 
		name = link.text.encode('ascii', 'ignore').decode('ascii')
		print(currentName + " " + name)
				
		#insert name of scholar and current node scholar into db
		try:
			cur.execute("INSERT into connections (sourceScholar, targetScholar) VALUES ('%s','%s')" % (currentName, name))
			conn.commit()
		except ValueError:
			print("Failed inserting....")	

		link = "https://scholar.google.co.uk" + link.get('href')

		#check if link exists in first degree array and the second degree array
		if link not in relatedScholars:
			if link not in relatedScholars2ndDegree:
				relatedScholars2ndDegree.append(link)
		
#third degree - scholars the second degree scholar has collaborated with				
def thirdDegree(url, cur):
	r = requests.get(url)
	soup = BeautifulSoup(r.content, "html.parser")
	
	#print parent node name
	r = requests.get(url)
	soup = BeautifulSoup(r.content, "html.parser")
	name_data = soup.find_all("div", {"id": "gsc_prf_in"})[0]
	currentName = name_data.text.encode('ascii', 'ignore').decode('ascii')
	
	try:
		cur.execute("INSERT into nodes (scholarName) VALUES ('%s')" % (currentName))
		conn.commit()
	except ValueError:
		print("Failed inserting....")

	for link in soup.find_all("a", {"class": "gsc_rsb_aa"}):
		#print name 
		name = link.text.encode('ascii', 'ignore').decode('ascii')
		print(currentName + " " + name)
		name = name.replace("'", ":")
		
		#insert name of scholar and current node scholar into db
		try:
			cur.execute("INSERT into connections (sourceScholar, targetScholar) VALUES ('%s','%s')" % (currentName, name))
			conn.commit()
		except ValueError:
			print("Failed inserting....")	
							
if __name__ == "__main__":

	print("it's author_network.py!!!!!")
	
	try:
		print("Connecting to mySQL.....")
		conn = pymysql.connect(host='localhost', db='googlescholardb', user='root', password='', cursorclass=pymysql.cursors.DictCursor)
		print("Connection established!")
	except:
		print("Connection Failed!")
	
	url = "https://scholar.google.co.uk/citations?user=" + sys.argv[1]
	#print(url)
	#url = "https://scholar.google.co.uk/citations?user=qc6CJjYAAAAJ"
	breathFirstSearch(url, conn)
	print("finish coauthor")
	
	conn.close()