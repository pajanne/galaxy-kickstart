# Galaxy kickstart
Upload sequencing data into Galaxy

## Objectives

- write a script that upload staging FASTQ and BAM files into Galaxy data libraries using BioBlend API https://github.com/galaxyproject/bioblend
- write a tool that search for FASTQ/BAM files of certain projects or library identifiers (SLX-IDs) and import them into Galaxy
- run a simple RNA-Seq workflow on the data imported in Galaxy using the in-house cluster

## How to run this feature

1. Galaxy requires Python 2.7, to check your python version, run:

    ```Bash
    $ python -V
    Python 2.7.3
    ```
    Install Galaxy release_16.04:

    ```Bash
    $ sh get-galaxy.sh
    ```

    Start Galaxy:

    ```Bash
    $ sh run.sh --daemon
    ```

    Once Galaxy completes startup, you should be able to view Galaxy in your browser at:

    http://localhost:8080

2. Configure Galaxy for Data Libraries

    The desired directory for this option must be specified in the Galaxy configuration file `config/galaxy.ini`, copy sample file from `config/galaxy.ini.sample`.

    ```
    # Directories of files contained in the following directory can be uploaded to a library from the Admin view
    library_import_dir = /some_local_directory_of_files
    ```

    Use `library_import_dir = path-to-local-galaxy-kickstart-repo/test-data/`

    The setting for `library_import_dir` should be a directory that contains files or other directories, the contents of which can be selected for upload to the Data Library.

    :warning: Copying datasets or not - Galaxy admin interface
    > If a checkbox labeled "Copy data into Galaxy?" is checked, it will prevent Galaxy from copying data to its files directory. This is useful for large library datasets that live in their own managed locations on the filesystem, and will prevent the existence of duplicate copies of datasets. However, using this feature requires administrators to take responsibility for managing these files - moving or removing the data from its Galaxy-external location will render these datasets invalid within Galaxy.

    > Also, when the "Copy data into Galaxy?" checkbox is checked, any symbolic links encountered in the chosen import directory will be made absolute and dereferenced once. This allows administrators to link large datasets to the import directory rather than having to make copies of the files, and these links can be deleted after importing. Only the first symlink (the one in the import directory itself) is dereferenced, all others remain.

  More informations about Uploading Data Libraries here: https://wiki.galaxyproject.org/Admin/DataLibraries/UploadingLibraryFiles

  Restart Galaxy:
  ```Bash
  $ sh run.sh --restart
  ```

3. Create admin user

  In the web interface, go to User > Register and create an `admin` account with an associated email address `admin@admin.org` that should be entered in the `config/galaxy.ini` as admin users.

  ```
  # Administrative users - set this to a comma-separated list of valid Galaxy
  # users (email addresses).  These users will have access to the Admin section
  # of the server, and will have access to create users, groups, roles,
  # libraries, and more.  For more information, see:
  #   https://wiki.galaxyproject.org/Admin/Interface
  admin_users = admin@admin.org
  ```

  Restart Galaxy:
  ```Bash
  $ sh run.sh
  ```


## Sequencing data location
Currently all sequencing data files are located on the galaxy server in `/staging` under folders of this kind `/staging/160802_D00281L_0127_C9NPBANXX/fastq/`.

The FASTQ filenames are of this format:
`SLX-11649.A002.C9NPBANXX.s_1.r_1.fq.gz`, and the content of this folder is in `SLX-11649.C9NPBANXX.s_1.contents.csv` describing the mapping between barcode names and original sample names:

```
"Pool","Barcode","Sequence","Sample name"
"SLX-11649","A002","CGATGT","MTMB0212"
"SLX-11649","A005","ACAGTG","MTMB0225"
"SLX-11649","A006","GCCAAT","MTMB0184"
"SLX-11649","A012","CTTGTA","MTMB0195"
"SLX-11649","A014","AGTTCC","MTMB0264"
"SLX-11649","A007","CAGATC","MTMB0234"
"SLX-11649","A013","AGTCAA","MTMB0251"
"SLX-11649","A004","TGACCA","MTMB0046"
```

BAM files if present are located in an `../alignment/` directory e.g. in `/staging/160803_K00252_0047_HFNCKBBXX/alignment/`. The filenames are of this format:
`SLX-11654.D707_D501.HFNCKBBXX.s_5.bwa.homo_sapiens.bam` and alignment metrics stored in
`SLX-11654.D707_D501.HFNCKBBXX.s_5.bwa.homo_sapiens.alignment_metrics.txt`

```
## htsjdk.samtools.metrics.StringHeader
# picard.analysis.CollectAlignmentSummaryMetrics INPUT=/lustre/mib-cri/solexa/Runs/160803_K00252_0047_HFNCKBBXX/alignment/SLX-11654.D707_D501.HFNCKBBXX.s_5.bwa.homo_sapiens.bam OUTPUT=/lustre/mib-cri/solexa/Runs/160803_K00252_0047_HFNCKBBXX/alignment/SLX-11654.D707_D501.HFNCKBBXX.s_5.bwa.homo_sapiens.alignment_metrics.txt.pipetemp REFERENCE_SEQUENCE=/lustre/reference_data/mib-cri/reference_genomes/homo_sapiens/hs37d5/fasta/hsa.hs37d5.fa TMP_DIR=[/lustre/mib-cri/solexa/Runs/160803_K00252_0047_HFNCKBBXX/alignment/temp] VALIDATION_STRINGENCY=SILENT    MAX_INSERT_SIZE=100000 ADAPTER_SEQUENCE=[AATGATACGGCGACCACCGAGATCTACACTCTTTCCCTACACGACGCTCTTCCGATCT, AGATCGGAAGAGCTCGTATGCCGTCTTCTGCTTG, AATGATACGGCGACCACCGAGATCTACACTCTTTCCCTACACGACGCTCTTCCGATCT, AGATCGGAAGAGCGGTTCAGCAGGAATGCCGAGACCGATCTCGTATGCCGTCTTCTGCTTG, AATGATACGGCGACCACCGAGATCTACACTCTTTCCCTACACGACGCTCTTCCGATCT, AGATCGGAAGAGCACACGTCTGAACTCCAGTCACNNNNNNNNATCTCGTATGCCGTCTTCTGCTTG] METRIC_ACCUMULATION_LEVEL=[ALL_READS] IS_BISULFITE_SEQUENCED=false ASSUME_SORTED=true STOP_AFTER=0 VERBOSITY=INFO QUIET=false COMPRESSION_LEVEL=5 MAX_RECORDS_IN_RAM=500000 CREATE_INDEX=false CREATE_MD5_FILE=false
## htsjdk.samtools.metrics.StringHeader
# Started on: Thu Aug 04 11:07:05 BST 2016

## METRICS CLASS	picard.analysis.AlignmentSummaryMetrics
CATEGORY	TOTAL_READS	PF_READS	PCT_PF_READS	PF_NOISE_READS	PF_READS_ALIGNED	PCT_PF_READS_ALIGNED	PF_ALIGNED_BASES	PF_HQ_ALIGNED_READS	PF_HQ_ALIGNED_BASES	PF_HQ_ALIGNED_Q20_BASES	PF_HQ_MEDIAN_MISMATCHES	PF_MISMATCH_RATE	PF_HQ_ERROR_RATE	PF_INDEL_RATE	MEAN_READ_LENGTH	READS_ALIGNED_IN_PAIRS	PCT_READS_ALIGNED_IN_PAIRS	BAD_CYCLES	STRAND_BALANCE	PCT_CHIMERAS	PCT_ADAPTER	SAMPLE	LIBRARY	READ_GROUP
UNPAIRED	16997058	16997058	1	0	0	0	0	0	0	0	0	0	0	0	50	0	0	0	0	0	0.01539			
```

## Existing projects to get inspiration from...

- bcbio-nextgen - Validated, scalable, community developed variant calling, RNA-seq and small RNA analysis https://github.com/chapmanb/bcbio-nextgen

- internal CRUKCI kickstart command line tool

- ...
