"""
dialogs.py
Dialog boxes used to communicate information in the GUI.
(c) William Menz (wjm34) 2012
"""

import os

try:
    import pygtk
    pygtk.require('2.0')
    import gtk
except:
    print("Couldn't find pygtk or gtk.")
    sys.exit(1)

# Other libraries
try:
    import datamodel.mops_parser as MParser
    import datamodel.series as Series
    import datamodel.ensemble as Ensemble
    import program.command as Cmd
except:
    print("Couldn't find other sources for " + os.path.abspath( __file__ ))
    sys.exit(4)

class LoadCSVDialog:
    # Class for loading relevant MOPS csv files into the system.
    def destroy(self, widget, data=None):
        self.m_window.destroy()
        return self.m_results
    
    def __init__(self, fname, consts, filetype):
        self.m_fname = fname    # Name of file to load
        self.m_ftype = filetype # Type of file to load
        self.m_types = consts
        self.m_results = []     # To be returned by the destroy()
        
        # Initialise a new window
        self.m_window = gtk.Window()
        self.m_window.connect("destroy", self.destroy)
        self.m_window.set_default_size(300,300)
        self.m_window.set_title("Load {0}".format(self.m_fname))
        
        # Initialise a HBox for some padding
        self.m_hbox = gtk.HBox(homogeneous=False)
        self.m_window.add(self.m_hbox)
        
        # Initialise the main VBox for the system
        self.m_vbox = gtk.VBox(homogeneous=False)
        self.m_hbox.pack_start(self.m_vbox, \
                                    padding = self.m_types.m_pad)
        
        # Add some text explaining what to do
        label1 = gtk.Label("Select the trajectories to load.")
        self.m_vbox.pack_start(label1,  expand=False, \
                                    padding = self.m_types.m_pad)
        
        # Generate the of trajectories
        self.makeTreeView()
        
        # Initialise a HBox and the buttons
        self.m_b_hbox          = gtk.HBox(homogeneous=True)
        self.m_b_load_selected = gtk.Button("Load selected")
        self.m_b_load_selected.connect("clicked", self.getSelectedTrajectories, )
        self.m_b_load_all      = gtk.Button("Load all")
        self.m_b_load_all.connect("clicked", self.getAllTrajectories, )
        self.m_b_hbox.pack_start(self.m_b_load_selected, expand=False,  \
                                    padding = self.m_types.m_pad)
        self.m_b_hbox.pack_start(self.m_b_load_all, expand=False,  \
                                    padding = self.m_types.m_pad)
        self.m_vbox.pack_start(self.m_b_hbox, fill=False, expand=False,  \
                                    padding = self.m_types.m_pad)
        
        # Show window
        self.m_window.show_all()
    
    def makeTreeView(self):
        # Makes the list view showing all series in the file
        headerparser = MParser.HeaderParser(self.m_fname)
        data = headerparser.getHeaders()
        if (data == None):
            print("No data found in file.")
            self.destroy(None, None)
        else:
            
            # Create the list store
            self.m_l_store = gtk.ListStore(type("str"))
            for item in data:
                self.m_l_store.append((item,))
    
            self.m_l_view = gtk.TreeView()
            self.m_l_view.set_model(self.m_l_store)
            
            col  = gtk.TreeViewColumn()
            cell = gtk.CellRendererText()
            col.pack_start(cell)
            col.add_attribute(cell, "text", 0)
            self.m_l_view.append_column(col)
            
            # Turn off headers
            self.m_l_view.set_headers_visible(False)
            self.m_l_view.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
    
            
            # Create the scrolled view
            scroller = gtk.ScrolledWindow()
            scroller.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
            scroller.set_shadow_type(gtk.SHADOW_IN)
            scroller.add_with_viewport(self.m_l_view)
            
            self.m_vbox.pack_start(scroller, expand=True, fill=True,  \
                                    padding = self.m_types.m_pad)
    
    def getSelectedTrajectories(self, widget, data=None):
        # Returns a list of the indicies of the trajectories of interest
        
        # Initialise blank array
        indices = []
        
        selection = self.m_l_view.get_selection()
        if selection != None:
            (model, pathlist) = selection.get_selected_rows()
        
            for path in pathlist:
                indices.append(path[0])
        else:
            print("Nothing selected!") 
        
        # Set the selections to be accessed by the destructor
        self.m_results = indices
        
        self.destroy(None, None)
    
    def getAllTrajectories(self, widget, data=None):   
        indices = range(0, len(self.m_l_store))
        
        # Set the selections to be accessed by the destructor
        self.m_results = indices
        
        self.destroy(None, None)

class LoadMiscFileDialog:
    # Class for loading a miscellaneous DSV type file
    
    def destroy(self, widget, data=None):
        self.m_window.destroy()
    
    def __init__(self, pane, consts):
        self.chooseFile(None, None)
        self.m_results = []     # To be returned by the destroy()
        self.m_pane    = pane
        self.m_consts  = consts
        
        # Initialise a new window
        self.m_window = gtk.Window()
        self.m_window.connect("destroy", self.destroy)
        #self.m_window.set_default_size(300,300)
        self.m_window.set_title("Load {0}".format(self.m_fname))
        
        # Initialise a HBox for some padding
        hbox = gtk.HBox(homogeneous=False)
        self.m_window.add(hbox)
        
        # Initialise the main VBox for the system
        vbox = gtk.VBox(homogeneous=False)
        hbox.pack_start(vbox, padding = self.m_consts.m_pad)
        
        label        = gtk.Label("DSV file properties")
        vbox.pack_start(label)
        
        # Create a field for the delimiter
        self.m_entry = gtk.Entry(5)
        label        = gtk.Label("Delimiter: ")
        hbox1        = gtk.HBox(homogeneous=False)
        hbox1.pack_start(label, padding = self.m_consts.m_pad)
        hbox1.pack_start(self.m_entry, padding = self.m_consts.m_pad)
        vbox.pack_start(hbox1)
        
        # Create the load button
        button       = gtk.Button("Load file")
        button.connect("clicked", self.loadFile, None)
        vbox.pack_start(button, padding = self.m_consts.m_pad)
        
        self.m_window.show_all()
        
    def chooseFile(self, widget, data=None):
        # Check PyGTK version
        if gtk.pygtk_version < (2,3,90):
           print("PyGtk 2.3.90 or later required!")
           raise SystemExit
        
        dialog = gtk.FileChooserDialog("Select file or path..",
                               None,
                               gtk.FILE_CHOOSER_ACTION_OPEN,
                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        
        # Allow multiple files to be selected
        dialog.set_select_multiple(False)
        
        # Add file filters to dialog
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        dialog.add_filter(filter)
        
        # Now run the chooser!
        fname = dialog.run()
        
        # Check the response
        if fname == gtk.RESPONSE_OK:
            self.m_fname = dialog.get_filename()
        elif fname == gtk.RESPONSE_CANCEL:
            print 'Closed, no files selected'
        dialog.destroy()
    
    def getDelimiter(self):
        text = self.m_entry.get_text()
        if text == "\t":
            text = "tab"
        elif text == "":
            text = "tab"
        return text
    
    def loadFile(self, widget, data=None):
        # Attempts to load and parse the selected file
        parser = MParser.MiscFileParser(self.m_fname)
        results = parser.start(self.getDelimiter(), self.m_pane.m_sType, self.m_consts)

        if len(results) > 0:
            self.m_pane.addSeries(results)
        else:
            print("Error getting series from the parser.")
        
        self.destroy(None, None)



class LoadPSLDialog:
    # Class for loading MOPS PSL files.
    
    def destroy(self, widget, data=None):
        self.m_window.destroy()
    
    def __init__(self, fname, psdpane, consts):
        self.m_fname = fname    # Name of file to load
        self.m_pane = psdpane   # Reference of PSD pane
        self.m_results = []     # To be returned by the destroy()
        self.m_consts  = consts # Reference to contants
        
        # Initialise a new window
        self.m_window = gtk.Window()
        self.m_window.connect("destroy", self.destroy, )
        self.m_window.set_default_size(300,200)
        self.m_window.set_title("Load {0}".format(self.m_fname))
        
        # Initialise a HBox for some padding
        hbox = gtk.HBox(homogeneous=False)
        self.m_window.add(hbox)
        
        # Initialise the main VBox for the system
        self.m_vbox = gtk.VBox(homogeneous=False)
        hbox.pack_start(self.m_vbox, \
                                    padding = self.m_consts.m_pad)
        
        # Add some text explaining what to do
        label1 = gtk.Label("Select the diameter types to load.")
        self.m_vbox.pack_start(label1,  expand=False, \
                                    padding = self.m_consts.m_pad)
        
        self.generateDiamEntries()
        
        self.m_loadSelected = gtk.Button("Load selected")
        self.m_loadSelected.connect("clicked", self.loadSelected, None)
        self.m_vbox.pack_start(self.m_loadSelected, \
                               expand=False, fill=False, padding=2)

        # Show window
        self.m_window.show_all()
    
    def loadSelected(self, widget, data=None):
        # Load the selected series
        
        # First identify which entries are selected.
        results = []
        i = 0
        for button, entry in zip(self.m_dCheck, self.m_dHEntry):
            if button.get_active():
                active = self.m_cols[i]
                active += [self.getH(entry, None)]
                results.append(active)
            i += 1
        
        # Data passed to the PSL parser has the form:
        # [[Const id, Column id, bandwidth], ..]
        # Note -1 bandwidth gives automatic calculation.
        
        if len(results) < 1: 
            print("Nothing selected!")
        else:
            # Now need to parser the file and get the relevant series
            parser = MParser.PSLParser(self.m_fname)
            parsed = parser.start(results)
            
            if len(parsed) < 1:
                print("Failure trying to get parsed data.")
                self.destroy(None, None)
             
            # Call the ensemble object to create ensembles
            allseries = []
            for sets in parsed[1:]:
                ens = Ensemble.KernelDensity(sets[2], parsed[0], sets[1])
                
                if len(ens.diameters) > 0:
                    
                    series = Series.PSD(self.m_consts.matchDiam(sets[0]), ens.mesh,\
                                            ens.psd)
                    series.setH(ens.smoothing)
                    series.setParent(self.m_fname)
                    series.setType(sets[0], self.m_consts)
                    allseries.append(series)
            
            # Now send the series to the plotpane!
            if len(allseries) > 0:
                self.m_pane.addSeries(allseries)
            
            # Kill the window now
            self.destroy(None, None)
        
    
    def generateDiamEntries(self):
        # Calls the parser to see which diameter types are present
        # adds their entry to the load pane
        
        parser = MParser.PSLHeaderParser(self.m_fname)
        line = parser.getHeaders()
        if line != None:
            self.m_cols = parser.scanForDiameters(line, self.m_consts)
        
        self.m_dHEntry = []
        self.m_dCheck  = []
        
        for item in self.m_cols:
            dtype = item[0]
            colid = item[1]
            
            if colid > 0:
                hbox = self.makeDiamEntry(dtype)
                self.m_vbox.pack_start(hbox, expand=False,
                                       padding=self.m_consts.m_pad)
        
        del parser
    
    def makeDiamEntry(self, dtype):
        
        hbox = gtk.HBox(homogeneous=False)
        label = gtk.Label(self.m_consts.matchDiam(dtype) + " diameter")
        hbox.pack_start(label)
        
        label = gtk.Label("h:")
        entry = gtk.Entry(6)
        entry.set_text("auto")
        entry.set_width_chars(6)
        hbox.pack_start(label, expand=False)
        hbox.pack_start(entry, expand=False, padding=5)
        
        label = gtk.Label("load?")
        check = gtk.CheckButton()
        if (dtype == self.m_consts.d_mob or dtype == self.m_consts.d_sph):
            check.set_active(False)
        else:
            check.set_active(True)
        hbox.pack_start(label, expand=False)
        hbox.pack_start(check, expand=False)
        
        # Store useful variables in lists
        self.m_dHEntry.append(entry)
        self.m_dCheck.append(check)
        
        return hbox
    
    def getH(self, widget, data=None):
        # Gets the scaling factor from a widget
        h = -1
        text = widget.get_text()
        if (text == "auto" or text == "*" or \
            text == "def"): h = -1
        else:
            try:
                h = float(text)
            except:
                h = -1
        return h

class GetStatsDialog:
    """
    Dialog box giving the XML output of a given input file, just
    as if the program was called via command line interface
    """
    
    def destroy(self, widget, data=None):
        self.m_window.destroy()
    
    def __init__(self, fname, consts):
        
        self.m_fname = fname    # Name of file to load
        self.m_consts  = consts # Reference to contants
        
        # Initialise a new window
        self.m_window = gtk.Window()
        self.m_window.connect("destroy", self.destroy, )
        self.m_window.set_default_size(400,300)
        self.m_window.set_title("Stats of {0}".format(self.m_fname))
        
        # Initialise a HBox for some padding
        hbox = gtk.HBox(homogeneous=False)
        self.m_window.add(hbox)
        
        # Initialise the main VBox for the system
        self.m_vbox = gtk.VBox(homogeneous=False)
        hbox.pack_start(self.m_vbox, \
                                    padding = self.m_consts.m_pad)
        
        
        # Add some text explaining what to do
        label1 = gtk.Label("XML output")
        hbox = gtk.HBox(homogeneous=False)
        self.m_vbox.pack_start(hbox,  expand=False, \
                                    padding = self.m_consts.m_pad)
        hbox.pack_start(label1)
        
        # Add the button to save a file
        button = gtk.Button("Save file")
        button.connect("clicked", self.saveFile, None)
        hbox.pack_start(button, expand=False, fill=False)
        
        self.m_data = self.getLabelText(self.m_fname)
        text  = gtk.Label(self.m_data)
        text.set_selectable(True)
        text.set_line_wrap_mode(True)
        text.set_justify(gtk.JUSTIFY_LEFT)
        
        scroller = gtk.ScrolledWindow()
        scroller.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        scroller.set_shadow_type(gtk.SHADOW_IN)
        scroller.add_with_viewport(text)
        
        self.m_vbox.pack_start(scroller, expand=True, fill=True, \
                               padding = self.m_consts.m_pad)
        
        self.m_window.show_all()

    def getLabelText(self, fname):
        # Gets the XML-formatted text for the label.
        ftype = self.m_consts.checkForKnownFile(fname)
        if ftype == self.m_consts.f_psl:
            cmd = Cmd.PSLCommand(fname, self.m_consts)
            cmd.start()
            
            parser = cmd.writeXML(None)
            
        elif ftype == self.m_consts.f_chem or \
                ftype == self.m_consts.f_part or \
                ftype == self.m_consts.f_rates:
            cmd = Cmd.TrajectoryCommand(fname, self.m_consts)
            cmd.start()
            
            parser = cmd.writeXML(None)
        
        data = parser.getData()
        del parser
        del cmd
        
        return data
    
    def saveFile(self, widget, data=None):
        fname = self.chooseFile()
        
        if fname != None:
            print("File {0} saved.".format(fname))
            fstr = open(fname, 'w')
            fstr.write(self.m_data)
            fstr.close()
    
    def chooseFile(self):
        # Check PyGTK version
        if gtk.pygtk_version < (2,3,90):
           print("PyGtk 2.3.90 or later required!")
           raise SystemExit
        
        dialog = gtk.FileChooserDialog("Select file or path..",
                               None,
                               gtk.FILE_CHOOSER_ACTION_SAVE,
                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        
        # Allow multiple files to be selected
        dialog.set_select_multiple(False)
        
        # Add file filters to dialog
        filter = gtk.FileFilter()
        filter.set_name("XML files")
        filter.add_pattern("*.xml")
        dialog.add_filter(filter)
        
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        dialog.add_filter(filter)
        
        # Now run the chooser!
        fname = dialog.run()
        
        # Check the response
        if fname == gtk.RESPONSE_OK:
            filename = dialog.get_filename()
        elif fname == gtk.RESPONSE_CANCEL:
            print 'Closed, no files selected'
            filename = None
        
        dialog.destroy()
        
        return filename