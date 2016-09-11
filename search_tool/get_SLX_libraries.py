import bioblend
import logging
import os
import sys

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('search')

def find_SLX_libraries(SLX_libraries_path='.'):
    # TODO: Think about how to make this more flexible => .loc?

    # TODO: Check the path
    list_SLX_libraries_formatted = []
    if SLX_libraries_path is None:
        return list_SLX_libraries_formatted

    list_SLX_libraries = [entry
                          for entry in os.listdir(SLX_libraries_path)
                          if os.path.isdir(os.path.abspath(os.path.join(SLX_libraries_path, entry)))]

    list_SLX_libraries_formatted = [(library_name,
                                    os.path.abspath(os.path.join(SLX_libraries_path, library_name)),
                                    True)
                                    for library_name in list_SLX_libraries]
    log.debug("Result data in find_SLX_libraries from {0}: {1}".format(SLX_libraries_path, list_SLX_libraries_formatted))
    return list_SLX_libraries_formatted

def get_SLX_library_fastq_files(SLX_library_path='.'):
    list_SLX_library_fastq_files = []

    log.debug("Parameter in get_SLX_library_fastq_files: {0}".format(SLX_library_path))
    if SLX_library_path is None:
        return list_SLX_library_fastq_files

    slx_fastq_library_path = os.path.join(SLX_library_path, 'fastq')

    fa_gz_list_checker = ['fq', 'gz']
    def get_last_two_extensions(string):
        return string.split('.')[-2:]

    for entry in os.listdir(slx_fastq_library_path):
        full_entry_path = os.path.join(slx_fastq_library_path, entry)
        if os.path.isfile(full_entry_path):
            # TODO: This is ugly...need to change that asap
            two_exts = get_last_two_extensions(entry)
            if two_exts == fa_gz_list_checker:
                list_SLX_library_fastq_files.append((entry, full_entry_path, True))

    log.debug("Result in get_SLX_library_fastq_files: {0}".format(list_SLX_library_fastq_files))
    return list_SLX_library_fastq_files