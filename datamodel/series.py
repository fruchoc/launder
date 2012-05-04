"""
(c) wjm34 2012
Series class is holds information about a series ready for plotting.
"""

# Import pygtk and gtk packages.
# obtain for any platform at http://www.pygtk.org
try:
    import pygtk
    pygtk.require('2.0')
    import gtk
except:
    print("Couldn't find pygtk or gtk.")
    sys.exit(1)


class Series:
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

class Trajectory(Series):
    
    def getPlotPaneList(self):
        item = [self.m_name, self.m_unit]
        return item

class PSD(Series):
    
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