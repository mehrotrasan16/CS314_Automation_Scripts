#!/bin/bash

#Clones certain directories from one organization repo to another. Both repos should already exist. Name of the organizations and the folders to clone are specifed in the shell script.

#TODO: using hub or gh command line tools to extend this or to make it cleaner. will have to install them from their sites tho: https://hub.github.com/ and https://cli.github.com/
#TODO: extend using ssh so that you don't have to put in your username and password in everytime


#Should ALREADY EXIST!
ORG_NAME=csucs314s20
NEW_ORG_NAME=csucs314f20

GIT_USERNAME=mehrotrasan16

folders=("devops")

repos="devops" #base guide grading product


if [ $# -gt 0 ]
then
	if [ $1 == "-h" -o  $1 == "--help" ]
	then
		echo "
		Utility: git organization clone
		Usage : ./git_org_clone.sh
		Function: Clones certain directories from one organization repo to another. Both repos should already exist. Name of the organizations and the folders to clone are specifed in the shell script.
		"
	fi
fi

mkdir $ORG_NAME
cd $ORG_NAME

# Read through the folder list, get each repo and copy it to 
for repo in $repos
do
  echo "Cloning $i from https://github.com/$ORG_NAME/$repo.git to local storage, please wait."
  git clone https://github.com/$ORG_NAME/$repo.git
  
  # If repo doesn't exist, die
  if [ $? -ne 0 ]
  then
    echo "Failed to clone repository $repo. Does it exist?"
    exit 1
  fi
done
echo "Cloned specified repos from old organization repo to local folder at $(pwd) sucessfully."

cd ..
mkdir $NEW_ORG_NAME
cd $NEW_ORG_NAME

for repo in $repos
do
  echo "Creating project repo in new organization repository : https://github.com/$NEW_ORG_NAME/$repo.git on remote, please wait."
  repo_name=$repo
  #curl -u $GIT_USERNAME -X POST -H "Accept: application/vnd.github.v3+json" https://api.github.com/orgs/$NEW_ORG_NAME/repos -d '{"name":"$repo","private":true}' 
  rsync -rv --exclude=.git ../$ORG_NAME/$repo ./ 
  cd ./$repo
  git init
  git add .
  git commit -m "$i Repo cloned from $ORG_NAME"
  git push 
  cd ..
done

