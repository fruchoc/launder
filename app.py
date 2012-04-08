#!/usr/bin/env python

import sys
import glob

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
    

class App:
    def __init__(self):
        # Create main window
        self.m_window_main = gtk.Window()
        
        # Initialise and connect signals
        self.m_window_main.connect("destroy", gtk.main_quit)
        self.m_window_main.set_default_size(600,300)
        self.m_window_main.set_title("Launder GTK+")
        
        # Create main vbox to hold toolbar and everything else
        self.m_vbox_main = gtk.VBox(homogeneous=False)
        self.m_window_main.add(self.m_vbox_main)
        
        # Add the control pane
        self.m_control_pane = ControlPane()
        self.m_vbox_main.pack_start(self.m_control_pane.m_vbox)
        
        self.m_window_main.show_all()
        
        

    
    def main(self):
        gtk.main()

class ControlPane:
    def __init__(self):
        # Initialise empty variables
        self.m_auto_files = []
        self.m_selected_files = []
        
        
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
        
        # Add the file list pane
        label = gtk.Label("Available files")
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.m_vbox.pack_start(label, fill=False, expand=False)
        
        # Set up the file tree view
        self.m_file_tree_store = gtk.TreeStore(str)
        
        self.m_file_tree_view  = gtk.TreeView(self.m_file_tree_store)
        self.m_file_tree_col   = gtk.TreeViewColumn('Available files')
        self.m_file_tree_view.set_headers_visible(False)
        self.m_file_tree_view.append_column(self.m_file_tree_col)
        cell  = gtk.CellRendererText()
        self.m_file_tree_col.pack_start(cell, True)
        self.m_file_tree_col.add_attribute(cell, 'text', 0)
        self.m_vbox.pack_start(self.m_file_tree_view)
        
        # Add buttons
        self.m_button_loadfile = gtk.Button("Load selected")
        self.m_button_loadfile.connect("clicked",self.loadSelectedFile)
        self.m_vbox.pack_start(self.m_button_loadfile, expand=False)
    
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
            print("Found the following files:")
            for f in filelist:
                print f
    
    def appendFilesToTreeView(self, widget, flag):
        # Given a list of filename, add this to the treeview
        filelist = []
        if flag == "sel":
            filelist = self.m_selected_files
        elif flag == "auto":
            filelist = self.m_auto_files
        for fname in filelist:
            print fname
            self.m_file_tree_store.append(None, [fname])
        
    def loadSelectedFile(self, widget):
        # Loads the selected file on the TreeView
        print("Loading file.")
        selection = self.m_file_tree_view.get_selection().get_selected()
        fname = selection[0].get_value(selection[1], 0)
        
    
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
        self.destroy()
    
    def __init__(self, fname):
        self.m_fname = fname    # Name of file to load
        
        # Initialise a new window
        self.m_window = gtk.Window()
        self.m_window_main.connect("destroy", self.destroy)
        self.m_window_main.set_default_size(600,300)
        self.m_window_main.set_title("Launder GTK+")

if __name__ == "__main__":
    app = App()
    app.main()
    

print "all okay?"