# CRUKCI command line kickstart

## Usage

Upload FASTQ and or BAM files from the command line based on project name and/or library name from information is stored in the LiMS database.

```
usage: java org.cruk.pipeline.kickstart.AnalysisPipelineKickstart <options>
    -a,--aligner <aligner>                     The aligner to use for
                                               realignment. Default is 'bwa'.
    -c,--combine-samples                       Whether to combine samples with
                                               the same name (see below).
    -C,--ignore-checksums                      Don't perform checksum checks on
                                               download.
    -D,--skip-download                         Don't download files, just manage
                                               the sample sheet.
    -d,--download-dir <directory>              The path of the download
                                               directory.
    -e,--extra-metrics                         Try to download extra metrics
                                               files with the main files.
    -f,--file-system-friendly                  Add columns to the sample sheet
                                               and file index for "friendly"
                                               versions of the sample name and
                                               source id.
    -F,--file-index <name>                     The name of the file index file.
                                               Default is 'filelist.csv'.
       --fastq-only                            Ignore alignment files and fetch
                                               FASTQ even when a BAM is
                                               available.
    -g,--genome <name>                         The short name of the genome to
                                               align to. Only the most common
                                               genomes are recognised.
    -h,--help                                  Prints option information.
    -l,--library <SLX id>                      The SLX id of the library to
                                               fetch. Can be repeated.
    -m,--metadata <file>                       Meta data CSV files on the local
                                               file system. Can be repeated.
    -p,--project <name>                        The name of the project to fetch.
                                               Can be repeated.
       --progress                              Display download progress to the
                                               console.
    -r,--reference-data-dir <directory>        The reference genome base
                                               directory.
    -R,--no-resume                             Don't resume partially complete
                                               downloads; always restart.
    -s,--species <name>                        The name of the species to align
                                               to.
    -S,--samplesheet <name>                    The name of the sample sheet
                                               file. Default is
                                               'samplesheet.csv'.
    -u,--url <url>                             The base URL of the Clarity
                                               server.
    -v,--genome-version <version>              The version of the genome to
                                               align to.
    -z,--dev                                   Use the development server.

Aligned files will be fetched if either -g or both -s and -v are defined.
Supported -g options are: grch37, grcm38, hg19, mm10.
Supported -a options are: bwa, bwamem, tophat.

Default reference data directory is /lustre/reference_data/mib-cri/reference_genomes

The "friendly" versions of the sample name and source identifier
are the same name turned into upper case and characters other than letters,
digits and underscore removed. Whitespace is turned into underscores.
These can help with using the name or id in file names, where other characters
can cause problems with the file system or in pipeline expressions.

The --combine-samples argument creates a sample sheet where samples with the
same name are considered the same sample. This may seem unnecessary, but without
this option samples are only considered the same if they are the same object
in Clarity (i.e. unique by LIMS identifier). This flag means same name equals
same sample, even if they are different objects in Clarity.

The --extra-metrics argument will attempt to download extra metrics files
that are not recorded in the LIMS by looking for files in the same location
as the main file and named in a standard manner based on the base name of
the main file.
```
