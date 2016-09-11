import argparse
from bioblend import galaxy
import os
import sys

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

   # Add each file in the current history of the user (more precisely in the API Key user history
   for fastq_file_path in fastq_files_list:
      # Remove the end '/'
      fastq_file_path = os.path.normpath(fastq_file_path)
      gi.tools.upload_file(fastq_file_path, current_history_id)

      print("- Added {0}".format(fastq_file_path.split('/')[-1]))

   print("Job done!")


if __name__ == "__main__":
   main()