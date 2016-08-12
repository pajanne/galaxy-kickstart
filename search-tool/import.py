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

   print("Galaxy URL: {0}".format(galaxy_url))
   print("API Keys: {0}".format(api_keys))
   print("Fastq files before reconstruction: {0}".format(fastq_files_list_not_reconstructed))

   fastq_files_list = fastq_files_list_not_reconstructed.split(',')

   print("Fastq files after reconstruction: {0}".format(fastq_files_list))

   """
   URL: http://127.0.0.1:8080/
   API_KEY: 5e8cc5748922c598c1aa6ec9e605780f
   """

   gi = galaxy.GalaxyInstance(url=galaxy_url, key=api_keys)

   current_history_id = gi.histories.get_current_history()['id']

   for fastq_file_path in fastq_files_list:
      # Remove the end '/'
      sys.stderr.write(fastq_file_path)
      fastq_file_path = os.path.normpath(fastq_file_path)
      gi.tools.upload_file(fastq_file_path, current_history_id)

      print("- Added {0}".format(fastq_file_path.split('/')[-1]))

   print("Job done!")


if __name__ == "__main__":
   main()