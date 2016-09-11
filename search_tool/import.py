import argparse
import logging
import os

from bioblend import galaxy

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('search')

def main():
    parser = argparse.ArgumentParser()

    """
    --galaxy-url $galaxy_url
    --api_keys $api_keys
     --fastq_files_list $slx_library_fastq_file
    """
    parser.add_argument('--galaxy-url')

    parser.add_argument('--api_keys')

    parser.add_argument('--fastq_files_list')

    args = parser.parse_args()

    galaxy_url = args.galaxy_url
    api_keys = args.api_keys
    fastq_files_list_not_reconstructed = args.fastq_files_list

    # Recontruction of the list separated by ','
    fastq_files_list = fastq_files_list_not_reconstructed.split(',')

    # Creation of the Galaxy Bioblend object
    gi = galaxy.GalaxyInstance(url=galaxy_url, key=api_keys)

    # We want, by default, to import in the history of the user
    current_history_id = gi.histories.get_current_history()['id']

    # Check if the files already exist in Data Library
    #  - If yes, import from therer
    #  - If no, import from local path + add the folder to the data library (use the kickstart)

    # As, for now, all the files can be selected from only the same folder,
    # we just need to check the location of the first file

    #TODO: Refactor with kickstart search
    # Get the first file name
    first_fastq_file_name = os.path.basename(fastq_files_list[0])

    libs = gi.libraries.get_libraries()
    libs_not_deleted = [lib
                        for lib in libs
                        if lib['deleted'] is False]

    lib_content_found = None
    for lib in libs_not_deleted:
        lib_content = gi.libraries.show_library(lib['id'], contents=True)
        for file in lib_content:
            if file['name'].replace('/', '') == first_fastq_file_name:
                if lib_content_found is not None:
                    log.warning("The file has been found in multiple locations...")
                lib_content_found = lib_content
                log.info("We found the file in the data library!")

    if lib_content_found is None:
        # TODO: Refactor in a function
        # Add each file in the current history of the user (more precisely in the API Key user history
        for fastq_file_path in fastq_files_list:
            # Remove the end '/'
            fastq_file_path = os.path.normpath(fastq_file_path)
            gi.tools.upload_file(fastq_file_path, current_history_id)

            log.info("- Added {0}".format(fastq_file_path.split('/')[-1]))
    else:
        # Add the requested files from the Data Library folder found into the user history
        for fastq_file_path in fastq_files_list:
            # Get the basename
            fastq_file_path_name = os.path.basename(fastq_file_path)
            # TODO: To avoid a O(n*m) time complexity, with n == len(fastq_files_list) and m == len(lib_found), sort the two lists/dict, and make only a O(m)
            for file in lib_content_found:
                file_name = file['name'].replace('/', '')
                if fastq_file_path_name == file_name:
                    gi.histories.upload_dataset_from_library(current_history_id, file['id'])
                    log.info("- Added {0} from library {1}".format(fastq_file_path_name, lib_content_found[0]['id']))
                    break

    log.info("Job done!")


if __name__ == "__main__":
    main()
