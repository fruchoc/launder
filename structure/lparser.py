
import csv

def DSVParser(fname):
    # Parses a DSV file and returns a dictionary of {"header": [values]}
    
    s = csv.Sniffer()
    f = open(fname, "rb")
    # Use three lines of file for context
    l += f.readline() + f.readline() + f.readline()
    f.close()
    d = s.sniff(f)
    hh = s.has_header(f)
    
    cstr = csv.DictReader(open(fname, 'r'), delimiter=d.delimiter)
    
    # Create dictionaries to hold the fields
    results = {}
    if hh:
        for n in cstr.fieldnames:
            results[n] = []
    else:
        for i in range(0, len(cstr.fieldnames)):
            results["line"+str(i)] = []
    
    for line in cstr:
        for n in cstr.fieldnames:
            results[n].append(float(line[n]))
    
    return results

class LParser:
    # Generic parsing of DSV files.
    def __init__(self, fname):
        self.fname = fname
    
    def get(self):
        return DSVParser(fname)

class PSLParser(LParser):
    # For the parsing of PSL files.
    def __init__(self, name):
        super(LParser, self).__init__(fname)
        
    def get(self):
        # Get a dictionary of results.
        r = super(LParser, self).get()
        
