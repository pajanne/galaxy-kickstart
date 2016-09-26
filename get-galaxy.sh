#!/bin/bash

GALAXY_HOME=galaxy-dist

# check python version
case "$(python --version 2>&1)" in
    *" 2.7"*)
        echo "Fine! Python 2.7 installed."
        ;;
    *)
        echo "Wrong Python version! Galaxy requires Python 2.7."
        exit 1
        ;;
esac

# check git installed
hash git 2>/dev/null && echo "Fine! Git installed." || { echo >&2 "Git not installed. Aborting."; exit 1; }

# clone Galaxy repo
rm -rf $GALAXY_HOME
git clone https://github.com/galaxyproject/galaxy.git $GALAXY_HOME
cd $GALAXY_HOME
git checkout -b release_16.04 origin/release_16.04
