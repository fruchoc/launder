import re
import series

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
    def getCSVLine(self, csvline, datatype, delimiter):
        
        # Split on comma delimiter
        if delimiter == "tab": line = csvline.split()
        else: line = csvline.split(delimiter)
        
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
        line = self.getCSVLine(csvline, type('str'), ',')
        
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

class TrajectoryParser(Parser):
    # Parses MOPS moment files with time versus some parameter.
    # Returns a trajectory type for each of the indices given
    
    def start(self, indices):
        # Loads the trajectories with headers of a given index
        # as supplied by <indices>, a list of header indices
        
        # Check there are some indices supplied!
        if len(indices) < 1:
            print("No indices supplied for loading.")
            self.closeCSV()
            return None
        
        # Check there is enough information in the CSV file
        result = self.checkForEnoughInfo()
        if (not result):
            print("No data in file {0}!".format(self.m_fname))
            self.closeCSV()
            return None
        
        # Convert indices
        csvindices = self.convertPassedIndices(indices)
        
        # Get headers again.
        headers = self.getSpecificHeaders(indices)

        # Initialise a list of lists for storing data
        values = []
        errors = []
        for col in headers:
            values.append([])
            errors.append([])
        
        # Loop over the result data in the CSV file
        time = []
        for line in result:
            # Append time data
            time.append(line[1])
            # Get data and values
            for i in range(0, len(headers)):
                j = csvindices[i]
                data = self.getDataAndErrors(line, j)
                #print j, headers[i], data
                values[i].append(data[0])
                errors[i].append(data[1])
        
        # Now initialise the series!
        allseries = []
        for i in range(0, len(headers)):
            newseries = series.Trajectory(headers[i], time, values[i],\
                                           errors[i])
            allseries.append(newseries)
        
        return allseries
    
    def checkForEnoughInfo(self):
        lines = []
        headers = self.m_istream.readline()
        for csvline in self.m_istream:
            line = self.getCSVLine(csvline, type(1.0), ',')
            lines.append(line)
        
        self.closeCSV()
        
        if len(lines) < 1:
            return False
        else:
            return lines
    
    def convertPassedIndices(self, indices):
        # Given a list of indices from the app (which don't correspond
        # to the real ones in the file), convert them into the actual
        # column numbers in the moment file.
        newindices = []
        for ind in indices:
            newindices.append(int(2*(ind+1)))
        return newindices

    def getSpecificHeaders(self,  indices):
        # Given a list of indices, return a list with only
        # the data entries given by those indices
        
        hparser = HeaderParser(self.m_fname)
        allheaders = hparser.getHeaders()
        
        headers = []
        for i in indices:
            headers.append(allheaders[i])
        return headers
        
    def getDataAndErrors(self, datalist, index):
        # Given a list of data an index, return a list with only
        # values and errors
        return [datalist[index], datalist[index+1]]

class MiscFileParser(Parser):
    # Imports miscellaneous files into the system (e.g. DSV files)
    # Assume file has headers
    
    def start(self, delimiter):
        
        # Read in the file.
        try:
            (headers, data) = self.parse(delimiter)
        except:
            print("Couldn't parse file")
            return []
        
        results = []
        if len(headers) < 1:
            print("Error getting the headers!")
        else:
            fixed = self.convertData(data)
            
            # Generate series
            results = []
            for i in range(1, len(headers)):
                newseries = series.Trajectory(headers[i], fixed[0], fixed[i])
                results.append(newseries)
        return results
    
    def convertData(self, data):
        # Converts a list of rows to a list of columns
        
        # Create column list first
        cols = []
        for col in data[0]:
            cols.append([])
        
        # Now loop over rows
        for row in data:
            for i in range(0, len(row)):
                cols[i].append(row[i])
        
        return cols
    
    def parse(self, delimiter):
        # Parses a misc. DSV file
        
        # First get headers
        line = self.m_istream.readline()
        headers = self.getCSVLine(line, type('str'), delimiter)
        
        # Parse file based on given delimiter
        data = []
        for csvline in self.m_istream:
            data.append(self.getCSVLine(csvline, type(1.0), delimiter))
        self.closeCSV()
        
        if len(data) > 0:
            return (headers, data)
        else:
            return ([], [])

class PSLHeaderParser(Parser):
    # Class for processing PSL files' headers
    
    def getHeaders(self):
        print("Getting headers of file {0}".format(self.m_fname))
        
        # Get first line
        csvline = self.m_istream.readline()
        self.closeCSV()
        line = self.getCSVLine(csvline, type('str'), ',')
    
        # Check the file format
        if self.__checkForStandardFormat(line):
            return line
        else:
            return None
    
    def __checkForStandardFormat(self, line):
        # Given a list of headers from a csv file, check it is compatible
        
        ans = False
        if (line[0] == "Weight"):
            ans = True
        else:
            print("Unrecognised MOPS PSL file format.")
            ans = False
        return ans
        

class PSLParser(Parser):
    # Class to parse MOPS psl files
    
    def start(self):
        print 1