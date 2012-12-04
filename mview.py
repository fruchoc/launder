#!/usr/bin/env python

import sys
import getopt

def head():
    print "mview: Copyright William Menz (wjm34) 2012"
    print "A program for viewing the results of MOPS calculations rapidly."

def usage():
    print "Usage:"
    print "-h, --help        print this help message"
    print "-i, --input       postprocess MOPS PSL file"
    print "-k, --key         use header key for postprocessing"
    print "-x, --xml         write postprocessed results to xml file"
    print "-c, --csv         write postprocessed results to csv file"
    print "-g, --gui         activate default GUI"

if __name__ == "__main__":
    head()
    # Set some default constants
    iname   = ""
    ikey    = ""
    csvout  = ""
    xmlout  = ""
    gui     = False
    
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "i:x:c:k:gh",
                                   ["input=,xml=,csv=,key=,gui,help"])
    except getopt.GetoptError:
        usage()
        sys.exit(1)
    
    for opt, arg in opts:
        if opt in ["-h", "--help"]:
            usage()
            sys.exit()
        elif opt in ["-i", "--input"]:
            iname = str(arg)
        elif opt in ["-k", "--key"]:
            ikey = str(arg)
        elif opt in ["-c", "--csv"]:
            csvout = str(arg)
        elif opt in ["-x", "--xml"]:
            xmlout = str(arg)
        elif opt in ["-g", "--gui"]:
            gui = True
        else:
            print "Unrecognised option " + str(opt) + "."
            sys.exit(1)
    
    # Start main program
    
    # Has iname been specified?
    if iname:
        
        if csvout or xmlout:
            print "Running command-line options."
            # Check that a key has first been specified
            if not ikey:
                raise KeyError("No key for postprocessing specified.")
            
            import structure.lparser
            import structure.core
            
            # Try to load this as a MOPS PSL file.
            if structure.lparser.examine_filetype(iname) == "psl":
                p = structure.lparser.PSLParser(iname)
                dat = p.get()
                
                # Turn this into an ensemble object
                e = structure.core.Ensemble(iname, dat["data"])
                e.kernel_density(ikey)
                
                # Write to csv
                if csvout:
                    p = structure.lparser.DSVWriter(csvout)
                    p.write_series(e.pdf_as_series(0))
                    p.close()
                
                # Write to xml
                if xmlout:
                    p = structure.lparser.XMLWriter(xmlout)
                    p.write_ensemble_stats(e)
                    p.close()
            else:
                print "Not a PSL file. Not even going to try."
                
        
        if gui:
            print "Running matplotlib GUI."
            import gui.mpl
            
            m = gui.mpl.MPL(iname)
    else:
        # iname not specified: load GTK gui by default.
        print "Loading GTK GUI."
        import gui.mgtk
        
        m = gui.mgtk.MView()
        m.main()

print("Goodbye.")