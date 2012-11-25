import math
PI = 3.141592653589793

class LStats:
    # A class for holding general statistics about a PSL file, i.e.
    # a particle ensemble.
    
    def __init__(self, fname, data):
        # Name of the file from which stats are to be generated
        self.fname = fname
        # Name of this particular instantiation
        self.name  = fname
        # Dictionary of data to be used in calculation.
        self.data  = data
        
        # Dictionary of the statistics
        self.stats = {}
    
    def __str__(self):
        s = "[Stats Object]: " + self.name + "\n"
        s += "data: " + self.stats.__str__()
        return s
    
    def setName(self, name):
        self.name = name
    
    def get(self, key):
        # Get the statistics, using a key
        self.generate(self.data["Weight (-)"], self.data[key])
    
    def generate(self, weights, values):
        # Generate basic information about an ensemble
        self.stats["num"] = len(values)
        
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
            gsdev += w * math.pow(math.log(v) - math.log(gmean, 2.0)
        
        asdev = math.sqrt(asdev / wtsum)
        gsdev = math.exp(math.sqrt(gsdev / wtsum))
        self.stats["asdev"] = asdev
        self.stats["gsdev"] = gsdev

class LDensity(LStats):
    # A derived class to hold information about a distribution
    def __init__(self, fname, name, data):
        # Call parent class
        super(LDensity, self).__init__(self, fname, name, data)
        
        # Store some extra variables
        self.bandwidth = 0.0
        self.npts      = 64
        self.lb        = 0.0
        self.ub        = 0.0
        
        # Choice of kernel
        self.kernel    = "Gaussian"
    
    def setBounds(self, lb, ub):
        # Set the boundaries for the distribution
        if lb > ub:
            print "Upper bound must be greater than lower bound."
        else:
            self.lb = lb
            self.ub = ub
    
    def setBandwidth(self, h):
        # Set the bandwidth of the distribution.
        self.bandwidth - h
    
    def setNumberOfPoints(self, n):
        # Set number of points in the mesh
        self.npts = n
    
    def setKernel(self, k):
        # Choice of kernel to use
        self.kernel = k
    
    def __estimateBandwidth(self):
        # Use the Normal Distibution Approximation
        # http://en.wikipedia.org/wiki/Kernel_density_estimation
        return 1.06 * self.stats["asdev"] * pow(self.stats["num"], -(1.0/5.0))
    
    def __mesh(self):
        # Generate the mesh for the distribution.
        m = []
        
        d = (self.ub - self.lb) / self.npts
        for i in range(0, self.npts):
            m.append(self.lb + d * i)
        
        self.stats["mesh"] = m
    
    def __kernel(self, weights, values, p):
        # Evaluate the kernel function
        k = 0.0
        
        if "Gaussian" in self.kernel:
            for di, w in zip(diameters, weights):
                ki = w * math.exp(-pow( (p - di)/self.h, 2.0)/2.0)
                if ki > 1.0e-40:
                    k = k + ki
            k = (1.0/math.sqrt(PI*2.0)) * k / (sum(weights) * self.h)
        else:
            raise NameError('Unknown kernel type specified.')
        
        return k
    
    def __locate(self, p):
        # Locate a point on the CDF with probability p.
        v = 0
        mesh = self.stats["mesh"]
        cdf = self.stats["cdf"]
        
        for i in range(1, len(c)):
            if p == cdf[i]:
                v = mesh[i]
            elif (cdf[i-1] < p and cdf[i] > p):
                # Linear interpolation on CDF
                dM = mesh[i] - mesh[i-1]
                dV = cdf[i] - cdf[i-1]
                v = mesh[i-1] + dM * (p - cdf[i-1]) / dV
        
        if not v:
            print "Warning: got val " + str(v) + " at " + str(p) + "\n."
        
        return v
    
    def generate(self, weights, values):
        # Generate a distribution function for this instance.
        
        # Call parent function.
        super(LStats, self).generate(weights, values)
        
        # Now generate a probability distribution
        pdf = []
        
        # Loop over the mesh points
        for m in self.stats["mesh"]:
            pdf.append(self.__kernel(weights, values, m))
        self.stats["pdf"] = pdf
        
        # Now generate cumulative density function
        cdf = [self.stats["pdf"]]
        asum = 0
        
        for i in range(1, len(self.stats["mesh"]):
            # Calculate integral element
            dx = 0.5 * (self.stats["mesh"][i]-self.stats["mesh"][i-1])
                    * (pdf[i]+pdf[i-1])
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
            if self.psd[i] > dmax:
                dmax = self.psd[i]
                imax = i
        self.stats["mode"] = mesh[imax]
        
        # Get the 'quartiles'
        self.stats["d10"] = self.__locate(0.1)
        self.stats["d50"] = self.__locate(0.5)
        self.stats["d90"] = self.__locate(0.9)
