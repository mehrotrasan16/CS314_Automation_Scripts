import json
import os
import glob
import sys
import pandas as pd
#os.chdir('/media/sanketm/Data/Temp/CS314/csucs314fa20-repo/students/tests/sprint2') # path to the students repo

all_jsons = glob.glob('/media/sanketm/Data/Temp/CS314/csucs314fa20-repo/students/tests/sprint2/*.json') # get list of all json files

student_dict = {}                                                     
count = 0
student_rec = []

# print(all_jsons)

for file in all_jsons: 
	print(file)
	with open(file,'r') as f:
		try:	
			jsonfile = json.load(f)
			student_rec = []
			eid = file.split("sprint2")[1].split("-")[0].split("/")[1] # splitting ./shlok-distance.json to get shlok
			req = file.split("sprint2")[1].split("-")[1].split(".json")[0] # splitting ./shlok-distance.json to get distance
			print(eid,req)
			#student_rec.append(eid)
			student_rec.append(req)
#			print(student_rec)
			student_dict[eid] = student_rec
		except:
			print(f'{file} is not proper JSON')

print(student_dict)
