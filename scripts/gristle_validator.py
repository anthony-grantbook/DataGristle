#!/usr/bin/env python
""" Extracts subsets of input file based on user-specified columns and rows.
    The input csv file can be piped into the program through stdin or identified
    via a command line option.  The output will default to stdout, or redirected
    to a filename via a command line option.

    The columns and rows are specified using python list slicing syntax -
    so individual columns or rows can be listed as can ranges.   Inclusion
    or exclusion logic can be used - and even combined.

    To do:
       - work with analyze_file to produce a special exception for empty files.
       - improve msg if user provides no args - and tell about -h

    See the file "LICENSE" for the full license governing this code. 
    Copyright 2011 Ken Farmer
"""

#--- standard modules ------------------
from __future__ import division
import sys
import optparse
import csv
import fileinput
import collections
#from pprint import pprint as pp

#--- gristle modules -------------------
sys.path.append('../')     # allows running from project structure
sys.path.append('../../')  # allows running from project structure

import gristle.file_type           as file_type 

SMALL_SIDE = 0
LARGE_SIDE = 1

#------------------------------------------------------------------------------
# Command-line section 
#------------------------------------------------------------------------------
def main():
    """ runs all processes:
            - gets opts & args
            - analyzes file to determine csv characteristics unless data is 
              provided via stdin
            - runs each input record through process_cols to get output
            - writes records
    """
    bad_field_cnt = collections.defaultdict(int)

    (opts, files) = get_opts_and_args()
    if len(files) == 1:
        my_file                = file_type.FileTyper(files[0],
                                            opts.delimiter   ,
                                            opts.recdelimiter,
                                            opts.hasheader)
        try:
            my_file.analyze_file()
        except file_type.IOErrorEmptyFile:
            return 1

        dialect                = my_file.dialect
    else:
        # dialect parameters needed for stdin - since the normal code can't
        # analyze this data.
        dialect                = csv.Dialect
        dialect.delimiter      = opts.delimiter       
        dialect.quoting        = opts.quoting
        dialect.quotechar      = opts.quotechar
        dialect.lineterminator = '\n'                 # naive assumption

    rec_cnt = -1

    if opts.output == '-':
        outfile = sys.stdout
    else:
        outfile = open(opts.output, "w")

    for rec in csv.reader(fileinput.input(files), dialect):
        rec_cnt += 1
        if not rec:
            break
        if len(rec) != opts.fieldcnt:
           bad_field_cnt[len(rec)] += 1
           write_fields('field_cnt-%d' % len(rec), rec_cnt, outfile, rec, dialect.delimiter)

    fileinput.close()
    if opts.output != '-':
        outfile.close()

    return 0




def write_fields(label, rec_cnt, outfile, fields, delimiter):
    """ Writes output to output destination.
        Input:
            - list of fields to write
            - output object
        Output:
            - delimited output record written to stdout
        To Do:
            - write to output file
    """
    rec = label + delimiter + str(rec_cnt) + delimiter + delimiter.join(fields)
    outfile.write(rec + '\n')
         


def get_opts_and_args():
    """ gets opts & args and returns them
        Input:
            - command line args & options
        Output:
            - opts dictionary
            - args dictionary 
    """
    use = ("%prog is used to extract column and row subsets out of files "
           "and write them out to stdout or a given filename: \n" 
           " \n"
           "   %prog [file] [misc options]")
    parser = optparse.OptionParser(usage = use)

    parser.add_option('-o', '--output', 
           default='-',
           help='Specifies the output file.  The default is stdout.  Note that'
                'if a filename is provided the program will override any '
                'file of that name.')
    parser.add_option('-f', '--fieldcnt',
           type=int,
           help=('Specify the number of fields in the record'))
    parser.add_option('-d', '--delimiter',
           help=('Specify a quoted single-column field delimiter. This may be'
                 'determined automatically by the program.'))
    parser.add_option('--quoting',
           default=False,
           help='Specify field quoting - generally only used for stdin data.'
                '  The default is False.')
    parser.add_option('--quotechar',
           default='"',
           help='Specify field quoting character - generally only used for '
                'stdin data.  Default is double-quote')
    parser.add_option('--recdelimiter',
           help='Specify a quoted end-of-record delimiter. ')
    parser.add_option('--hasheader',
           default=False,
           action='store_true',
           help='Indicate that there is a header in the file.')

    (opts, files) = parser.parse_args()

    if files:
        if len(files) > 1 and not opts.delimiter:
            parser.error('Please provide delimiter when piping data into program via stdin or reading multiple input files')
    else:   # stdin
        if not opts.delimiter:
            parser.error('Please provide delimiter when piping data into program via stdin or reading multiple input files')

    return opts, files



if __name__ == '__main__':
    sys.exit(main())

