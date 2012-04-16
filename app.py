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
    import datamodel.mops_trajectory as MTrj
    import datamodel.mops_parser as MParser
except:
    print("Couldn't find data model files!")
    sys.exit(4)

class App:
    def __init__(self):
        
        # Create main window
        self.m_window_main = gtk.Window()
        
        # Initialise and connect signals
        self.m_window_main.connect("destroy", gtk.main_quit)
        self.m_window_main.set_default_size(300,600)
        self.m_window_main.set_title("Launder GTK+")
        
        # Create main vbox to hold toolbar and everything else
        self.m_vbox_main = gtk.VBox(homogeneous=False)
        self.m_window_main.add(self.m_vbox_main)
        
        # Create a hbox for some padding
        self.m_hbox_main = gtk.HBox(homogeneous=False)
        self.m_vbox_main.pack_start(self.m_hbox_main,  \
                                    padding = LaunderTypes.m_pad)

        
        # Add the control pane
        self.m_control_pane = ControlPane()
        self.m_hbox_main.pack_start(self.m_control_pane.m_vbox,  \
                                    padding = LaunderTypes.m_pad)
        
        # Add the trajectory MPL PlotPane
        self.m_trj_pane = PlotPane()
        self.m_hbox_main.pack_start(self.m_trj_pane.m_vbox,  \
                                    padding = LaunderTypes.m_pad)
        
        self.m_window_main.show_all()
        
        

    
    def main(self):
        gtk.main()

class ControlPane:
    def __init__(self):
        # Initialise empty variables
        self.m_auto_files = []
        self.m_selected_files = []
        self.m_types = LaunderTypes()
        
        # Create main vbox for control pane
        self.m_vbox = gtk.VBox(homogeneous=False)
        
        # Create the toolbar
        self.m_toolbar = gtk.Toolbar()
        self.m_toolbar.set_style(gtk.TOOLBAR_ICONS)
        self.m_toolbar.set_icon_size(4)
        
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
        file_vbox.pack_start(self.m_file_tree_view, \
                                    padding = LaunderTypes.m_pad)
        
        # Add buttons
        self.m_button_loadfile = gtk.Button("Load selected")
        self.m_button_loadfile.connect("clicked",self.loadSelectedFile)
        file_vbox.pack_start(self.m_button_loadfile, expand=False)
    
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
        else:
            self.m_dialog = LoadCSVDialog(fname, filetype)
            self.m_dialog.m_window.connect("destroy", self.getLoadCSVDialogResults, )
    
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
        
        if (results == []):
            print "nothing"
        else:
            print results
        
        del self.m_dialog
    
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
    
    def __init__(self):
        
        # Initialise a h/vbox for storage of all the plot elements.
        self.m_vbox = gtk.VBox(homogeneous=False)
        self.m_hbox = gtk.HBox(homogeneous=False)
        self.m_vbox.pack_start(self.m_hbox, padding=LaunderTypes.m_pad)
        
        # Create a frame to hold everything
        self.m_main_hbox = gtk.HBox(homogeneous=False)
        frame = gtk.Frame()
        frame.set_label("PlotPane type here")
        frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        frame.add(self.m_main_hbox)
        self.m_hbox.pack_start(frame, padding=LaunderTypes.m_pad)
        
        # Create a scroller and plot list pane
        self.m_list = self.createPlotList()
        self.m_main_hbox.pack_start(self.m_list)
        
        # Create the MPL canvas
        self.m_canvas = self.createMPLCanvas()
        self.m_main_hbox.pack_start(self.m_canvas)

    def createPlotList(self):
        # Create the liststore
        # Create the scroller
        scroller     = gtk.ScrolledWindow()
        scroller.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        scroller.set_shadow_type(gtk.SHADOW_IN)
        
        # Use columns: param / unit / PlotAvg / PlotCI
        store = gtk.ListStore(type("a"), type("a"), \
                              type(gtk.RadioButton()), 
                              type(gtk.RadioButton()))
        view  = gtk.TreeView(store)
        scroller.add_with_viewport(view)
        
        # Create columns
        renderer = gtk.CellRendererText()
        col      = gtk.TreeViewColumn("Parameter", renderer, text=0)
        col.set_sort_column_id(0)
        view.append_column(col)
        
        renderer = gtk.CellRendererText()
        col      = gtk.TreeViewColumn("Units", renderer, text=0)
        col.set_sort_column_id(1)
        view.append_column(col)    
            
        renderer = gtk.CellRendererText()
        col      = gtk.TreeViewColumn("Plot Avg?", renderer, text=0)
        col.set_sort_column_id(2)
        view.append_column(col)
        
        renderer = gtk.CellRendererText()
        col      = gtk.TreeViewColumn("Plot CIs?", renderer, text=0)
        col.set_sort_column_id(3)
        view.append_column(col)
        
        return scroller
    
    
    def createMPLCanvas(self):        
        # Create the figure
        figure = Figure(figsize=(5,4), dpi=100)
        axes = figure.add_subplot(111)
        canvas = FigureCanvas(figure)
        return canvas
    
    #def createMPLToolbar(self):
        # Create the toolbar
        #toolbar = NavToolbar(canvas, self.m_window_main)
        #return toolbar
    
class PlotContainer:
    # Generic class for holding data series to be plotted via MPL
    
    def __init__(self):
        self.m_plotlist = []        # List of all series to be plot
        


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
