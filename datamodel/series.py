"""
(c) wjm34 2012
Series class is holds information about a series ready for plotting.
"""

class Series:
    
    # Header for creating DSV files
    m_dheader = ["xvalue", "yvalue"]
    
    def __init__(self, name, xseries, yseries, errors=None):
        # Initialise a series with xy values. Optional errors argument
        # for trajectory type series.
        
        names = self.getParameterName(name)
        self.m_name = names[0]
        self.m_unit = names[1]
        
        self.m_xvalues = xseries
        self.m_yvalues = yseries
        
        if errors: 
            self.m_yerrors = errors
            self.m_lower_ci = []
            self.m_upper_ci = []
            
            for v, e in zip(yseries, errors):
                self.m_lower_ci.append(max(v - e, 0.0))
                self.m_lower_ci.append(v + e)
    
        # Returns a parameter's name and unit as vector
    def getParameterName(self, string):
        
        try:
            splitstring = string.split('(')
            unit = splitstring[1].split(')')[0]
            param = splitstring[0].strip()
        except:
            param = string
            unit = "-"
        
        return [param, unit]
    
    def printSeries(self):
        print self.m_name, self.m_unit
        for x, y in zip(self.m_xvalues, self.m_yvalues):
            print x, y
    
    def getYatX(self, xval=None, tol=1.0e-6):
        # Gets the corresponding yvalue for a given xvalue
        # no argument returns the last 
        
        if xval == None: return self.m_yvalues[len(self.m_yvalues)-1]
        else:
            
            row = 0
            i = 0
            for x in self.m_xvalues:
                if abs(x-xval)/x < tol: row = i
                i += 1
            return self.m_yvalues[row]

    def getEatX(self, xval=None, tol=1.0e-6):
        # Gets the corresponding yerror for a given xvalue
        # no argument returns the last 
        
        if xval == None: return self.m_yerrors[len(self.m_yerrors)-1]
        else:
            
            row = 0
            i = 0
            for x in self.m_xvalues:
                if abs(x-xval)/x < tol: row = i
                i += 1
            return self.m_yerrors[row]
    
    def getOutputData(self):
        # Gets the data formatted in a convenient way for writing
        # to a DSV file.
        data = []
        data.append(self.m_dheader)
        
        if hasattr(self, "m_yerrors"):
            
            for x, y, e in zip(self.m_xvalues, self.m_yvalues, \
                               self.m_yerrors):
                data.append([x, y, e])
        else:
            for x, y in zip(self.m_xvalues, self.m_yvalues):
                data.append([x, y])
        return data

class Trajectory(Series):
    
    # Header for creating DSV files
    m_dheader = ["xvalue", "yvalue", "error", "lowerci", "upperci"]
    
    def getPlotPaneList(self):
        item = [self.m_name, self.m_unit]
        return item

class PSD(Series):
    
    # Header for creating DSV files
    m_dheader = ["mesh", "density"]
    
    def setType(self, type, consts):
        self.m_type = consts.matchDiam(type)
    
    def setH(self, h):
        # Sets the bandwidth of the PSD
        self.m_h = h
    
    def setParent(self, parent):
        self.m_parent = parent
    
    def getPlotPaneList(self):
        item = [self.m_type, self.m_h, self.m_parent]
        return item