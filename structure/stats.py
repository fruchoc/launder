import math
PI = 3.141592653589793

class LStats(object):
    # A class for holding general statistics about a PSL file, i.e.
    # a particle ensemble.
    
    def __init__(self, fname, data):
        # Name of the file from which stats are to be generated
        self.fname = fname
        # Name of this particular instantiation
        self.name  = fname
        # Dictionary of data to be used in calculation.
        # expect "Weight" and "Another key"
        self.data  = data
        
        # Check that there are only two entries in the dictionary
        if len(self.data.keys()) > 2:
            raise ValueError("Too many entries in the stats key dictionary.")
        
        # Guess what the weight key is (backward compatibility)
        self.wtkey = "Weight (cm-3)"
        for k in self.data.keys():
            if "weight" in k.lower(): self.wtkey = k
        
        # Dictionary of the statistics
        self.stats = {}
    
    def __str__(self):
        s = "[Stats Object]: " + self.name + "\n"
        s += "data: " + self.stats.__str__() + "\n"
        return s
    
    def setName(self, name):
        self.name = name
    
    def keys(self):
        # Returns the data keys which don't correspond to weight
        quays = []
        for k in self.data.keys():
            if not ("weight" in k.lower()): quays.append(k)
        return quays[0]
    
    def stats_keys(self):
        # Returns the stats keys for output, excluding anything that is a list
        quays = []
        
        for k, v in self.stats.iteritems():
            if type(v) == float or type(v) == int:
                quays.append(k)
        
        return quays
    
    def get(self, key):
        # Get the statistics, using a key
        self.generate(self.data[self.wtkey], self.data[key])
    
    def generate(self, weights, values):
        # Generate basic information about an ensemble
        self.stats["num"] = len(values)
        self.stats["min"] = min(values)
        self.stats["max"] = max(values)
        
        # Initialise some variables, get means first
        amean = 0.0
        gmean = 1.0
        wtsum = sum(weights)
        p = 1.0 / wtsum
        
        for w, v in zip(weights, values):
            amean += w * v
            gmean *= math.pow(v, w * p)
        amean /= wtsum
        # Save in stats dictionary
        self.stats["amean"] = amean
        self.stats["gmean"] = gmean
        
        # Get the standard deviations
        asdev = 0.0
        gsdev = 0.0
        
        for w, v in zip(weights, values):
            asdev += w * math.pow(v - amean, 2.0)
            gsdev += w * math.pow(math.log(v) - math.log(gmean), 2.0)
        
        asdev = math.sqrt(asdev / wtsum)
        gsdev = math.exp(math.sqrt(gsdev / wtsum))
        self.stats["asdev"] = asdev
        self.stats["gsdev"] = gsdev

class LDensity(LStats):
    # A derived class to hold information about a distribution
    def __init__(self, fname, data):
        # Call parent class
        super(LDensity, self).__init__(fname, data)
        
        # Store some extra variables
        self.stats["bandwidth"] = 0.0
        self.stats["npts"]      = 64
        self.stats["lb"]        = 0.0
        self.stats["ub"]        = 0.0
        
        # Choice of kernel
        self.kernel    = "Gaussian"
    
    def setBounds(self, lb, ub):
        # Set the boundaries for the distribution
        if lb > ub:
            print "Upper bound must be greater than lower bound."
        else:
            self.stats["lb"] = lb
            self.stats["ub"] = ub
    
    def setBandwidth(self, h):
        # Set the bandwidth of the distribution.
        self.stats["bandwidth"] - h
    
    def setNumberOfPoints(self, n):
        # Set number of points in the mesh
        self.stats["npts"] = n
    
    def setKernel(self, k):
        # Choice of kernel to use
        self.kernel = k
    
    def __estimateBandwidth(self):
        # Use the Normal Distibution Approximation
        # http://en.wikipedia.org/wiki/Kernel_density_estimation
        self.stats["bandwidth"] = 1.06 * self.stats["asdev"] \
            * pow(self.stats["num"], -(1.0/5.0))
    
    def __mesh(self):
        # Generate the mesh for the distribution.
        m = []
        
        d = (self.stats["ub"] - self.stats["lb"]) / self.stats["npts"]
        for i in range(0, self.stats["npts"]):
            m.append(self.stats["lb"] + d * i)
        
        self.stats["mesh"] = m
    
    def __kernel(self, weights, values, p):
        # Evaluate the kernel function
        k = 0.0
        
        if "Gaussian" in self.kernel:
            for di, w in zip(values, weights):
                ki = w
                ki *= math.exp(-pow( (p - di)/self.stats["bandwidth"], 2.0)/2.0)
                if ki > 1.0e-40:
                    k = k + ki
            k = (1.0/math.sqrt(PI*2.0)) * \
                k / (sum(weights) * self.stats["bandwidth"])
        else:
            raise NameError('Unknown kernel type specified.')
        
        return k
    
    def __locate(self, p):
        # Locate a point on the CDF with probability p.
        v = 0
        mesh = self.stats["mesh"]
        cdf = self.stats["cdf"]
        
        for i in range(1, len(cdf)):
            if p == cdf[i]:
                v = mesh[i]
            elif (cdf[i-1] < p and cdf[i] > p):
                # Linear interpolation on CDF
                dM = mesh[i] - mesh[i-1]
                dV = cdf[i] - cdf[i-1]
                v = mesh[i-1] + dM * (p - cdf[i-1]) / dV
        
        if not v:
            print "Warning: got val " + str(v) + " at cdf=" + str(p) + "."
        
        return v
    
    def generate(self, weights, values, auto=True):
        # Generate a distribution function for this instance.
        
        # Call parent function.
        super(LDensity, self).generate(weights, values)
        
        # If auto, automatically guess some parameters.
        if auto:
            self.setKernel("Gaussian")
            self.setBounds(0.6*self.stats["min"], 1.4*self.stats["max"])
            self.__mesh()
            self.__estimateBandwidth()
        
        # Now generate a probability distribution
        pdf = []
        
        # Loop over the mesh points
        for m in self.stats["mesh"]:
            pdf.append(self.__kernel(weights, values, m))
        self.stats["pdf"] = pdf
        
        # Now generate cumulative density function
        cdf = [self.stats["pdf"][0]]
        asum = 0
        
        for i in range(1, len(self.stats["mesh"])):
            # Calculate integral element
            dx = 0.5 * (self.stats["mesh"][i]-self.stats["mesh"][i-1]) * \
                (pdf[i]+pdf[i-1])
            cdf.append(dx + cdf[i-1])
            asum += dx
        
        if asum < 0.9 or asum > 1.05:
            print "Warning: obtained area of " + str(asum) + "\n."
        
        self.stats["area"] = asum
        self.stats["cdf"]  = cdf
        
        # Get the mode of the PSD
        dmax = 0
        imax = 0
        for i in range(0, len(pdf)):
            if pdf[i] > dmax:
                dmax = pdf[i]
                imax = i
        self.stats["mode"] = self.stats["mesh"][imax]
        
        # Get the 'quartiles'
        self.stats["d10"] = self.__locate(0.1)
        self.stats["d50"] = self.__locate(0.5)
        self.stats["d90"] = self.__locate(0.9)
