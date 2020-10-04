import os,csv,json

with open('people.json') as f:
	jsonfile = json.load(f)

with open('student-dev-ports.csv','w') as csvfile:
	streamwriter = csv.write(csvfile,delimiter=' ',quotechar='|', quoting=csv.QUOTE_MINIMAL)
	streamwriter.writerow(['Student Name','Dev Port'])  
	for r in jsonfile: 
		streamwriter.writerow([r['name'],r['dev']]) 
