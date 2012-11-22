
import csv

def DSVParser(fname):
    # Parses a DSV file and returns a dictionary of {"header": [values]}
    
    
    



class LParser:
    # Generic parsing of DSV files. Generates a dictionary of lists 
    # (columns of DSV files).
    def __init__(self, fname):
        self.fname = fname
    
    def __check(self, fname):
        # Checks the dialect and whether the file has headers.
        s = csv.Sniffer()
        
        try:
            f = open(fname, "rb")
        except IOError:
            print "Couldn't open", fname
            return None
        else:
            # Use three lines of file for context
            l += f.readline() + f.readline() + f.readline()
            f.close()
            d = s.sniff(f)
            hh = s.has_header(f)
            
            return {"dialect": d, "has_headers": hh}
    
    def __preLoad(self, fname):
        # First get any properties of the DSV file
        p = self.__check(self.fname)
        
        # Create dictionaries to hold the fields
        r = {}
        cstr = csv.DictReader(open(fname, 'r'), 
                delimiter=p["dialect"].delimiter)
        
        # Generate the keys
        keys = []
        if p["has_headers"]:
            keys = cstr.fieldnames
        else:
            for i in range(0, len(cstr.fieldnames)):
                keys.append("col"+str(i))
        
        return (keys, cstr)
    
    def get(self):
        (keys, cstr) = self.__preLoad(fname)
        
        # Load the data from the lines
        for line in cstr:
            for k in keys:
                r[k].append(float(line[k]))
        
        return {"data": r, "keys": keys}

class PSLParser(LParser):
    # For the parsing of PSL files. This gets a list of dictionaries 
    # (rows of PSL files), and their keys.
    def __init__(self, name):
        super(LParser, self).__init__(fname)
        
    def get(self):
        (keys, cstr) = self.__preLoad(fname)
        
        # Load the data from the lines:
        for line in cstr:
            d = {}
            for k in keys:
                d[k] = line[k]
            r.append(d)
        
        return {"data": r, "keys": keys} 
