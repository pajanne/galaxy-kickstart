class CompressedFastq( CompressedArchive ):
    """
        Class describing an compressed fastq file
        This class can be sublass'ed to implement archive filetypes that will not be unpacked by upload.py.
    """
    file_ext = "fq.gz"

    def set_peek( self, dataset, is_multi_byte=False ):
        if not dataset.dataset.purged:
            dataset.peek = "Compressed fastq file"
            dataset.blurb = nice_size( dataset.get_size() )
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'

    def display_peek( self, dataset ):
        try:
            return dataset.peek
        except:
            return "Compressed fastq file (%s)" % ( nice_size( dataset.get_size() ) )


Binary.register_unsniffable_binary_ext("fq.gz")
