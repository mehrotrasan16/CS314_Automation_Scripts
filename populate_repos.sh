#!/bin/bash

# Populates team repositories with the starter kit codebase

# These variables may change from semester to semester
ORG_NAME=csucs314f20

if [ $# -eq 0 ]
then
  echo "Usage: ./populate_repos.sh <team_list>"
  exit 1
fi

# Note that the codebase (base) should be in the same directory as this script at runtime
# Verify that directory exists
if [ ! -d "Base" ]
then
  echo "
  Base directory must be in the same directory as this script, Cloning locally!
  "
  git clone git@github.com:$ORG_NAME/base.git
fi

# Read through the team list, populate each repo with codebase
while read team
do

  # Copy ALL files from base into a working directory that's safe to sed in
  echo "
  Creating intermediate local directory from base
  "
  cp -r ./base ./working_base
  cd working_base

  # Rename directories with wrong team number
  # Check out "man find" for more info on this command
  find . -depth -type d -name t00 -execdir mv {} $team ";"

  # Replace t00s in repository
  # Need to specifically exclude this one file because Footer.js contains some "t00" string in
  # a base64-encoded image string
  grep --ignore-case -ls -r --exclude FooterLogo\.js t00 | xargs sed -i "s/\(t\|T\)00/$team/g"

  cd ..
  
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
		
	# Copy all files into team dir
	cp -r ./working_base/ $team
	
	# Append .gitignore to new file or existing file
	cat ./working_base/.gitignore >> ./$team/.gitignore
	
	# cd into new repo
	cd $team
	hub create $ORG_NAME/$team
	git remote set-url --push origin git@github.com:$ORG_NAME/$team 
	
	if [ $? -ne 0 ]
	then
		echo "Failed to create repository $repo on $NEW_ORG_NAME. is the name valid??"
		exit 1
	fi
	
	# Commit changes
	git add .
	git commit -m "Add initial code base"
	
	# Push changes
	git push origin master
	#git push git@github.com:$ORG_NAME/$team 
	
	# cd out of repo
	cd ..
  fi

  # (Optionally) Delete folders to clean up
  #rm -rf working_base
  # rm -rf $team

done < "$1" # Note that this is where we pass the team list file
