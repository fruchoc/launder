#!/usr/bin/env python

import sys
import getopt
import os
import re
import glob

class Constants:
# Enum-like class to hold various constants
    f_psl    = 0
    f_rates  = 1
    f_chem   = 2
    f_part   = 3
    f_grates = 4
    
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
    d_imp   = 4
    
    # Terminal colours
    tcHEADER = '\033[95m'
    tcOKBLUE = '\033[94m'
    tcOKGREEN = '\033[92m'
    tcWARNING = '\033[93m'
    tcFAIL = '\033[91m'
    tcENDC = '\033[0m'

    def disable(self):
        self.tcHEADER = ''
        self.tcOKBLUE = ''
        self.tcOKGREEN = ''
        self.tcWARNING = ''
        self.tcFAIL = ''
        self.tcENDC = ''

    
    def matchDiam(self, i):
        if i == 0: return "Spherical"
        elif i == 1: return "Mobility"
        elif i == 2: return "Collision"
        elif i == 3: return "Primary"
        elif i == 4: return "Imported"
        else: return "ERROR"
        
    def checkForKnownFile(self, fname):
        # Checks that the filename is of a known type, returns the type
        if re.search("-psl", fname): return self.f_psl
        elif re.search("-chem.csv", fname): return self.f_chem
        elif re.search("-part-rates.csv", fname): return self.f_rates
        elif re.search("-part.csv", fname): return self.f_part
        elif re.search("-gp-rates.csv", fname): return self.f_grates
        else: return -1

def autoFind():
    # Function to automatically find the most recent PSL file for
    # postprocessing (useful for MoDS)
    psllist  = glob.glob("*psl*.csv")
    psltimes = []
    
    if len(psllist) > 0:
        for psl in psllist:
            psltimes.append(pslTime(psl))
        index = psltimes.index(max(psltimes))
        print(str(len(psllist)) + " PSLs found. Using file " + psllist[index])
        return psllist[index]
    else:
        print("No PSL files found.")
        return None
    
def pslTime(fname):
    # Parses the time of PSL file.
    foo = fname.split("(")
    foo = foo[1].split(")")
    foo = foo[0].split("s")
    foo = float(foo[0].strip())
    return(foo)

def head():
    print("Launder GTK+")
    print("(c) William Menz (wjm34) 2012")

def usage():
    print("\nUSAGE:")
    print("(none)            load GUI")
    print("-a                automagically find PSL file in directory")
    print("-d <arg>          change to directory")
    print("-h, --help        print usage")
    print("-i, --input <arg> postprocess specific file")
    print("-x, --xml <arg>   write statistics to XML file")
    print("-p, --psd <arg>   write PSDs from a PSL file (CSV format)")
    print("-t, --time <arg>  write stats from a trajectory to XML file at time given")
    print("                  (default end time of simulation)")

if __name__ == "__main__":
    head()
    exitVal  = 0    # value to exit program with
    
    # Will load the GUI if this is true
    guiMode  = True
    xmlOut   = False
    psdOut   = False
    timeOut  = None
    
    try:
        opts, args = getopt.getopt(sys.argv[1:],\
                                   "ahd:i:p:t:x:",\
                                   ["auto", "help", "input=", "psd=", "time=",\
                                     "xml="]) 
    except getopt.GetoptError:
        usage()
        sys.exit(1)
    
    for opt, arg in opts:
        if opt in ["-h", "--help"]:      
            usage()
            sys.exit()
        elif opt in ["-a", "--auto"]:
            fname = autoFind()
            if fname == None: sys.exit(1)
            guiMode = False
        elif opt == "-d":
            rundir = arg
            print("Changing to directory {0}.".format(rundir))
            os.chdir(rundir)
        elif opt in ["-i", "--input"]:
            fname = arg
            guiMode = False
        elif opt in ["-p", "--psd"]:
            psdOut   = str(arg)
        elif opt in ["-t", "--time"]:
            try:
                timeOut  = float(arg)
            except:
                print(Constants.tcWARNING + \
                      "Couldn't get trajectory time, using final time." + 
                      Constants.tcENDC)
                timeOut = None
        elif opt in ["-x", "--xml"]:
            xmlOut   = str(arg)
        else:
            print("Unrecognised option {0}".format(opt))
            usage()
            exitVal = 1
        
    if guiMode:
        
        if xmlOut: print("Warning: XML out unsupported in GUI mode.")
        if psdOut: print("Warning: PSD out unsupported in GUI mode.")
        
        # Import panes
        try:
            import program.panes as Panes
        except:
            print(Constants.tcFAIL + "Couldn't find data model files!" + \
                  Constants.tcENDC)
            exitVal = 2
        
        app = Panes.App(Constants())
        app.main()
    else:
        print("Entering non-GUI mode.")
        
        # Import commands
        try:
            import program.command as Cmd
        except:
            print(Constants.tcFAIL + "Couldn't find data model files!" + \
                  Constants.tcENDC)
            exitVal = 3
        
        consts = Constants()
        ftype = consts.checkForKnownFile(fname)
        print("Postprocessing file {0}.".format(fname))
        if ftype == consts.f_psl:
            if (not xmlOut) and (not psdOut):
                print(consts.tcWARNING + \
                      "Warning: no output file specified." + \
                      consts.tcENDC)
            if timeOut:
                print(consts.tcWARNING + \
                      "Warning: time argument has no effect for PSL processing." + \
                      consts.tcENDC)
            
            cmd = Cmd.PSLCommand(fname, consts)
            cmd.start()
            
            if cmd.m_allowOutput:
                if xmlOut: cmd.writeXML(xmlOut)
                if psdOut: cmd.writePSDs(psdOut, ",")
            else:
                print(consts.tcFAIL + "No ensembles could be loaded." + \
                      consts.tcENDC)
                exitVal = 4
            
        elif ftype == consts.f_chem or \
                ftype == consts.f_part or \
                ftype == consts.f_rates or \
                ftype == consts.f_grates:
            if not xmlOut:
                print(consts.tcWARNING + \
                      "Warning: no output file specified." + 
                      consts.tcENDC)
            if psdOut:
                print(consts.tcWARNING + \
                      "Warning: PSD out argument has no effect in trajectory mode." + \
                      consts.tcENDC)
            
            cmd = Cmd.TrajectoryCommand(fname, consts)
            cmd.start()
            
            if xmlOut: cmd.writeXML(xmlOut, timeOut)
            
        else:
            print(consts.tcFAIL + \
                  "Unrecognised file type input." + 
                  consts.tcENDC)
            exitVal = 5
    
if exitVal > 0:
    print(Constants.tcFAIL + "Goodbye!" + Constants.tcENDC)
else:
    print(Constants.tcOKGREEN + "Goodbye!" + Constants.tcENDC)
sys.exit(exitVal)