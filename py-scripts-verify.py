import json
import os
import glob
os.chdir('/media/sanketm/Data/Temp/CS314/csucs314fa20-repo/students/tests/sprint2') # path to the students repo

all_jsons = glob.glob('./**.json') # get list of all json files

student_dict = {}                                                     

for file in all_jsons: 
	with open(file,'r') as f: 
	 try: 
		 json.load(f) 
		 eid = file.split("-")[0].split("./")[1] # splitting ./shlok-distance.json to get shlok
		 req = file.split("-")[1].split(".")[0] # splitting ./shlok-distance.json to get distance
		 
		 student_rec = student_dict.get(eid,{})
		 print(student_rec)
		 if student_rec == {}:
			 student_rec = {}
			 if req == 'find':
				 student_rec['find'] = 1
			 elif req == 'distance':
				 student_rec['distance'] = 1
			 student_dict[eid] = student_rec
		 else:
			 if req == 'find':
				 student_rec['find'] = 1
			 elif req == 'distance':
				 student_rec['distance'] = 1
			 student_dict[eid] = student_rec
		 print(f"{file} is valid json ") 
	 except: 
		 print(f"{file} is invalid ")

print(student_dict)

with open('eid_sprint2_tests.csv', 'w') as f:
    for key in student_dict.keys():
        f.write("%s,%s\n"%(key,student_dict[key]))
