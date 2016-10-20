import argparse
import configparser
import glob
from bioblend.galaxy import GalaxyInstance
import os

# logging
import logging
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
log = logging.getLogger('kickstart')


def get_galaxy_item(galaxy_library_contents, item_type, item_name):
    # remove file extension to match on name only as galaxy store file names without .gz sometimes
    if item_type == 'file':
        item_name = item_name[:-6]
    for item in galaxy_library_contents:
        if item['type'] == item_type and item_name in item['name']:
            log.debug('get_galaxy_item: item SEARCH %s, %s' % (item_type, item_name))
            log.debug('get_galaxy_item: item FOUND %s' % item)
            return item


def upload_files(data_config, options, gi, user_gi, galaxy_library, file_config):
    # user current history
    user_current_history_id = user_gi.histories.get_current_history()['id']

    # fetch contents of sequencing library in galaxy
    galaxy_library_contents = gi.libraries.show_library(library_id=galaxy_library['id'], contents=True)
    log.debug('>>> gi.libraries.show_library: %s' % galaxy_library_contents)

    # search sequencing files on disk in library root folder
    # import them into galaxy data libraries if they do not already exist
    # and upload them into user's history
    sequencing_files = glob.glob("%s/*/%s/%s*.%s" % (data_config['library_root'], file_config['subfolder'], options.library_id, file_config['extension']))

    log.debug(sequencing_files)
    tool_message = "Sequencing files *.%s found:\n" % file_config['extension']
    if not sequencing_files:
        tool_message += "\tNone\n"
    for i, f in enumerate(sequencing_files, start=1):
        # extract filename and run folder
        path, seq_filename = os.path.split(f)
        path, file_dir = os.path.split(path)
        if file_dir == file_config['subfolder']:
            path, run_folder = os.path.split(path)
        else:
            run_folder = file_dir

        tool_message += "\t%s\t%s\n" % (i, seq_filename)

        # find folder in galaxy data library if not create it
        run_folder_in_galaxy = get_galaxy_item(galaxy_library_contents, 'folder', run_folder)
        if not run_folder_in_galaxy:
            # create folder in galaxy
            run_folder_in_galaxy = gi.libraries.create_folder(library_id=galaxy_library['id'], folder_name=run_folder)[0]
            # retrieve new library contents
            galaxy_library_contents = gi.libraries.show_library(library_id=galaxy_library['id'], contents=True)

        # find file in galaxy data library if not upload it
        seq_file_in_galaxy = get_galaxy_item(galaxy_library_contents, 'file', seq_filename)
        if not seq_file_in_galaxy:
            # upload file
            seq_file_in_galaxy = gi.libraries.upload_from_galaxy_filesystem(
                library_id=galaxy_library['id'],
                filesystem_paths=f,
                folder_id=run_folder_in_galaxy['id'],
                file_type=file_config['galaxy_type'],
                link_data_only='link_to_files')[0]
            tool_message += "\t\t>>> uploaded into data library %s\n" % (data_config['galaxy_library_root'])
            # retrieve new library contents
            galaxy_library_contents = gi.libraries.show_library(library_id=galaxy_library['id'], contents=True)

        # upload file in user's current history from data library
        user_gi.histories.upload_dataset_from_library(user_current_history_id, seq_file_in_galaxy['id'])
        tool_message += '\t\t+++ added into current history\n'

    return tool_message


def main():
    # command line options
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", dest="config", action="store", help="The configuration file.", required=True)
    parser.add_argument("--userapikey", dest="user_api_key", action="store", help="The current user api key.", required=True)
    parser.add_argument("--library", dest="library_id", action="store", help="The SLX id of the library to fetch.", required=True)
    parser.add_argument("--filetypes", dest="file_types", action="store", help="The type of files to upload.", required=True)
    parser.add_argument("--output", dest="output", action="store", help="Output log file.", required=True)
    options = parser.parse_args()

    # read config from ini file
    config = configparser.ConfigParser()
    config.read(options.config)
    galaxy_config = config['Galaxy']
    data_config = config['Data']

    # create bioblend galaxy instance for admin
    gi = GalaxyInstance(url=galaxy_config['url'], key=galaxy_config['api-key'])

    # create bioblend galaxy instance for current user
    user_gi = GalaxyInstance(url=galaxy_config['url'], key=options.user_api_key)

    # fetch sequencing library in galaxy, create it if it does not exist
    galaxy_libraries = gi.libraries.get_libraries(name=data_config['galaxy_library_root'])
    # ignore deleted libraries
    active_galaxy_libraries = [lib for lib in galaxy_libraries if lib['deleted'] is False]
    if len(active_galaxy_libraries) == 0:
        sequencing_galaxy_library = gi.libraries.create_library(name=data_config['galaxy_library_root'])
    else:
        sequencing_galaxy_library = active_galaxy_libraries[0]
    log.debug(sequencing_galaxy_library)

    log.debug(">>> File types: %s" % options.file_types)

    tool_message  = "--------------------------------------------------------------------------------\n"
    tool_message += "--- Upload Sequencing files ----------------------------------------------------\n"
    tool_message += "--------------------------------------------------------------------------------\n"
    tool_message += "Library root: %s\n" % data_config['library_root']
    tool_message += "User API key: %s\n" % options.user_api_key
    tool_message += "Library ID: %s\n" % options.library_id
    tool_message += "--------------------------------------------------------------------------------\n"
    tool_message += upload_files(data_config, options, gi, user_gi, sequencing_galaxy_library, config['contents'])
    if 'fastq' in options.file_types:
        tool_message += upload_files(data_config, options, gi, user_gi, sequencing_galaxy_library, config['fastq'])
    if 'bam' in options.file_types:
        tool_message += upload_files(data_config, options, gi, user_gi, sequencing_galaxy_library, config['bam'])
    tool_message += "--------------------------------------------------------------------------------\n"

    # write output message into file
    with open(options.output, 'w') as out:
        out.write(tool_message)


if __name__ == "__main__":
    main()
