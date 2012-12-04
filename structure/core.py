import stats

# Class-less functions only for use in this file.
def guess_unit(string):
    # From a string, attempt to guess what the unit is.
    # Expects a formal like Diameter (nm)
    sp = string.split("(")
    if len(sp) > 1:
        return sp[1].split(")")[0]
    else: return "?"

class Ensemble:
    # An ensemble object holds information from a PSL file. It is used
    # as the source data from which the stats data are derived.
    
    def __init__(self, fname, data):
        
        # Name of the file from which stats are to be generated
        self.fname = fname
        
        # Raw data from the PSL file
        self.data  = data
        
        # List of references to statistics objects of this ensemble.
        self.statlist = []
    
    def __str__(self):
        s = "[Ensemble Object]: " + self.fname + "\n"
        s += "with keys: " + self.keys().__str__() + "\n"
        s += "with " + str(len(self.statlist)) + " stats.\n"
        return s
    
    def keys(self):
        # Returns the available headers in the data
        keys = self.data[0].keys()
        
        # Don't allow Weight to be shown.
        cleaned = []
        for k in keys:
            if not "Weight" in k: cleaned.append(k)
        
        return cleaned
    
    def get_list(self, key):
        # Gets a list of all data entries from the corresponding key
        l = []
        for p in self.data:
            l.append(p[key])
        return l
    
    def kernel_density(self, keys):
        # Generate statistics objects from the keys supplied.
        wtstr = "Weight (cm-3)"
        wts = self.get_list(wtstr)
        
        # Convert keys to a list if not already
        if type(keys) != type([]): keys = [keys]
        
        for k in keys:
            d = {wtstr: wts, k: self.get_list(k)}
            s = stats.LDensity(self.fname, d)
            # Call the calculation routine
            s.get(k)
            self.statlist.append(s)
    
    def pdf_as_series(self, i=0):
        # Returns a Trj generated from the statslist with index i.
        if i >= len(self.statlist):
            raise NameError("No stats object with this index.")
        # @TODO: FIX THE STATS OBJECT TO STORE THE KEY OF THE GENERATED STATS.
        s = self.statlist[i]
        x = Trj(s.keys(), s.stats["mesh"])
        y = Trj("Kernel Density (1/"+guess_unit(s.keys())+")", s.stats["pdf"])
        return Series("PDF of " + str(x.header), x, y)
    
    def cdf_as_series(self, i=0):
        # Returns a Trj generated from the statslist with index i.
        if i >= len(self.statlist):
            raise NameError("No stats object with this index.")
        
        s = self.statlist[i]
        x = Trj(s.keys(), s.stats["mesh"])
        y = Trj("Cumulative Density (-)", s.stats["cdf"])
        return Series("CDF of " + str(x.header), x, y)

class MOPSTrajectories(object):
    # An object which conveniently processes all trajectories in a MOPS -part
    # style CSV file.
    
    def __init__(self, fname, data):
        self.fname = fname
        # Raw data from the parser
        self.data  = data["data"]
        
        # Get 'edited' keys of the parsed file
        self.keys = data["keys"] 
    
    def times(self):
        return self.data["Time (s)"]
    
    def steps(self):
        return self.data["Step"]
    
    def get_keys(self):
        # Get a edited list of keys which excludes errors and such.
        quays = []
        for k in self.keys:
            if "Time" in k or "Step" in k or "Err" in k:
                # Do nothing
                pass
            else:
                quays.append(k)
        return quays
    
    def get_series(self, xkey, ykey):
        # Gets a series with certain x and y keys.
        x = Trj(xkey, self.times())
        y = Trj(ykey, self.data[ykey], self.data["Err in " + str(ykey)])
        return Series("Series " + str(ykey), x, y)
    
    def series_list(self, xkey = "Time (s)"):
        # Returns a list series representing all x (with xkey) - y series
        # from parsed file.
        slist = []
        for k in self.get_keys():
            slist.append(get_series(xkey, k))
        return slist


class Trj(object):
    # Trajectories store a header, values and some error measurement
    
    def __init__(self, header, values, err=[]):
        # Name of the trajectory.
        self.header  = header
        # Values of the trajectory.
        self.values  = values
        # A measure of error of the series, e.g. 99.9% confidence
        # interval of MOPS
        self.err     = err
        
    def __str__(self):
        s = "[Trj object]: " + str(self.header) + "\n"
        s += "with " + str(len(self.values)) + "values "
        s += "and " + str(len(self.values)) + "errors.\n"
        return s
    
    def add_errors(self, err):
        self.err = err
    
    def ub(self):
        # Gets the upper bound
        l = []
        for v, e in zip(self.values, self.err):
            l.append(v + e)
        return l
    
    def lb(self):
        # Gets the upper bound
        l = []
        for v, e in zip(self.values, self.err):
            l.append(min(v - e), 0.0)
        return l

class Series(object):
    # Holds two trajectories. Good for plotting x-y graphs.
    def __init__(self, name, x, y):
        self.name = name
        
        # Can also store the filename of a Series
        self.filename = ""
        
        # x and y are Trj objects.
        self.x = x
        self.y = y
    
    def __str__(self):
        s = "[Series object]: " + str(self.name) + "\n"
        s += "x trajectory: " + str(self.x.header) + "\n"
        s += "y trajectory: " + str(self.y.header) + "\n"
        return s
    
    def axes_name(self, ax):
        # Returns the name of the axis
        if ax == "x": return self.x.header
        elif ax == "y": return self.y.header
        else:
            raise NameError("Unrecognised axes requested.")
    
    def axes_values(self, ax):
        # Returns the values of the axis
        if ax == "x": return self.x.values
        elif ax == "y": return self.y.values
        else:
            raise NameError("Unrecognised axes requested.")
    
    def axes_error(self, ax):
        # Returns the error values of the axis
        if ax == "x": return self.x.err
        elif ax == "y": return self.y.err
        else:
            raise NameError("Unrecognised axes requested.")
    
    def __match(self, val, values):
        # Return the index in the values list which corresponds to val
        for i in range(0, len(values)):
            if abs(values[i] - val)  / val < 1.0e-6:
                return i
        
        # Otherwise return the last value of the list.
        return len(values) - 1
    
    def y_at_x(self, val):
        # Return the y value for a given x value
        return self.y.values[self.__match(val, self.x.values)]
    
    def set_file(self, fname):
        # Sets the filename of the object
        self.filename = fname
    
    def get_data_list(self):
        # Gets a list of data for convenient display in a Liststore in the GUI
        return [self, self.name, self.axes_name("x"), self.axes_name("y"), 
                self.filename]