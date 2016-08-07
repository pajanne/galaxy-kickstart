#!/usr/bin/env/python3

import argparse
import configparser

from bioblend.galaxy import GalaxyInstance

from utils.delete import delete_all_libraries
from utils.upload import upload_datasets_to_galaxy


def main():
    # Launch config
    config = configparser.ConfigParser()

    config.read('config.ini')

    galaxy_config = config['Galaxy']

    # Create GalaxyInstance object
    gi = GalaxyInstance(url=galaxy_config['url'], key=galaxy_config['api-key'])

    # Arguments initialization
    # Parser for the whole software
    parser = argparse.ArgumentParser(description='Program to manage your sequencing '
                                             'data in Galaxy Data Libraries',
                                     add_help=True)

    subparsers = parser.add_subparsers(help='Sub commands')
    """:type : argparse.Action"""

    # For uploading
    parser_upload = subparsers.add_parser('upload',
                                          help='Upload your sequencing data to Galaxy')

    parser_upload.add_argument('--libraries-root',
                               required=True,
                               help="Path to the folder containing "
                                    "the folders to upload as data libraries")
    parser_upload.set_defaults(func=upload_datasets_to_galaxy)

    # For deleting / cleaning
    parser_delete = subparsers.add_parser('delete', help='Delete data libraries from Galaxy')
    """:type : argparse.ArgumentParser"""

    parser_delete.set_defaults(func=delete_all_libraries)

    args = parser.parse_args()

    args.func(args, galaxy_instance=gi)

if __name__ == "__main__":
    main()