import re

class Parser:
    # Default constructor
    def __init__(self, fname):
        self.m_fname = fname
        
        try:
            print("Loading file {0}.".format(self.m_fname))
            self.m_istream = open(self.m_fname, "r")
        except:
            print("Couldn't open file {0}.".format(self.m_fname))
            raise
    
    # Closes the CSV
    def closeCSV(self):
        print("Closing file {0}.".format(self.m_fname))
        self.m_istream.close()
    
    # Reads a CSV line and converts all to float or string
    def getCSVLine(self, csvline, datatype):
        
        # Split on comma delimiter
        line = csvline.split(',')
        
        # Remove any \n characters
        cleanline = []
        for l in line:
            
            # Convert to floats
            if (datatype == type(1.0)):
                cleanline.append(float(l.strip()))
            elif (datatype == type("str")):
                cleanline.append(str(l.strip()))
            else:
                print("Unrecognised format in file {0}".format(self.m_fname))
                raise
                
        return cleanline

class HeaderParser(Parser):
    # Used to investigate only the header of a file for loading series
    
    def getHeaders(self):
        print("Getting headers of file {0}".format(self.m_fname))
        data = []   # Empty list for headers
        
        # Get first line
        csvline = self.m_istream.readline()
        self.closeCSV()
        line = self.getCSVLine(csvline, type('str'))
        
        # Check the file format
        if self.__checkForStandardFormat(line):
            i = 0
            for col in line[2:]:
                if (i % 2 == 0):
                    data.append(col)
                i += 1
        else:
            return None
        
        return data
    
    def __checkForStandardFormat(self, line):
        # Given a list of headers from a csv file, check it is compatible
        
        ans = False
        if (line[0] == "Step") and re.search("Time", line[1]):
            ans = True
        else:
            print("Unrecognised MOPS file format.")
            ans = False
        return ans