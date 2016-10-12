import glob
import configparser

# logging
import logging
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
log = logging.getLogger('kickstart')


def find_sequencing_files(library_id, config_file):
    # read config from ini file
    config = configparser.ConfigParser()
    config.read(config_file)
    data_config = config['Data']
    log.debug(library_id)
    sequencing_files = glob.glob("%s/*/fastq/%s*.fq.gz" % (data_config['library_root'], library_id))
    log.debug(sequencing_files)
    return sequencing_files
