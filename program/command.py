"""
command.py
Source for dealing with the command-line interface of the postprocessor
(c) William Menz (wjm34) 2012
"""

import sys
import datamodel.mops_parser as MParser
import datamodel.ensemble as Ensemble
import program.output as Out
 
class Command:
    
    def __init__(self, fname, consts):
        
        self.m_fname  = fname       # filename to be processed
        self.m_consts = consts      # reference to Constants
        
        
class PSLCommand(Command):
    # Command-line interface for postprocessing PSL files
    
    def start(self):
        # Initialise output writing
        self.m_allowOutput = True
        
        
        # Parse the headers to see what is there!
        parser = MParser.PSLHeaderParser(self.m_fname)
        line = parser.getHeaders()
        if line != None:
            parseddata = parser.scanForDiameters(line, self.m_consts)
            self.m_parseddata = []
            # Hide zero col id entries (i.e. not found in PSL) from the parser
            for data in parseddata:
                if data[1] != 0: self.m_parseddata.append(data)
        else:
            print(self.m_consts.tcFAIL + \
                  "Couldn't parse headers" + \
                  self.m_consts.tcENDC)
            sys.exit(1)
        
        procdata = []
        for data in self.m_parseddata:
            if data[1] != 0:
                print(self.m_consts.tcOKGREEN + \
                      "Found diameter type "+self.m_consts.matchDiam(data[0]) + \
                      self.m_consts.tcENDC)
                # Append -1 to indicate automatic calculation of bandwidth
                procdata.append(data + [-1])
        
        parser = MParser.PSLParser(self.m_fname)
        parsed = parser.start(procdata)
        
        if len(parsed) < 1:
            print(self.m_consts.tcFAIL + \
                  "Failed trying to get parsed data" + \
                  self.m_consts.tcENDC)
            sys.exit(1)
        
        self.m_ensembles = []
        for sets in parsed[1:]:
            ens = Ensemble.KernelDensity(sets[2], parsed[0], sets[1])
            if len(ens.diameters) > 0:
                ens.calculateCumulativePSD()
                ens.calculatePSDStats()
                self.m_ensembles.append(ens)
        
        if len(self.m_ensembles) < 1:
            # Block output if there were no ensembles added.
            self.m_allowOutput = False
        
    def writeXML(self, oname):
        # Write the ensembles to XML!
        parser = Out.XMLOut(oname)
        
        # Write XML preamble
        parser.head()
        
        if len(self.m_ensembles) != len(self.m_parseddata):
            print(self.m_consts.tcFAIL + \
                  "Segmentation of ensembles and parsed data." + \
                  self.m_consts.tcENDC)
            sys.exit(1)
        
        parser.write1("output", [])
        
        # Write the file characteristics
        parser.write1("file", [["name", self.m_fname]], 1, "/")
        
        # Write the ensembles
        for data, ens in zip(self.m_parseddata, self.m_ensembles):
            parser.write1("psl", [["type", self.m_consts.matchDiam(data[0])]], 1)
            
            parser.write2("amean", ens.damean, 2)
            parser.write2("gmean", ens.dgmean, 2)
            parser.write2("astdev", ens.astdev, 2)
            parser.write2("gstdev", ens.gstdev, 2)
            
            # Write PSD diagnostics
            parser.write1("psd", [["points", ens.num_points], ["bandwidth", ens.smoothing], ["area", ens.psd_area]], 2)
            
            parser.write2("d10", ens.d10, 3)
            parser.write2("d50", ens.d50, 3)
            parser.write2("d90", ens.d90, 3)
            parser.write2("dmode", ens.dmode, 3)
            
            parser.write1("/psd", [], 2)
            
            parser.write1("/psl", [], 1)
        
        parser.write1("/output", [])
        
        parser.close()
        
        return parser
    
    def writePSDs(self, oname, delimiter=","):
        # Writes all PSDs for a given file
        # One file per PSD.
        
        for data, ens in zip(self.m_parseddata, self.m_ensembles):
            fname = self.fileName(oname, self.m_consts.matchDiam(data[0]))
            self.writePSD(fname, ens, delimiter)
    
    def fileName(self, oname, ftype):
        # Generates a filename of the form oname.ftype.ext
        splitted = oname.split(".")
        string = oname
        if len(splitted) > 1:
            f = splitted[0]
            b = splitted[1:]
            string = f
            string += "." + ftype.lower()
            for i in b:
                string += "." + i
        else:
            string = oname
            string += "." + ftype.lower()
        return string
    
    def writePSD(self, oname, ensemble, delimiter=","):
        # Writes a PSD as a DSV file. Only writes one at a time in case
        # different meshes are used.
        
        parser = Out.DSVOut(oname)
        
        parser.head(["diameter", "density", "cumulative"], delimiter)
        
        for d, r, c in zip(ensemble.mesh, ensemble.psd, \
                           ensemble.cumulative_psd):
            parser.write([d, r, c], delimiter, None)
        
        parser.close()
        return parser

class TrajectoryCommand(Command):
    # Parses trajectories and writes to a file
    
    m_rtol  = 1.0e-6    # relative tolerance for getting time
 
    def start(self):
        # Parse the headers to see what is there!
        parser = MParser.HeaderParser(self.m_fname)
        self.m_headers = parser.getHeaders()
        
        if self.m_headers == None:
            print(self.m_consts.tcFAIL + \
                  "Couldn't parse headers" + \
                  self.m_consts.tcENDC)
            sys.exit(1)
        
        parser = MParser.TrajectoryParser(self.m_fname)
        self.m_allseries = parser.start(range(0, len(self.m_headers)))
    
    def splitHeader(self, entry):
        # Splits Header (unit) into [Header, unit]
        if not ("(" in entry):
            return [entry, "-"]
        
        head, text = entry.split("(")
        unit = text.split(")")[0]
        return [head, unit]
        
    
    def writeXML(self, oname, time=None):
        # Write the trajectory to XML. Default is to write at the final time.
        parser = Out.XMLOut(oname)
        
        # Write XML preamble
        parser.head()
        parser.write1("output", [])
        
        # Write the file characteristics
        parser.write1("file", [["name", self.m_fname], \
                               ["time", self.m_allseries[0].getXatX(time, self.m_rtol)]], 1, "/")
        
        # Write the series
        for series in self.m_allseries:
            val = series.getYatX(time, self.m_rtol)
            err = series.getEatX(time, self.m_rtol)
            
            unit = series.m_unit
            mult = 1.0
            if unit == "m":
                unit = "nm"
                mult = 1.0e9
            
            parser.write1("stat", [["name", series.m_name], ["unit", unit]], 1)
            parser.write2("mean", val*mult, 2)
            parser.write2("ci", err*mult, 2)
            parser.write2("upper", (val+err)*mult, 2)
            parser.write2("lower", max(val-err,0.0)*mult, 2)
            parser.write1("/stat", [], 1)
        parser.write1("/output", [])
        
        parser.close()
        
        return parser
