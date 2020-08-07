#!/bin/bash

#Clones certain directories from one organization repo to another. Both repos should already exist. Name of the organizations and the folders to clone are specifed in the shell script.

#TODO: extend using ssh so that you don't have to put in your username and password in everytime
#hub was used to make this work, you may need to install it: `sudo apt install hub`


#Organizations Should ALREADY EXIST!
ORG_NAME=csucs314s20
NEW_ORG_NAME=csucs314f20

repos="devops grading guide product" # devops base guide product


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
  echo "
  Cloning $i 
  from https://github.com/$ORG_NAME/$repo.git to local storage, please wait.
  "
  
  git clone --mirror git@github.com:$ORG_NAME/$repo.git
  
  # If repo doesn't exist, die
  if [ $? -ne 0 ]
  then
    echo "Failed to clone repository $repo. Does it exist?"
    exit 1
  fi
  
  cd $repo.git
  
  hub create -p $NEW_ORG_NAME/$repo
  
  if [ $? -ne 0 ]
  then
    echo "\n\nFailed to create repository $repo on $NEW_ORG_NAME. is the name valid??"
    exit 1
  fi
  
  git remote set-url --push origin git@github.com:$NEW_ORG_NAME/$repo.git 
  git push git@github.com:$NEW_ORG_NAME/$repo.git 
  cd ..
done
echo "Cloned specified repos from old organization $ORG_NAME repo to local folder at $(pwd) and pushed to new organization $NEW_ORG_NAME repo sucessfully."

