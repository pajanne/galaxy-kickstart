#!/usr/bin/python3
import argparse
from bioblend.galaxy import GalaxyInstance
import configparser
import os

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

    gi = GalaxyInstance(url='http://127.0.0.1:8080', key='5e8cc5748922c598c1aa6ec9e605780f')

    name_folder_test = '160802_D00281L_0127_C9NPBANXX'
    path_folder_test = './test-data/staging/' + name_folder_test
    path_to_fastq_folder_test = os.path.join(path_folder_test, 'fastq')

    # TODO: Make a loop which execute the following, for each directory found
    libs_folder = gi.libraries.get_libraries(name=name_folder_test)
    # TODO: Check the library does already exist
    # Create the library with the name equal to the folder name
    # and description 'Library' + folder_name
    dict_library_test = gi.libraries.create_library(name_folder_test,
                                                    description=' '.join(['Library', name_folder_test]),
                                                    synopsis=None)

    # Upload the data in the library just created
    list_of_files = '\n'.join(os.listdir(path_to_fastq_folder_test))
    unknow_return = gi.libraries.upload_from_galaxy_filesystem(
            library_id=dict_library_test.get('id'),
            filesystem_paths=list_of_files,
            file_type='auto',
            link_data_only='link_to_files',
            )
    print(unknow_return)
    # TODO: Check if no new files, else upload them
    # print("Already there! Skipping {0}".format(name_folder_test))

    #print(gi.histories.get_histories())


if __name__ == "__main__":
    upload_datasets_to_galaxy()