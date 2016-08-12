#!/usr/bin/env python3

import bioblend
import logging
import os
import sys

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('search')

def find_SLX_libraries(SLX_libraries_path='.'):
    # TODO: Think about how to make this more flexible => .loc?

    # TODO: Check the path
    list_SLX_libraries = [entry
                          for entry in os.listdir(SLX_libraries_path)
                          if os.path.isdir(os.path.abspath(os.path.join(SLX_libraries_path, entry)))]

    list_SLX_libraries_formatted = [(library_name,
                                    os.path.abspath(os.path.join(SLX_libraries_path, library_name)),
                                    True)
                                    for library_name in list_SLX_libraries]

    return list_SLX_libraries_formatted

def get_SLX_library_fastq_files(slx_library_path='.'):
    log.debug(slx_library_path)
    slx_fastq_library_path = os.path.join(slx_library_path, 'fastq')

    fa_gz_list_checker = ['fa', 'gz']
    def get_last_two_extensions(string):
        return string.split('.')[-2:]

    # TODO: Rework this with a loop
    list_SLX_library_fastq_files = [(entry, os.path.isfile(os.path.join(slx_library_path, entry)))
                                    for entry in os.listdir(slx_fastq_library_path)
                                    if os.path.isfile(os.path.join(slx_library_path, entry)) and
                                    get_last_two_extensions(entry).equals(fa_gz_list_checker)]

    list_SLX_library_fastq_files_formatted = [(entry.name, entry.path, True)
                                               for entry in list_SLX_library_fastq_files]
    return list_SLX_library_fastq_files_formatted