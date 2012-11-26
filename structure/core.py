import stats

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
    
    def keys(self):
        # Returns the available headers in the data
        keys = self.data[0].keys()
        
        # Don't allow Weight to be shown.
        cleaned = []
        for k in keys:
            if not "Weight" in k: cleaned.append(k)
        
        return cleaned
    
    def getList(self, key):
        # Gets a list of all data entries from the corresponding key
        l = []
        for p in self.data:
            l.append(p[key])
        return l
    
    def kernel_density(keys):
        # Generate statistics objects from the keys supplied.
        wts = self.getList("Weight (-)")
        
        # Convert keys to a list if not already
        if type(keys) != type([]): keys = [keys]
        
        for k in keys:
            d = {"Weight (-)": wts, k: self.getlist(k)}
            s = stats.LDensity(self.fname, d)
            # Call the calculation routine
            s.get(k)
            self.statlist.append(s)
    
    def pdf_as_series(self, i):
        # Returns a Trj generated from the statslist with index i.
        if i >= len(self.statslist):
            raise NameError("No stats object with this index.")
        # @TODO: FIX THE STATS OBJECT TO STORE THE KEY OF THE GENERATED STATS.
        s = self.statslist[i]
        x = Trj(s[""], s["mesh"])
        y = Trj("kernel density", s["pdf"])
        return Series("PDF of " + str(x.header), x, y)
    
    def cdf_as_series(self, i):
        # Returns a Trj generated from the statslist with index i.
        if i >= len(self.statslist):
            raise NameError("No stats object with this index.")
        
        s = self.statslist[i]
        x = Trj(s[""], s["mesh"])
        y = Trj("kernel density", s["cdf"])
        return Series("PDF of " + str(x.header), x, y)
        
    
class Trj:
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

class Series:
    # Holds two trajectories. Good for plotting x-y graphs.
    def __init__(self, x, y):
        if type(x) != type(Trj) or type(y) != type(Trj):
            raise NameError("Wrong objects passed to series.")
        self.x = x
        self.y = y
    
    def __str__(self):
        s = "[Series object]:\n"
        s += "x trajectory: " + str(self.x.header) + "\n"
        s += "y trajectory: " + str(self.y.header) + "\n"
    
    def axes_name(self, ax):
        # Returns the name of the axis
        if ax == "x": return self.x.header
        elif ax == "y": return self.y.header
        else:
            raise NameError("Unrecognised axes requested.")
    
    def axes_value(self, ax):
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
    
    
