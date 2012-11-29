import sys

import structure.lparser
import structure.core

# Requires matplotlib v1.0+
try:
    import matplotlib.pyplot as plt
except:
    print "Could not find matplotlib dependencies."

class MPL:
    # MPL defines a class which is used for primitive command-line interaction
    # with DSV files. It allows the user to plot a series directly from the
    # command-line. This is advantageous when GTK is not available.
    def __init__(self, fname):
        self.fname  = fname
        self.fig    = plt.figure()
        self.ax     = self.fig.add_subplot(111)
        self.loopfn = None
        self.lines  = []
        self.shown  = False
        
        # Enable interactive mode.
        plt.ion()
        
        s = structure.lparser.examine_filetype(fname)
        if s == "psl":
            # Check if it's a MOPS PSL file
            print "MOPS PSL file found."
            self.loopfn = self.psl
            self.plot_series(self.psl())
        elif s == "part":
            # Is it a MOPS -part etc CSV file?
            print "MOPS trajectory output file found."
            self.loopfn = self.part
            self.plot_series(self.part())
        else:
            # It's probably just a normal CSV file
            print "Unsupported."
    
    def __get_answer(self, minval, maxval):
        # Returns an answer
        sys.stdout.write("Enter a number for your answer: ")
        ans = sys.stdin.readline()
        try:
            ians = int(ans)
        except:
            if str(ans).strip() == "q": sys.exit()
            print "Must have an integer value (q for quit)."
            ians = self.__get_answer(minval, maxval)
        
        if ians > maxval or ians < minval:
            print "Must be between " + str(minval) + " and " + str(maxval) \
                    + " (q for quit)."
            ians = self.__get_answer(minval, maxval)
        return ians
    
    def __get_choice(self, question, opts):
        # List options and get an answer
        print question
        for i in range(0, len(opts)):
            print str(i) + ": " + str(opts[i])
        a = self.__get_answer(0, len(opts)-1)
        print ""
        return a
    
    def psl(self):
        # Do stuff with a PSL file.
        p = structure.lparser.PSLParser(self.fname)
        dat = p.get()
        e = structure.core.Ensemble(self.fname, dat["data"])
        keys = dat["keys"]
        
        # With the core objects initialised, generate stats
        i = self.__get_choice("Which parameter is to be analysed?", keys)
        e.kernel_density(keys[i])
        
        # Plot pdf or cdf?
        i = self.__get_choice("Plot PDF or CDF?", ["PDF (PSD)", "CDF"])
        if i == 0:
            s = e.pdf_as_series(0)
        if i == 1:
            s = e.cdf_as_series(0)
        
        return s
    
    def part(self):
        # Do stuff with mops -chem or -part.csv etc files.
        p = structure.lparser.PartParser(self.fname)
        # Get a dictionary of lists
        dat = p.get()
        
        # Load the data into a MOPS Trajectories object
        mtrj = structure.core.MOPSTrajectories(self.fname, dat)
        keys = mtrj.get_keys()
        
        # Plot something?
        ki = keys[self.__get_choice("Plot which parameter?", keys)]
        return mtrj.get_series("Time (s)", ki)
    
    def plot_series(self, series):
        # Plot a series object
        if not self.shown:
            print "Creating canvas."
            plt.show()
            self.shown = True
        else:
            # Ask if we want to replot or start a new one
            i = self.__get_choice("Start new clean plot or use old one?", 
                              ["Clean plot", "Use old canvas"])
            if i == 0:
                plt.cla()
        
        l = self.ax.plot(series.axes_values("x"), series.axes_values("y"),
                         label=series.name)
        self.ax.set_xlabel(series.axes_name("x"))
        self.ax.set_ylabel(series.axes_name("y"))
        try:
            # Try to use best positioning
            self.ax.legend(loc=0)
        except:
            self.ax.legend()
        plt.draw()
        
        self.plot_series(self.loopfn())