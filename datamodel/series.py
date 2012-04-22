"""
(c) wjm34 2012
Series class is holds information about a series ready for plotting.
"""


class Series:
    def __init__(self, name, xseries, yseries, errors=None):
        # Initialise a series with xy values. Optional errors argument
        # for trajectory type series.
        
        names = self.getParameterName(name)
        self.m_name = names[0]
        self.m_unit = names[1]
        
        self.m_xvalues = xseries
        self.m_yvalues = yseries
        
        if not errors: 
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
