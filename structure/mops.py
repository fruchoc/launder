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
    
    def stats(keys):
        # Generate statistics objects from the keys supplied.
        wts = self.getList("Weight (-)")
        for k in keys:
            d = {"Weight (-)": wts, k: self.getlist(k)}
            s = stats.LStats(self.fname, d)
            self.statlist.append(s)
    
    
