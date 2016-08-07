#!/usr/bin/env/python3

import os
import sys
from urllib.parse import urljoin


def upload_datasets_to_galaxy(args, galaxy_instance=None):
    """
    Function to upload a folder into Galaxy Data Libraries
    :param galaxy_instance:
    :return:
    """

    # Get all parameters

    libraries_root = args.libraries_root

    gi = galaxy_instance

    """:type : bioblend.galaxy.GalaxyInstance"""

    # Get all folders to add or update
    # TODO: Use full path
    sequence_folders = [entry
                        for entry in os.scandir(libraries_root)
                        if entry.is_dir()]

    # Fetch all, not deleted, libraries
    libs = gi.libraries.get_libraries()
    libs_not_deleted = [lib
                        for lib in libs
                        if lib['deleted'] is False]
    # Check the libs
    for sequence_folder in sequence_folders:
        # If not already exists in Galaxy Data Library, we create it
        # Else we update
        # TODO: Inefficient to go through the libs_not_deleted for each sequence_folder
        s_name = sequence_folder.name
        if s_name not in [lib['name'] for lib in libs_not_deleted]:
            # Creation of the folder
            print("{0} does not exist yet.".format(s_name))

            print("Creating {0} now...".format(s_name))
            dict_new_library = gi.libraries.create_library(s_name,
                                                            description=' '.join(['Library', s_name]),
                                                            synopsis=None)
            print("{0} created.".format(dict_new_library['description']))

            # Symlink the files
            print("Adding files now in Galaxy Data Library {0}:".format(s_name))

            ## Get the path the fastq
            fastq_folder_rel_path = os.path.join(libraries_root, s_name, 'fastq')
            fastq_folder_abs_path = os.path.abspath(fastq_folder_rel_path)

            str_fastqs_filesystem = ''

            entries_in_fastq_folder = os.scandir(fastq_folder_abs_path)
            for index, file in enumerate(entries_in_fastq_folder):
                # If file matches, we store the full path in a str, line separated
                # Else, we warn and do nothing more
                if file.is_file() and file.name.split('.')[-2:] == ['fq', 'gz']:
                    full_file_path = os.path.abspath(file.path)
                    str_fastqs_filesystem = ''.join([str_fastqs_filesystem, full_file_path, '\n'])
                    print("ADDED: {0} is a compressed fastq".format(file.name))
                else:
                    # TODO: Store the filtered files in a log
                    if index < 15:
                        print("SKIPPED: {0} is not a compressed fastq".format(file.name))
                    elif index == 16:
                        print("Too much verbosity, the printing of the skipped files is not continuing")
            # We now upload them to Galaxy
            print('')
            print('We are now uploading the "ADDED" files to the Galaxy Data Library: {0}'.format(s_name))
            # TODO: Handle errors all around the code, need to discuss with Anne about that
            dict_info_uploaded_files = gi.libraries.upload_from_galaxy_filesystem(
                    library_id=dict_new_library['id'],
                    filesystem_paths=str_fastqs_filesystem,
                    link_data_only='link_to_files')
            print('Upload successfully finished into {0}'.format(s_name))

            partial_url_api_to_contents = dict_info_uploaded_files[-1]['url']
            url_to_json = urljoin(gi.base_url, partial_url_api_to_contents)
            print('Here is the url of the result JSON to have the actual content of the library: {0}'.\
                format(url_to_json))
            print('')
        else:
            print("{0} already exists! Updating coming soon".format(sequence_folder.name))

    print("All done,")
    print("Bye!")

    # TODO: Check the library does already exist
    # Create the library with the name equal to the folder name
    # and description 'Library' + folder_name
    """

    # Upload the data in the library just created
    all_full_path_string = ''
    for file in os.listdir(path_to_fastq_folder_test):
        full_path_file = os.path.join(path_to_fastq_folder_test, file)
        all_full_path_string = '\n'.join([all_full_path_string, full_path_file])

    list_of_files = '\n'.join(os.path.join(os.listdir(path_to_fastq_folder_test)))
    unknow_return = gi.libraries.upload_from_galaxy_filesystem(
            library_id=dict_library_test.get('id'),
            filesystem_paths=list_of_files,
            file_type='auto',
            link_data_only='link_to_files',
            )

    print(unknow_return)
    # TODO: Check if no new files, else upload them
    # print("Already there! Skipping {0}".format(name_folder_test))
    """
    #print(gi.histories.get_histories())


if __name__ == "__main__":
    print("Please see the option to call this script from the main program. Quiting...")
    sys.exit(-1)
