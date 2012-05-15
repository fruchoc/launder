#!/usr/bin/env python

import sys
import getopt
import os
import re

class Constants:
# Enum-like class to hold various constants
    f_psl    = 0
    f_rates  = 1
    f_chem   = 2
    f_part   = 3
    
    # Global padding declarations
    m_pad     = 5
    
    # Window size request declarations
    x_main      = 1080
    y_main      = 650
    
    # Listview default
    x_lv        = int(x_main * 0.3)
    y_lv        = int(y_main * 0.3)
    
    # diameter types
    d_sph   = 0
    d_mob   = 1
    d_col   = 2
    d_pri   = 3
    
    def matchDiam(self, i):
        if i == 0: return "Spherical"
        elif i == 1: return "Mobility"
        elif i == 2: return "Collision"
        elif i == 3: return "Primary"
        else: return "ERROR"
        
    def checkForKnownFile(self, fname):
        # Checks that the filename is of a known type, returns the type
        if re.search("-psl", fname): return self.f_psl
        elif re.search("-chem.csv", fname): return self.f_chem
        elif re.search("-part-rates.csv", fname): return self.f_rates
        elif re.search("-part.csv", fname): return self.f_part
        else: return -1

def head():
    print("Launder GTK+")
    print("(c) William Menz (wjm34) 2012")

def usage():
    print("\nUSAGE:")
    print("(none)            load GUI")
    print("-d <arg>          change to directory")
    print("-h, --help        print usage")
    print("-i, --input <arg> postprocess specific file")
    print("-x, --xml <arg>   write statistics to XML file")

if __name__ == "__main__":
    head()
    # Will load the GUI if this is true
    guiMode  = True
    xmlOut   = False
    
    try:
        opts, args = getopt.getopt(sys.argv[1:],\
                                   "hd:p:i:x:",\
                                   ["help", "input=", "xml="]) 
    except getopt.GetoptError:
        usage()
        sys.exit(1)
    for opt, arg in opts:
        if opt in ["-h", "--help"]:      
            usage()
            sys.exit()
        elif opt == "-d":
            rundir = arg
            print("Changing to directory {0}.".format(rundir))
            os.chdir(rundir)
        elif opt in ["-i", "--input"]:
            fname = arg
            print("Postprocessing file {0}.".format(fname))
            guiMode = False
        elif opt in ["-x", "--xml"]:
            xmlOut   = str(arg)
        else:
            usage()
            sys.exit(2)
        
    if guiMode:
        
        if xmlOut: print("Warning: XML out unsupported in GUI mode.")
        
        # Import panes
        try:
            import program.panes as Panes
        except:
            print("Couldn't find data model files!")
            sys.exit(4)
        
        app = Panes.App(Constants())
        app.main()
    else:
        print("Entering non-GUI mode.")
        
        # Import commands
        try:
            import program.command as Cmd
        except:
            print("Couldn't find data model files!")
            sys.exit(4)
        
        consts = Constants()
        ftype = consts.checkForKnownFile(fname)
        if ftype == consts.f_psl:
            cmd = Cmd.PSLCommand(fname, consts)
            cmd.start()
            
            if xmlOut: cmd.writeXML(xmlOut)
            
        elif ftype == consts.f_chem or \
                ftype == consts.f_part or \
                ftype == consts.f_rates:
            cmd = Cmd.TrajectoryCommand(fname, consts)
            cmd.start()
            
            if xmlOut: cmd.writeXML(xmlOut)
            
        else:
            print("Unrecognised file type input.")
    

print "Goodbye!"
