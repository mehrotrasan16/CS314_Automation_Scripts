#!/bin/bash

# Creates Repos
#Author: Sanket Mehrotra
#this script requires the running user to be a member of the organization, have owner permissions to create repos, and have ssh keys setup to allow git@github pushing instead of https.
#hub was used to make this work, you may need to install it: `sudo apt install hub`. Hub also requires ssh keys to be set up to allow creation of private repos

# These variables may change from semester to semester
ORG_NAME=csucs314f20

if [ $# -eq 0 ]
then
	echo "
		Utility: github repo creator
		Usage: ./create_repos.sh <team_list file>
		Function: Populates team repositories with the starter kit codebase. Base code repo should already exist. Name of the organization is specifed in the shell script. Team names are to be provided in a separate file, each on a new line.
		"
  exit 1
fi

# Read through the team list, populate each repo with codebase
while read team
do
	# Clone individual repo
  echo "Cloning $team's repository via ssh"
  git clone git@github.com:/$ORG_NAME/$team
  #~ git clone git@github.com:/csucs314f20/t00.git
  
   # If repo doesn't exist, create it
  if [ $? -ne 0 ]
  then
    echo "
    Repo $team does not exist, creating.
    "
    mkdir $team
	cd $team
	#If hub does not work
	curl -u mehrotrasan16 https://api.github.com/orgs/csucs314f20/repos -d '{"name":"$teami", , "private": true}'
	# if you have hub
	#~ git init
	#~ hub create $ORG_NAME/$team
	git remote set-url --push origin git@github.com:$ORG_NAME/$team 
	
	
done < "$1" # Note that this is where we pass the team list file
