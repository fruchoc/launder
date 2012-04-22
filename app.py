#!/usr/bin/env python

import sys
import glob
import re

# Import pygtk and gtk packages.
# obtain for any platform at http://www.pygtk.org
try:
    import pygtk
    pygtk.require('2.0')
    import gtk
except:
    print("Couldn't find pygtk or gtk.")
    sys.exit(1)

# Import key matplotlib objects
# obtain at http://sourceforge.net/projects/matplotlib/
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_gtkagg \
        import FigureCanvasGTKAgg as FigureCanvas
    from matplotlib.backends.backend_gtkagg \
        import NavigationToolbar2GTKAgg as NavToolbar
except:
    print("Couldn't find matplotlib dependencies.")
    sys.exit(2)

# Import data model files
try:
    import datamodel.mops_parser as MParser
    import datamodel.series as Series
except:
    print("Couldn't find data model files!")
    sys.exit(4)

class App:
    def __init__(self):
        
        # Create main window
        self.m_window_main = gtk.Window()
        
        # Initialise and connect signals
        self.m_window_main.connect("destroy", gtk.main_quit)
        self.m_window_main.set_default_size(700,450)
        self.m_window_main.set_title("Launder GTK+")
        
        # Create main vbox to hold toolbar and everything else
        self.m_vbox_main = gtk.VBox(homogeneous=False)
        self.m_window_main.add(self.m_vbox_main)
        
        # Create a hbox for some padding
        self.m_hbox_main = gtk.HBox(homogeneous=False)
        self.m_vbox_main.pack_start(self.m_hbox_main,  \
                                    padding = LaunderTypes.m_pad)

        
        # Add the control pane
        self.m_control_pane = ControlPane(self)
        self.m_hbox_main.pack_start(self.m_control_pane.m_vbox,  \
                                    padding = LaunderTypes.m_pad)
        
        # Add the trajectory MPL PlotPane
        self.m_trj_pane = PlotPane(self.m_window_main)
        self.m_hbox_main.pack_start(self.m_trj_pane.m_vbox,  \
                                    padding = LaunderTypes.m_pad)
        
        self.m_window_main.show_all()
        
        

    
    def main(self):
        gtk.main()

class ControlPane:
    def __init__(self, app):
        # Initialise empty variables
        self.m_auto_files = []
        self.m_selected_files = []
        self.m_types = LaunderTypes()
        self.m_app = app
        
        # Create main vbox for control pane
        self.m_vbox = gtk.VBox(homogeneous=False)
        
        # Create the toolbar
        self.m_toolbar = gtk.Toolbar()
        self.m_toolbar.set_style(gtk.TOOLBAR_ICONS)
        #self.m_toolbar.set_icon_size(4)
        
        # Create key buttons
        self.m_open = gtk.ToolButton(gtk.STOCK_OPEN)
        self.m_open.connect("clicked", self.chooseFile, )
        self.m_open.set_tooltip_text("Open files")
        self.m_open.connect("clicked", self.appendFilesToTreeView, "sel")
        self.m_auto = gtk.ToolButton(gtk.STOCK_EXECUTE)
        self.m_auto.set_tooltip_text("Automatically find files")
        self.m_auto.connect("clicked", self.autoFindFiles, )
        self.m_auto.connect("clicked", self.appendFilesToTreeView, "auto")
        self.m_quit = gtk.ToolButton(gtk.STOCK_QUIT)
        self.m_quit.set_tooltip_text("Quit")
        self.m_quit.connect("clicked", gtk.main_quit)
        
        # Insert buttons
        self.m_toolbar.insert(self.m_open, 0)
        self.m_toolbar.insert(self.m_auto, 1)
        self.m_toolbar.insert(self.m_quit, 2)
        
        # Add toolbar to pane's vbox
        self.m_vbox.pack_start(self.m_toolbar, fill=False, expand=False)
        
        # Create the frame for filepath info
        file_frame = gtk.Frame()
        file_frame.set_label("Simulation info")
        file_frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        file_vbox = gtk.VBox(homogeneous=False)
        
        # Add the file list pane
        label = gtk.Label("Available files")
        label.set_justify(gtk.JUSTIFY_LEFT)
        file_vbox.pack_start(label, fill=False, expand=False)
        file_frame.add(file_vbox)
        self.m_vbox.pack_start(file_frame)
        
        # Set up the file tree view
        self.m_file_tree_store = gtk.TreeStore(str)
        
        self.m_file_tree_view  = gtk.TreeView(self.m_file_tree_store)
        self.m_file_tree_col   = gtk.TreeViewColumn('Available files')
        self.m_file_tree_view.set_headers_visible(False)
        self.m_file_tree_view.append_column(self.m_file_tree_col)
        cell  = gtk.CellRendererText()
        self.m_file_tree_col.pack_start(cell, True)
        self.m_file_tree_col.add_attribute(cell, 'text', 0)
        
        # Put all of this in a scroller
        scroller = gtk.ScrolledWindow()
        scroller.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        #scroller.set_shadow_type(gtk.SHADOW_IN)
        scroller.add_with_viewport(self.m_file_tree_view)
        file_vbox.pack_start(scroller, \
                                    padding = LaunderTypes.m_pad)
        
        # Add buttons - load selected button
        self.m_button_loadfile = gtk.Button("Load selected")
        self.m_button_loadfile.connect("clicked",self.loadSelectedFile)
        file_vbox.pack_start(self.m_button_loadfile, expand=False, \
                             padding = LaunderTypes.m_pad)
        # Add buttons - get stats button
        self.m_button_getstats = gtk.Button("Get statistics")
        #self.m_button_loadfile.connect("clicked",self.loadSelectedFile)
        file_vbox.pack_start(self.m_button_getstats, expand=False, \
                             padding = LaunderTypes.m_pad)
        
    def chooseFile(self, data=None):
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
        dialog.set_select_multiple(True)
        
        # Add file filters to dialog
        filter = gtk.FileFilter()
        filter.set_name("MOPS outputs")
        filter.add_pattern("*.csv")
        filter.add_pattern("*.sav")
        filter.add_pattern("*.aux")
        filter.add_pattern("*.sim")
        dialog.add_filter(filter)
        
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        dialog.add_filter(filter)
        
        # Now run the chooser!
        fname = dialog.run()
        
        # Check the response
        if fname == gtk.RESPONSE_OK:
            self.m_selected_files = dialog.get_filenames()
        elif fname == gtk.RESPONSE_CANCEL:
            print 'Closed, no files selected'
        dialog.destroy()
    
    def autoFindFiles(self, widget, data=None):
        # Scans the current directory for any useful csv files
        
        # Get lists of potential files in directory
        filelist = self.findFiles("*-psl*.csv") + \
            self.findFiles("*-part.csv") + \
            self.findFiles("*-part-rates.csv") + \
            self.findFiles("*-chem.csv")
        
        if len(filelist) < 1:
            print("No files found.")
        else:
            self.m_auto_files = filelist
    
    def appendFilesToTreeView(self, widget, flag):
        # Given a list of filename, add this to the treeview
        filelist = []
        if flag == "sel":
            filelist = self.m_selected_files
        elif flag == "auto":
            filelist = self.m_auto_files
        for fname in filelist:
            self.m_file_tree_store.append(None, [fname])
        
    def loadSelectedFile(self, widget):
        # Loads the selected file on the TreeView
        selection = self.m_file_tree_view.get_selection().get_selected()
        if selection[1] == None:
            print("Nothing selected!")
            return None
        else:
            fname = selection[0].get_value(selection[1], 0)
        
        filetype = self.checkForKnownFile(fname)
        if filetype < 0:
            print("Unknown file! Deleting from list.")
            self.m_file_tree_store.remove(selection[1])
            return None
        elif filetype > 0:
            self.m_dialog = LoadCSVDialog(fname, filetype)
            self.m_dialog.m_window.connect("destroy", self.getLoadCSVDialogResults, )
        elif filetype == 0:
            print("PSL file found. Processing not implemented yet.")
            return None
    
    def checkForKnownFile(self, fname):
        # Checks that the filename is of a known type, returns the type
        if re.search("-psl", fname): return self.m_types.f_psl
        elif re.search("-chem.csv", fname): return self.m_types.f_chem
        elif re.search("-part-rates.csv", fname): return self.m_types.f_rates
        elif re.search("-part.csv", fname): return self.m_types.f_part
        else: return -1

    def getLoadCSVDialogResults(self, widget, data=None):
        # Returns the results from the loadCSV class
        results = self.m_dialog.m_results
        
        # Parse the file 
        if len(results) > 0:
            parser = MParser.TrajectoryParser(self.m_dialog.m_fname)
            allseries = parser.start(results)
        
        del self.m_dialog
        
        # Now pass the series list over to the PlotPane
        self.m_app.m_trj_pane.addSeries(allseries)
    
    def findFiles(self, searchtext):
        # Helper function to search for searchtext, and return lists of files
        # Need for filename matching
        filelist = glob.glob(searchtext)
        if len(filelist) == 0:
            return []
        else:
            return filelist

class LoadCSVDialog:
    # Class for loading relevant MOPS csv files into the system.
    def destroy(self, widget, data=None):
        self.m_window.destroy()
        return self.m_results
    
    def __init__(self, fname, filetype):
        self.m_fname = fname    # Name of file to load
        self.m_ftype = filetype # Type of file to load
        self.m_types = LaunderTypes()
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
                                    padding = LaunderTypes.m_pad)
        
        # Add some text explaining what to do
        label1 = gtk.Label("Select the trajectories to load.")
        self.m_vbox.pack_start(label1,  \
                                    padding = LaunderTypes.m_pad)
        
        # Generate the of trajectories
        self.makeTreeView()
        
        # Initialise a HBox and the buttons
        self.m_b_hbox          = gtk.HBox(homogeneous=True)
        self.m_b_load_selected = gtk.Button("Load selected")
        self.m_b_load_selected.connect("clicked", self.getSelectedTrajectories, )
        self.m_b_load_all      = gtk.Button("Load all")
        self.m_b_load_all.connect("clicked", self.getAllTrajectories, )
        self.m_b_hbox.pack_start(self.m_b_load_selected, expand=False,  \
                                    padding = LaunderTypes.m_pad)
        self.m_b_hbox.pack_start(self.m_b_load_all, expand=False,  \
                                    padding = LaunderTypes.m_pad)
        self.m_vbox.pack_start(self.m_b_hbox, fill=False,  \
                                    padding = LaunderTypes.m_pad)
        
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
                                    padding = LaunderTypes.m_pad)
    
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
        
    def main(self):
        gtk.main()

class PlotPane:
    # A display class which contains a MPL canvas, plot container and
    # various other capabilities to enable rapid GUI-driven plots based 
    # on the list of series in the plot container.
    
    def __init__(self, window):
        # Must pass pointer to the main window reference, to allow MPL toolbar
        # to be properly initialised.
        
        # Initialise the list of series to be plotted
        self.m_series = []
        self.m_series_dict = {}
        
        # Initialise a h/vbox for storage of all the plot elements.
        self.m_vbox = gtk.VBox(homogeneous=False)
        self.m_hbox = gtk.HBox(homogeneous=False)
        self.m_vbox.pack_start(self.m_hbox, padding=LaunderTypes.m_pad)
        
        # Create a frame to hold everything
        self.m_main_vbox = gtk.VBox(homogeneous=False)
        self.m_main_hbox = gtk.HBox()           # Hbox for padding
        self.m_main_hbox.pack_start(self.m_main_vbox, padding=LaunderTypes.m_pad)
        self.m_main_vbox.set_size_request(400,300)
        frame = gtk.Frame()
        frame.set_label("MOPS trajectories")
        frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        self.m_hbox.add(frame)
        frame.add(self.m_main_hbox)
        
         # Create the MPL canvas
        self.m_canvas = self.createMPLCanvas()        
        # Create the MPL toolbar
        self.m_mpl_toolbar = self.createMPLToolbar(self.m_canvas, window)
        self.m_main_vbox.pack_start(self.m_mpl_toolbar, expand=False)
        self.m_main_vbox.pack_start(self.m_canvas, padding=LaunderTypes.m_pad)
        
        # Add some buttons
        hbox = self.createCommandButtons()
        self.m_main_vbox.pack_start(hbox, expand=False)
               
        # Create a scroller and plot list pane
        scroller = self.createPlotList()
        self.m_main_vbox.pack_start(scroller, expand=False, \
                                    padding=LaunderTypes.m_pad)
        

    def createPlotList(self):
        # Create the liststore
        # Create the scroller
        scroller     = gtk.ScrolledWindow()
        scroller.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        scroller.set_shadow_type(gtk.SHADOW_IN)
        
        # Use columns: param / unit / PlotAvg / PlotCI
        self.m_liststore = gtk.ListStore(type("a"), type("a"))
        self.m_listview  = gtk.TreeView(self.m_liststore)
        scroller.add_with_viewport(self.m_listview)
        
        # Create columns
        self.addColumn("Parameter", 0)
        self.addColumn("Units", 1) 
        
        return scroller
    
    def addColumn(self, title, colID):
        col = gtk.TreeViewColumn(title, gtk.CellRendererText(), \
                             text=colID)
        col.set_resizable(True)
        col.set_sort_column_id(colID)
        self.m_listview.append_column(col)
    
    
    def createMPLCanvas(self):        
        # Create the figure
        figure = Figure(figsize=(5,4), dpi=100)
        self.m_axes = figure.add_subplot(111)
        canvas = FigureCanvas(figure)
        return canvas
    
    def createMPLToolbar(self, canvas, window):
        # Create the toolbar
        toolbar = NavToolbar(canvas, window)
        return toolbar
    
    def createCommandButtons(self):
        # Create handy buttons for plotting thins with MPL]
        
        self.m_b_plot_selection = gtk.Button("Plot selected")
        self.m_b_logx_toggle    = gtk.CheckButton("LogX?")
        self.m_b_logy_toggle    = gtk.CheckButton("LogY?")
        self.m_b_toggle_cis     = gtk.CheckButton("Plot CIs?")
        
        # Connect some signals
        self.m_b_logx_toggle.connect("toggled", self.toggleLogAxis, "x")
        self.m_b_logy_toggle.connect("toggled", self.toggleLogAxis, "y")
        
        hbox = gtk.HBox(homogeneous=False)
        hbox.pack_start(self.m_b_plot_selection, expand=False)
        hbox.pack_start(self.m_b_logx_toggle, expand=False)
        hbox.pack_start(self.m_b_logy_toggle, expand=False)
        hbox.pack_start(self.m_b_toggle_cis, expand=False)
        
        return hbox
    
    def toggleLogAxis(self, widget, data):
        # Toggles between logx/logy axes
        if widget.get_active():
            if data == "x":
                self.m_axes.set_xscale("log")
                self.m_canvas.draw()
            elif data == "y":
                self.m_axes.set_yscale("log")
                self.m_canvas.draw()
        else:
            if data == "x":
                self.m_axes.set_xscale("linear")
                self.m_canvas.draw()
            if data == "y":
                self.m_axes.set_yscale("linear")
                self.m_canvas.draw()
    
    def addSeries(self, serieslist):
        # Add a series to the plotlist from series list.
        
        for item in serieslist:
            ref = self.m_liststore.append(item.getPlotPaneList())
            self.m_series.append(item)
            
            # Add to the dictionary of liststore references


class LaunderTypes:
# Enum-like class to hold various constants
    f_psl    = 0
    f_rates  = 1
    f_chem   = 2
    f_part   = 3
    
    # Global padding delcration
    m_pad     = 5
    

if __name__ == "__main__":
    app = App()
    #app = LoadCSVDialog("silica-fm-part.csv", LaunderTypes().f_part)
    app.main()
    

print "all okay?"
