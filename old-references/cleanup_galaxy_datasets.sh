#!/bin/bash
cd ~/galaxy
# delete userless histories and datasets
python scripts/cleanup_datasets/cleanup_datasets.py universe_wsgi.ini -d 60 -1
# purge deleted histories
python scripts/cleanup_datasets/cleanup_datasets.py universe_wsgi.ini -d 60 -2 -r
# purge deleted datasets
python scripts/cleanup_datasets/cleanup_datasets.py universe_wsgi.ini -d 60 -3 -r
# purge deleted libraries
python scripts/cleanup_datasets/cleanup_datasets.py universe_wsgi.ini -d 60 -4 -r
# purge deleted library folders
python scripts/cleanup_datasets/cleanup_datasets.py universe_wsgi.ini -d 60 -5 -r
# mark deletable datasets as deleted and purge associated dataset instances
python scripts/cleanup_datasets/cleanup_datasets.py universe_wsgi.ini -d 60 -6 -r