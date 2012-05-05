"""
command.py
Source for dealing with the command-line interface of the postprocessor
(c) William Menz (wjm34) 2012
"""

import sys
import datamodel.mops_parser as MParser
 
class Command:
    
    def __init__(self, fname, consts):
        
        self.m_fname = fname        # filename to be processed
        self.m_consts = consts      # reference to Constants
        
        # Parse the headers to see what is there!
        parser = MParser.PSLHeaderParser(self.m_fname)
        line = parser.getHeaders()
        if line != None:
            parseddata = parser.scanForDiameters(line, self.m_consts)
        else:
            print("Couldn't parse headers")
            sys.exit(4)
        