# Global imports
import math

# Declare constants
PI = 3.141592653589793

class KernelDensity:
    # Default constructor
    def __init__(self, diameters, weights):
        # The KDE object it initialised with a list of diameters and weights
        # from the calling Ensemble class.
        
        self.diameters = diameters
        self.weights = weights
        
        # Default properties of KDE curve
        self.bound_multiplier = 0.4     # percentage above/below max/min diameters
        self.smoothing = 1.0            # 'h' factor for smoothing PSD
        self.kerneltype = "Gaussian"    # type of kernel
        self.num_points = 64            # number of points needed for PSD (multiple of 2)
        
        # Set the default bounds of the PSD
        self.lowerbound = (1 - self.bound_multiplier) * min(self.diameters)
        self.upperbound = (1 + self.bound_multiplier) * max(self.diameters)
        
        # Calculate ensemble statistics
        self.smoothing = self.getBandwidth()
        
        # Make the mesh for the PSD
        self.mesh = self.makeMesh(self.num_points, self.lowerbound, self.upperbound)
        
        # Create the PSD
        self.psd  = self.calculatePSD(self.diameters, self.weights)
        

    # Set the lower bound of the estimated PSD
    def setLowerBound(self, lowerbound):
        self.lowerbound = lowerbound
    
    # Set the upper bound of the estimated PSD
    def setUpperBound(self, upperbound):
        self.upperbound = upperbound
    
    # Use the 'normal distribution approximation' to estimate for Gaussian kernels
    # http://en.wikipedia.org/wiki/Kernel_density_estimation
    def getBandwidth(self):
        if self.kerneltype == "Gaussian":
            # Check that ensemble stats have already been found.
            if (not hasattr(self, 'astdev')):
                self.calculateEnsembleStats()
            
            return (1.06 * self.astdev * pow(len(self.diameters), -(1.0/5.0)))
        else:
            return 1.0
    
    # Get the kernel density estimated PSD
    # returns a list of mesh diameters and frequency values [[dmesh], [freq]]
    def calculatePSD(self, diameters, weights):
        
        psd = []
        
        # Loop over the mesh points
        for dm in self.mesh:
            psd.append(self.kernel(diameters, weights, dm, self.smoothing))
        
        return psd
    
    # Generates the mesh to be used for the PSD
    def makeMesh(self, num_points, lb, ub):
        
        # Set the lower bound at zero if it's close
        if lb < 1.0:
            lb = 0
        
        # Get the step size
        delta = (ub - lb) / num_points
        
        mesh = []
        for i in range(0, num_points):
            mesh.append(i*delta + lb)
        
        return mesh
    
    # The kernel used (Gaussian default and recommended)
    def kernel(self, diameters, weights, dmesh, h):
        if self.kerneltype == "Gaussian":
            k = 0
            for di, w in zip(diameters, weights):
                ki = w * math.exp(-pow( (dmesh - di)/h, 2.0)/2.0)
                if ki > 1.0e-40:
                    k = k + ki
            k = (1.0/math.sqrt(PI*2.0)) * k / (sum(weights) * h)
            return k
        else:
            print("Unknown kernel specified!")
            return -1
    
    # Return the PSD
    def returnPSD(self):
        return [self.mesh, self.psd]
    
    # Generate the cumulative kernel density function
    def calculateCumulativePSD(self):
        
        # Check that the PSD has already been generated
        if len(self.psd) < 4:
            print("PSD not generated yet!")
        
        # Calculate the CDF
        cdf = [self.psd[0]]
        asum = 0
        
        i = 1
        while i < len(self.psd):
            # Calculate integral element
            dx = 0.5*(self.mesh[i]-self.mesh[i-1])*(self.psd[i]+self.psd[i-1])
            cdf.append(dx + cdf[i-1])
            asum += dx
            i += 1
        
        self.psd_area = asum
        
        return cdf
    

    # Generate statistics about this PSD
    # e.g. d10, d50, dmode, d90 etc
    def calculatePSDStats(self):
        
        if (not hasattr(self, 'cumulative_psd')):
            self.cumulative_psd = self.calculateCumulativePSD()
        
        # Get the d10/d50/d90
        self.d10 = self.findPoint(0.1)
        self.d50 = self.findPoint(0.5)
        self.d90 = self.findPoint(0.9)
        self.dmode = self.getMode()
    
    # Print the statistics about this PSD to console.
    def printPSDStats(self):
        
        print("\tarea:\t{0:.4f}".format(self.psd_area))
        print("\td10:\t{0:.2f} nm".format(self.d10))
        print("\td50:\t{0:.2f} nm".format(self.d50))
        print("\td90:\t{0:.2f} nm".format(self.d90))
        print("\tmode:\t{0:.2f} nm".format(self.dmode))

        
    # Interpolate between points on the cumulative PSD curve
    def interpolate(self, t, dl, du, kl, ku):
    
        dd = du - dl
        dk = ku - kl
        diam = dd * (t - kl) / dk + dl
        
        return diam
    
    def findPoint(self, t):
        # Given a cumulative density 't', return the value of the mesh
        value = -1
        
        i = 0
        while i < len(self.cumulative_psd):
            
            if t == self.cumulative_psd[i]:
                value = self.mesh[i]
            elif (self.cumulative_psd[i-1] < t and self.cumulative_psd[i] > t):
                value = self.interpolate(t, self.mesh[i-1], self.mesh[i], self.cumulative_psd[i-1], self.cumulative_psd[i])
            i += 1
        
        return value
    
   
    def getMode(self):
        # Get the mode of the PSD
        dmax = 0
        imax = 0
        i = 0
        while i < len(self.psd):
            
            if self.psd[i] > dmax:
                dmax = self.psd[i]
                imax = i
            
            i += 1
        
        return self.mesh[imax]

    def calculateEnsembleStats(self, diameters, weights):
        # Generate general statistics about this PSD
        
        self.damean = 0         # arithmetic mean
        self.astdev = 0         # arithmetic stdev
        self.dgmean = 1.0       # geometric mean
        self.gstdev = 1.0       # geometric stdev
        
        # Check for diameters and weights
        if (not (hasattr(self, 'diameters') and hasattr(self, 'weights'))):
            print("No diameters or weights found!")
            raise
        
        asum = 0.0
        gsum = 1.0
        avar = 0.0
        gvar = 1.0
        
        # Calculate scaling factor
        p = (1.0/sum(self.weights))
        
        # First calculate the means...
        for d, w in zip(self.diameters, self.weights):
            asum += (d * w)
            gsum += math.pow(d, w*p)
        
        self.damean = asum / sum(self.weights)
        self.dgmean = gsum
        
        # Now use these to find the stdevs...
        for d, w in zip(self.diameters, self.weights):
            avar += w * math.pow(d - self.damean, 2.0)
            gvar += w * math.pow(math.log(d) - math.log(self.dgmean), 2.0)
        
        self.astdev = math.sqrt(avar / sum(self.weights))
        self.gstdev = math.exp(math.sqrt(gvar / sum(self.weights)))
            
        