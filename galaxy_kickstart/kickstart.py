import argparse
import configparser
import glob


def main():
    # command line options
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", dest="config", action="store", help="The configuration file.", required=True)
    parser.add_argument("--library", dest="library_id", action="store", help="The SLX id of the library to fetch.", required=True)
    parser.add_argument("--output", dest="output", action="store", help="Output log file.", required=True)
    options = parser.parse_args()

    # read config from ini file
    config = configparser.ConfigParser()
    config.read(options.config)
    data_config = config['Data']

    # search sequencing files on disk in library root folder
    sequencing_files = glob.glob("%s/*/fastq/%s*.fq.gz" % (data_config['library_root'], options.library_id))
    with open(options.output, 'w') as out:
        out.write("Library root: %s\n" % data_config['library_root'])
        out.write("Library ID: %s\n" % options.library_id)
        out.write("Sequencing FASTQ files found: %s" % sequencing_files)


if __name__ == "__main__":
    main()
