"""
Brno University of Technology
Project: IPP1
Author: Vladislav Khrisanov (xkhris00)
"""

import sys
from parser import Parser


help_message = """
Desc: filter script parse.py
in:   source code in IPP-code24 from the stdin
out:  an XML representation of the program to the stdout

usage:
    parse.py [--help]
    parse.py [--stats=file] [stats_options] [--stats=file [...]]
    
optional arguments:
    --help        show this help message and exits
    --stats=file  prints chosen statistics about the sourcecode to the file
    
stats_options:
    --loc           lines of code
    --comments      number of comments
    --labels        number of labels
    --jumps         number of jumps
    --fwjumps       number of jumps forward
    --backjumps     number of jumps backwards
    --badjumps      number of jumps to missing label
    --frequent      most frequent opcode(s)
    --print=string  string
    --eol           newline"""

parser = Parser()

if len(sys.argv) > 1:
    # handle the "--help" argument
    if sys.argv[1] == '--help':
        if len(sys.argv) > 2:
            sys.exit(10)
        elif len(sys.argv) == 2:
            print(help_message)
            sys.exit(0)
    # process the possible stats request
    elif sys.argv[1].split('=', 1)[0] == '--stats':
        parser.gather_stats()
    # invalid parameters
    else:
        sys.exit(10)

parser.run()
