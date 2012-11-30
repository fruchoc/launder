import glob
import os

try:
    import pygtk
    pygtk.require("2.0")
except:
    print("Couldn't find correct version of pygtk.")

try:
    import gtk
except:
    print("Couldn't find correct version of gtk.")

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_gtkagg \
        import FigureCanvasGTKAgg as FigureCanvas
    from matplotlib.backends.backend_gtkagg \
        import NavigationToolbar2GTKAgg as NavToolbar
except:
    print("Couldn't find matplotlib dependencies.")

class MView(object):
    # Master class which administers all windows.
    
    def __init__(self):
        # Main window
        self.win_files  = MFiles()
        self.win_files.make()
        self.win_files.show()
    
    def main(self):
        gtk.main()
    
class MWindow(object):
    # An abstract class.
    
    def __init__(self):
        # Create the window object
        self.win = gtk.Window()
        self.win.connect("destroy", gtk.main_quit)
        self.win.set_default_size(self.x_def, self.y_def)
    
    def show(self):
        self.win.show_all()
    
    # Declare some constants for general use
    name = "mview"
    
    # Default x and y window sizes
    x_def   = 550
    y_def   = 350
    
    def _set_win_title(self, window, value):
        # Sets the title of a window
        window.set_title(self.name + ": " + value)
    
    def make(self):
        print("Don't call abstract class make.")

class MFiles(MWindow):
    # A window class to allow importing of files and folders.
    def __init__(self):
        super(MFiles, self).__init__()
        self._set_win_title(self.win, "Files")
        
        # A list of files most recently selected by the file chooser
        self.__sel_files = []
        
        # A list of default extensions for use when scanning.
        self.__exts = ["*.csv"]
    
    def make(self):
        # Make a window which allows access of files and directories of CSV and
        # MOPS results.
        
        # Add a vbox
        vb = gtk.VBox(homogeneous=False)
        self.win.add(vb)
        
        # Create the toolbar
        tools = gtk.Toolbar()
        tools.set_style(gtk.TOOLBAR_ICONS)
        vb.pack_start(tools, fill=False)
        
        # The open button
        open = gtk.ToolButton(gtk.STOCK_OPEN)
        open.set_tooltip_text("Open files or folders")
        open.connect("clicked", self.choose, )
        tools.insert(open, 0)
        
        # The autoscan button
        scan = gtk.ToolButton(gtk.STOCK_REFRESH)
        scan.set_tooltip_text("Scan current directory for data")
        scan.connect("clicked", self.scan, )
        tools.insert(scan, 1)
        
        # The remove button
        rem  = gtk.ToolButton(gtk.STOCK_DELETE)
        rem.set_tooltip_text("Delete entry from file lists")
        rem.connect("clicked", self.delete, )
        tools.insert(rem, 2)
        
        # The clean button
        cln  = gtk.ToolButton(gtk.STOCK_CLEAR)
        cln.set_tooltip_text("Clear all file entries")
        cln.connect("clicked", self.clean, )
        tools.insert(cln, 3)
        
        # The quit button
        quit = gtk.ToolButton(gtk.STOCK_QUIT)
        quit.set_tooltip_text("Quit " + self.name)
        quit.connect("clicked", gtk.main_quit)
        tools.insert(quit, 4)
        
        # Now set up the Tree Store.
        self.store = gtk.TreeStore(str)
        self.view  = gtk.TreeView(self.store)
        
        # Set up a column for the folder names
        col1       = gtk.TreeViewColumn("Available files")
        col1.pack_start(gtk.CellRendererText(), True)
        self.view.append_column(col1)
        
        # Add a scroller
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add_with_viewport(self.view)
        vb.pack_start(scroll, expand=True)
        
    
    def choose(self, callback = None):
        # Opens a file chooser to open files or folders
        dialog = gtk.FileChooserDialog("Load files or folders..",
                                       None,
                                       gtk.FILE_CHOOSER_ACTION_OPEN,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        dialog.set_current_folder(os.getcwd())
        
        # Allow multiple files
        dialog.set_select_multiple(True)
        # Allow the selection of a folder
        #dialog.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        
        # Add file filters
        filter = gtk.FileFilter()
        filter.set_name("MOPS outputs")
        filter.add_pattern("*.csv")
        dialog.add_filter(filter)
        
        filter = gtk.FileFilter()
        filter.set_name("Common data files")
        filter.add_pattern("*.csv")
        filter.add_pattern("*.dat")
        dialog.add_filter(filter)
        
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        dialog.add_filter(filter)
        
        val = dialog.run()
        if val == gtk.RESPONSE_OK:
            self.__sel_files = dialog.get_filenames()
            if not self.__sel_files:
                self.__sel_files = []
        else:
            self.__sel_files = []
        
        # Add them to the store.
        for f in self.__sel_files:
            self.__add_file_to_store(f)
        
        dialog.destroy()
    
    def scan(self, callback = None):
        # Scans the current directory for files which could be used.
        
        flist = []
        for ext in self.__exts:
            for f in glob.glob(ext):
                flist.append(f)
        
        # Now add to the store
        for f in flist:
            self.__add_file_to_store(f)
    
    def clean(self, callback = None):
        # Cleans the list store
        self.store.clear()
    
    def delete(self, callback = None):
        # Deletes an entry
        s = self.view.get_selection()
        
        if s.count_selected_rows() > 0:
            (model, plist) = s.get_selected_rows()
            for path in reversed(plist):
                del self.store[path[0]]
    
    def list_folders(self):
        # Gets a list of folders loaded in the tree
        flist = []
        for row in self.store:
            print row
            dir(row)
            v = self.store.get_value(row, 0)
            print v
        
        return flist
    
    def __get_folder_iter(self, folder):
        # Returns the TreeIter of a folder already in the tree
        pass
    
    def __is_folder_in_tree(self, folder):
        # Is the folder present in thre tree?
        if folder in self.list_folders():
            return True
        else:
            return False
    
    def __is_in_tree(self, fname):
        # Checks if a file is already in the tree
        flist = []
        for row in self.store:
            flist.append(row[0])
        return flist
    
    def __add_folder_to_store(self, folder):
        # Adds a folder reference to the store.
        return self.store.append(None, [folder])
    
    def __add_file_to_store(self, fname):
        # Adds a file to the TreeStore
        (folder, name) = os.path.split(os.path.abspath(fname))
        
        # Is the file already in the tree?
        if self.__is_in_tree(fname):
            # Do nothing
            pass
        else:
            if self.__is_folder_in_tree(folder):
                # Get an iter reference to the folder
                iter = None
            else:
                # Add the folder to the tree first
                iter = self.__add_folder_to_store(folder)
            
            # Now append it to store
            self.store.append(iter, [name])
