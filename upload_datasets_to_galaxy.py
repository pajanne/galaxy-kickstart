#!/usr/bin/python3
import argparse
import configparser
from bioblend.galaxy import GalaxyInstance

def upload_datasets_to_galaxy():
    # Arguments initialization
    parser = argparse.ArgumentParser(description="Script to upload a folder into"
                                                 "Galaxy Data Libraries")

    parser.add_argument('--folder', help='Folder to add in Data Libraries of Galaxy')

    args = parser.parse_args()

    # Fetch arguments
    folder_path = args.folder

    # Launch config
    config = configparser.ConfigParser()
    config.read('config.ini')

    #galaxy_config = config['Galaxy']
    print(config.get('Galaxy', 'url'))

    gi = GalaxyInstance(url="%s" % config.get('Galaxy', 'url'), key=config.get('Galaxy', 'api-key'))

    print(gi.histories.get_histories())


if __name__ == "__main__":
    upload_datasets_to_galaxy()
