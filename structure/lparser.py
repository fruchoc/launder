import csv

def examine_filetype(fname):
    # A function which will examine the file structure and return a guess at
    # what type of file it is.
    p = LParser(fname)
    (keys, cstr) = p._pre_load()
    
    # Convert to lower case to be sure
    lkeys = []
    for k in keys:
        lkeys.append(k.lower())
    
    rstr = "other"
    for k in lkeys:
        # If we find Weight and Stat Weight it's probably a PSL file
        if "stat. weight" in k: rstr = "psl"
        # If we find an 'Err' key it's probably a -part type file
        if "err" in k: rstr = "part"
    return rstr

class LParser(object):
    # Generic parsing of DSV files. Generates a dictionary of lists 
    # (columns of DSV files).
    def __init__(self, fname):
        self.fname = fname
    
    def _check(self):
        # Checks the dialect and whether the file has headers.
        s = csv.Sniffer()
        
        try:
            f = open(self.fname, "rb")
        except IOError:
            print "Couldn't open", self.fname
            return None
        
        # Use three lines of file for context
        l = ""
        l += f.readline() + f.readline() + f.readline()
        f.close()
        d = s.sniff(l)
        hh = s.has_header(l)
        
        return {"dialect": d, "has_headers": hh}
    
    def _pre_load(self):
        # First get any properties of the DSV file
        p = self._check()
        
        # Create dictionaries to hold the fields
        r = {}
        cstr = csv.DictReader(open(self.fname, 'r'), 
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
        (keys, cstr) = self._pre_load()
        
        # Initialise keys dictionary
        r = {}
        for k in keys:
            r[k] = []
        
        # Load the data from the lines
        for line in cstr:
            for k in keys:
                r[k].append(float(line[k]))
        
        return {"data": r, "keys": keys}

class PartParser(LParser):
    # Used for parsing MOPS trajectories, e.g. a -part.csv file. Need to use 
    # this class to properly load in the Err columns of the part file.
    def __init__(self, name):
        super(PartParser, self).__init__(name)
    
    def __gen_dictionary(self, headers):
        # Generates a new list of headers to be distinct keys in the data dict.
        # Remove: Err keys
        # Add: a Err key for each other distinct header.
        keys = []
        for h in headers:
            if h != "Err":
                # Order is important!
                keys.append(h)
                if not ("Step" in h) and not (h == "Time (s)"):
                    # Add an error key too
                    keys.append("Err in " + str(h))
        return keys
    
    def get(self):
        # Can't use the usual interface due to the annoying presence of the 
        # Err columns.
        p = self._check()
        cstr = csv.reader(open(self.fname, "rb"), dialect=p["dialect"])
        
        keys = self.__gen_dictionary(cstr.next())
        
        # Load data now
        r = {}
        for k in keys:
            r[k] = []
        
        # Loop over DSV file lines
        for line in cstr:
            # Loop over DSV file columns (assume same order as in keys)
            for i in range(0, len(keys)):
                r[keys[i]].append(float(line[i]))
        
        return {"data": r, "keys": keys}

class PSLParser(LParser):
    # For the parsing of PSL files. This gets a list of dictionaries 
    # (rows of PSL files), and their keys.
    def __init__(self, name):
        super(PSLParser, self).__init__(name)
        
    def get(self):
        (keys, cstr) = self._pre_load()
        # Remove the "Stat weight (-)" entry to avoid confusion later
        si = 0
        for k in keys:
            if "Stat. Weight" in k: si = keys.index(k)
        if si: del keys[si]
        
        # Load the data from the lines:
        r = []
        for line in cstr:
            d = {}
            for k in keys:
                    d[k] = float(line[k])
            r.append(d)
        
        # Check that data has actually been found
        if len(r) < 1:
            raise ValueError("No data could be loaded from the PSL.")
        
        return {"data": r, "keys": keys} 

class DSVWriter:
    # Used for writing DSV files.
    def __init__(self, fname, delimiter=","):
        self.fname      = fname
        self.delimiter  = delimiter
        self.fstr       = open(self.fname, "wb")
        self.writer     = csv.writer(self.fstr, delimiter=self.delimiter)
    
    def __write_row(self, row):
        # Writes a single row (i.e. a list) of data into the CSV file
        self.writer.writerow(row)
    
    def write_rows(self, rows):
        # Write rows (list of lists) into a DSV file
        for row in rows:
            self.__write_row(row)
    
    def write_series(self, series):
        # Writes a series object into a DSV file
        # First get the data
        header = [series.axes_name("x"), series.axes_name("y")]
        data = []
        for x, y in zip(series.axes_values("x"), series.axes_values("y")):
            data.append([x, y])
        
        # Now write it
        self.__write_row(header)
        self.write_rows(data)
    
    def close(self):
        # Clean up any open streams
        self.fstr.close()
        del self.writer

class XMLWriter:
    # Used to write XML files.
    def __init__(self, fname):
        self.fname      = fname
        self.fstr       = open(self.fname, "wb")
        self.fstr.write('<?xml version="1.0"?>\n')
        
        try:
            from lxml import etree
        except:
            print("lxml not available.")
        
        # Start an lxml root
        self.root = etree.Element("output")
    
    def write_stats(self, s, subnode):
        # Writes the data from a lstats object
        for k in s.stats_keys():
            el = etree.Element(k)
            el.text = "{0}".format(s.stats[k])
            subnode.append(el)
    
    def write_ensemble_stats(self, e):
        # Writes the statistics of an ensemble
        # First write some preamble
        self.root.append(etree.Element("file", name=e.fname))
        
        for s in e.statlist:
            subnode = etree.Element("stats", type=s.keys())
            self.write_stats(s, subnode)
            self.root.append(subnode)
        
        self.fstr.write(etree.tostring(self.root, pretty_print=True))
    
    def close(self):
        self.fstr.close()
