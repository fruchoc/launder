"""
output.py
The output interface for writing text files from the main program
(c) William Menz (wjm34) 2012
"""

import sys

class Output:
    
    def getData(self):
        return self.m_data
    
    def __init__(self, fname):
        self.m_fname    = fname
        self.m_data     = ""
        
        if self.m_fname != None:
            try:
                print("Opening {0} for writing.".format(self.m_fname))
                self.m_ostream  = open(self.m_fname, 'w')
            except:
                print("Couldn't open {0} for writing.".format(self.m_fname))
                raise
        else:
            self.m_ostream = sys.stdout
    
    def close(self):
        print("Closing file {0}".format(self.m_fname))
        self.m_ostream.close()

class XMLOut(Output):
    m_tab   = "  "  # Tab spacing characters
    m_fmt   = "{0.3e}"  # Formatting for floats
    
    def head(self):
        string = self.node("?xml", [["version", "1.0"]], "?")
        self.m_ostream.write(string)
    
    def node(self, text, attribs=[], endchar=""):
        # Gets a text string element of XML
        # supply attribs as list [[attribute, value], ..]
        string = "<"
        string += str(text)
        if len(attribs) > 0:
            string += " "
            for a, i in zip(attribs, range(0, len(attribs))):
                string += str(a[0]) + "=\"" + str(a[1]) + "\""
                if i != len(attribs) -1:  string += " "

        string += str(endchar) + ">\n"
        return string
    
    def short(self, param, value):
        # Get a string of the form <param>value</param>
        string = "<" + str(param) + ">"
        string += "{0}".format(value)
        string += "</" + str(param) + ">\n"
        return string
    
    def write1(self, text, attribs=[], tabs=0, endchar=""):
        string = ""
        string += self.indent(tabs)
        string += self.node(text, attribs, endchar)
        self.m_data += string
        self.m_ostream.write(string)
    
    def write2(self, param, value, tabs=0):
        string = ""
        string += self.indent(tabs)
        string += self.short(param, value)
        self.m_data += string
        self.m_ostream.write(string)
    
    def indent(self, tabs):
        # Writes a certain number of indents
        string = ""
        if tabs > 0:
            for t in range(0, tabs):
                string += self.m_tab
        return string

class DSVOut(Output):
    
    def line(self, items, delimiter, fmt=None):
        # Gets a line of DSV based on items list
        code = "{0"
        if fmt!=None: code += fmt
        code += "}"
        
        string = ""
        for i, j in zip(items, range(0,len(items))):
            string += code.format(i) 
            if j != len(items)-1: string += str(delimiter)
            j += 1
        
        return string