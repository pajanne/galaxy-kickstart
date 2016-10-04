import argparse
import configparser
from bioblend.galaxy import GalaxyInstance
import glob
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


def main():
    # command line options
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", dest="library_id", action="store", help="The SLX id of the library to fetch.", required=True)
    options = parser.parse_args()

    # read config from ini file
    config = configparser.ConfigParser()
    config.read('config.ini')
    galaxy_config = config['Galaxy']
    data_config = config['Data']

    # create bioblend galaxy instance
    gi = GalaxyInstance(url=galaxy_config['url'], key=galaxy_config['api-key'])

    # fetch sequencing library in galaxy, create it if it does not exist
    galaxy_libraries = gi.libraries.get_libraries(name=data_config['galaxy_library_root'])
    # ignore deleted libraries
    active_galaxy_libraries = [lib for lib in galaxy_libraries if lib['deleted'] is False]
    if len(active_galaxy_libraries) == 0:
        sequencing_galaxy_library = gi.libraries.create_library(name=data_config['galaxy_library_root'])
    else:
        sequencing_galaxy_library = active_galaxy_libraries[0]
    log.debug(sequencing_galaxy_library)

    # fetch contents of sequencing library in galaxy
    sequencing_galaxy_library_contents = gi.libraries.show_library(library_id=sequencing_galaxy_library['id'], contents=True)
    log.debug('>>> gi.libraries.show_library: %s' % sequencing_galaxy_library_contents)

    # search sequencing files on disk in library root folder
    # import them into galaxy data libraries if they do not already exist
    # and upload them into user's history
    sequencing_files = glob.glob("%s/*/fastq/%s*.fq.gz" % (data_config['library_root'], options.library_id))
    log.debug(sequencing_files)
    for f in sequencing_files:
        # extract fastq filename and run folder
        path, fastq_filename = os.path.split(f)
        path, fastq_dir = os.path.split(path)
        if fastq_dir == 'fastq':
            path, run_folder = os.path.split(path)
        else:
            run_folder = fastq_dir
        log.debug(run_folder)
        log.debug(fastq_filename)

        # find folder in galaxy data library if not create it
        run_folder_in_galaxy = get_galaxy_item(sequencing_galaxy_library_contents, 'folder', run_folder)
        if not run_folder_in_galaxy:
            # create folder in galaxy
            run_folder_in_galaxy = gi.libraries.create_folder(library_id=sequencing_galaxy_library['id'], folder_name=run_folder)[0]
            # retrieve library contents
            sequencing_galaxy_library_contents = gi.libraries.show_library(library_id=sequencing_galaxy_library['id'], contents=True)
            log.debug('>>> gi.libraries.show_library: %s' % sequencing_galaxy_library_contents)
        log.debug('>>> run_folder_in_galaxy: %s' % run_folder_in_galaxy)

        # find file in galaxy data library if not upload it
        fastq_filename_in_galaxy = get_galaxy_item(sequencing_galaxy_library_contents, 'file', fastq_filename)
        if not fastq_filename_in_galaxy:
            # upload file
            fastq_filename_in_galaxy = gi.libraries.upload_from_galaxy_filesystem(
                library_id=sequencing_galaxy_library['id'],
                filesystem_paths=f,
                folder_id=run_folder_in_galaxy['id'],
                #file_type='fastqsanger',
                link_data_only='link_to_files')[0]
            # retrieve library contents
            sequencing_galaxy_library_contents = gi.libraries.show_library(library_id=sequencing_galaxy_library['id'], contents=True)
            log.debug('>>> gi.libraries.show_library: %s' % sequencing_galaxy_library_contents)
        log.debug('>>> fastq_filename_in_galaxy: %s' % fastq_filename_in_galaxy)

if __name__ == "__main__":
    main()
