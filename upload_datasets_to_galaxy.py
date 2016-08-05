#!/usr/bin/python3
import argparse
# from bioblend.galaxy import GalaxyInstance
import configparser

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

    galaxy_config = config['Galaxy']

    # gi = GalaxyInstance(url=galaxy_config['url'], key=galaxy_config['api-key'])

    # print(gi.histories.get_histories())


if __name__ == "__main__":
    upload_datasets_to_galaxy()