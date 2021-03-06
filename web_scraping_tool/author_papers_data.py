import requests
import pymysql
from bs4 import BeautifulSoup

#urls
relatedScholars = []
relatedScholars2ndDegree = []
		
#A breadth first search pattern has been implemented to find unique scholars who are related to the input scholar

def breathFirstSearch(url, conn):
	relatedScholars.append(url)
	
	#print parent node name
	r = requests.get(url)
	soup = BeautifulSoup(r.content, "html.parser")

	cur = conn.cursor()
	
	#for every paper listed on profile, get the paper title and author name
	for paper in soup.find_all("tr", {"class": "gsc_a_tr"}):	
		paperTitle = paper.text.encode('ascii', 'ignore').decode('ascii')
		
		author_data = paper.find_all("div", {"class": "gs_gray"})[0]
		authors = author_data.text.encode('ascii', 'ignore').decode('ascii')
		
		print(paperTitle + " " + authors)
		insertDB(paperTitle, authors, cur)		
			
	#first degree - scholars the input scholar has collaborated with
	for link in soup.find_all("a", {"class": "gsc_rsb_aa"}):		
		name = link.text.encode('ascii', 'ignore').decode('ascii')	
		link = "https://scholar.google.co.uk" + link.get('href')
		relatedScholars.append(link)
		
	for link1stDegree in relatedScholars:
		secondDegree(link1stDegree, cur)
		
	cur.close()

#second degree - scholars the first degree scholar has collaborated with		
def secondDegree(url, cur):
	#print parent node name
	r = requests.get(url)
	soup = BeautifulSoup(r.content, "html.parser")
	
	#for every paper listed on profile, get the paper title and author name
	for paper in soup.find_all("tr", {"class": "gsc_a_tr"}):	
		paperTitle = paper.text.encode('ascii', 'ignore').decode('ascii')
		
		author_data = paper.find_all("div", {"class": "gs_gray"})[0]
		authors = author_data.text.encode('ascii', 'ignore').decode('ascii')
		
		print(paperTitle + " " + authors)
		insertDB(paperTitle, authors, cur)	
	
	for link in soup.find_all("a", {"class": "gsc_rsb_aa"}):
		link = "https://scholar.google.co.uk" + link.get('href')
		
		#check if link exists in first degree array and the second degree array
		if link not in relatedScholars:
			if link not in relatedScholars2ndDegree:		
				relatedScholars2ndDegree.append(link)

				r = requests.get(link)
				soup = BeautifulSoup(r.content, "html.parser")
				
				#for every paper listed on profile, get the paper title and author name
				for paper in soup.find_all("tr", {"class": "gsc_a_tr"}):	
					paperTitle = paper.text.encode('ascii', 'ignore').decode('ascii')
					
					author_data = paper.find_all("div", {"class": "gs_gray"})[0]
					authors = author_data.text.encode('ascii', 'ignore').decode('ascii')
					
					print(paperTitle + " " + authors)
					insertDB(paperTitle, authors, cur)	
								
#insert paper and and paper co-authors into db			
def insertDB(paper, authors, cur):	
	paper = paper.replace("'", ":")
	authors = authors.replace("'", ":")
	
	try:
		cur.execute("INSERT into paperCoAuthors (paperTitle, paperAuthors) VALUES ('%s','%s')" % (paper, authors))
		conn.commit()
	except ValueError:
		print("Failed inserting....")			
			
if __name__ == "__main__":
	url = "https://scholar.google.co.uk/citations?user=G0yAJAwAAAAJ&hl=en&oi=ao&cstart=0&pagesize=200"
	
	try:
		print("Connecting to mySQL.....")
		conn = pymysql.connect(host='localhost', db='googlescholardb', user='root', password='', cursorclass=pymysql.cursors.DictCursor)
		print("Connection established!")
	except:
		print("Connection Failed!")
	
	breathFirstSearch(url, conn)
	
	conn.close()