import glob
import os

# Imports from the other program libraries
import structure.lparser
import structure.core

# GUI imports: gtk, pygtk and matplotlib.
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
        self.win.connect("destroy", self.destroy, )
        self.win.set_default_size(self.x_def, self.y_def)
    
    def destroy(self, callback = None):
        self.win.destroy()
    
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
        self.win.connect("destroy", gtk.main_quit)
        
        # A list of files most recently selected by the file chooser
        self.__sel_files = []
        
        # A list of default extensions for use when scanning.
        self.__exts = ["*.csv", "*.dat"]
    
    def make(self):
        # Make a window which allows access of files and directories of CSV and
        # MOPS results.
        
        # Add a vbox
        vb = gtk.VBox(homogeneous=False)
        self.win.add(vb)
        
        # Make a hbox
        hb = gtk.HBox(homogeneous=False)
        vb.pack_start(hb, fill=False, expand=False)
        
        # Create the toolbar
        tools = gtk.Toolbar()
        tools.set_style(gtk.TOOLBAR_ICONS)
        hb.pack_start(tools)
        
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
        
        # Add the file loading buttons
        but = gtk.Button("Load file")
        but.connect("clicked", self.load_selected_file, )
        hb.pack_end(but, expand=False, fill=False, padding=2)
        
        # Now set up the Tree Store.
        self.store = gtk.TreeStore(str)
        self.view  = gtk.TreeView(self.store)
        
        # Generate a cell
        cell        = gtk.CellRendererText()
        
        # Set up a column for the folder names
        col1       = gtk.TreeViewColumn("Available files")
        col1.pack_start(cell, True)
        col1.add_attribute(cell, 'text', 0)
        self.view.append_column(col1)
        
        # Add a scroller
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add_with_viewport(self.view)
        vb.pack_start(scroll, expand=True, fill=True, padding=4)
        
    
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
    
    def get_all_folders(self):
        # Gets a list of folders loaded in the tree
        flist = []
        for row in self.store:
            # Only append if it has a parent (i.e. a folder)
            if not row.parent:
                flist.append(row[0])
        
        return flist
    
    def get_selected_file(self, callback = None):
        # Get the absolute path of the file selected.
        s = self.view.get_selection()
        fname = None
        if s:
            model, titer = s.get_selected()
            if titer:
                # Make sure that the TreeIter has a parent 
                # i.e. prevent directories from being loaded
                if model.iter_parent(titer):
                    fname = self.get_full_file_path(titer)
        
        return fname
    
    def get_all_files(self):
        # Gets a list of all files (full absolute paths) in store.
        flist = []
        for row in self.store:
            # Now loop over any children
            for child in row.iterchildren():
                flist.append(self.get_full_file_path(child.iter))
        return flist
    
    def get_full_file_path(self, titer):
        # From a TreeIter object, get the full path of a file
        fname = ""
        model = self.view.get_model()
        parent_titer = model.iter_parent(titer)
        if parent_titer:
            fname += model.get_value(parent_titer, 0)
        return os.path.join(fname, model.get_value(titer, 0))
    
    def load_selected_file(self, callback = None):
        fname = self.get_selected_file(callback)
        if fname:
            print "Loading", fname
        fw = MFileLoader(fname)
        fw.make()
        fw.show()
    
    def __get_folder_iter(self, folder):
        i = None
        if self.__is_folder_in_tree(folder):
            # If the folder is already in tree, get its iter
            for row in self.store:
                if not row.parent:
                    # File entries have no parents
                    if folder == row[0]:
                        i = row.iter
        else:
            # Otherwise, create a folder and add it.
            i = self.__add_folder_to_store(folder)
        return i
    
    def __is_folder_in_tree(self, folder):
        # Is the folder present in thre tree?
        ans = False
        flist = self.get_all_folders()
        
        if folder in flist:
            ans = True
        return ans
    
    def __is_in_tree(self, fname):
        # Checks if a file is already in the tree
        ans = False
        if os.path.abspath(fname) in self.get_all_files():
            ans = True
        return ans
    
    def __add_folder_to_store(self, folder):
        # Adds a folder reference to the store.
        return self.store.append(None, [folder])
    
    def __add_file_to_store(self, fname):
        # Adds a file to the TreeStore
        (folder, name) = os.path.split(os.path.abspath(fname))
        
        # Is the file already in the tree?
        if self.__is_in_tree(fname):
            # Do nothing
            #print "File " + fname + " is in tree."
            pass
        else:
            # Now append it to store
            self.store.append(self.__get_folder_iter(folder), [name])

class MFileLoader(MWindow):
    # The File Loader class is used to load the DSV files found by the 
    # MFiles class. It will change appearance based on the type of 
    # DSV file obtained.
    
    
    def __init__(self, fname):
        super(MFileLoader, self).__init__()
        self._set_win_title(self.win, "Loading " + fname)
        
        self.fname = fname
        ftype = structure.lparser.examine_filetype(fname)
        self.ffunc = self.other
        if ftype == "psl": self.ffunc = self.psl
        elif ftype == "part": self.ffunc = self.part
    
    def make(self):
        # Makes the file loader.
        self.ffunc()
    
    def psl(self):
        # Loads a PSL file
        pass
    
    def part(self):
        # Loads a MOPS -part.csv style file.
        pass
    
    def other(self):
        # Loads a generic DSV file
        
        # Create a parser
        p = structure.lparser.LParser(self.fname)
        data_dict = p.get()
        del p
        
        # Get a dictionary of the data from the file.
        data = data_dict["data"]
        keys = data_dict["keys"]
        
        # Create some elements in the window
        vb = gtk.VBox(homogeneous = False)
        self.win.add(vb)
        vb.pack_start(gtk.Label("Generic DSV file found."), expand=False)
        
        

        # X axis chooser
        hbx = gtk.HBox(homogeneous = False)
        vb.pack_start(hbx, expand=False, fill=False)
        hbx.pack_start(gtk.Label("x-axis column:"), expand=False)
        self.xcombo = self.__make_combo(keys)
        hbx.pack_start(self.xcombo, expand=False)
        
        # Y axis chooser
        hby = gtk.HBox(homogeneous = False)
        vb.pack_start(hby, expand=False, fill=False)
        hby.pack_start(gtk.Label("y-axis column:"), expand=False)
        self.ycombo = self.__make_combo(keys)
        hby.pack_start(self.ycombo, expand=False)
    
    def __make_combo(self, values):
        # Makes a ComboBox from a list of keys
        
        # Create a list store for the names
        store = gtk.ListStore(str)
        for v in values:
            store.append([v])
        
        combo = gtk.ComboBox(store)
        
        cell = gtk.CellRendererText()
        combo.pack_start(cell, True)
        combo.add_attribute(cell, "text", 0)
        return combo

    def __get_combo(self, callback = None):
        # Gets the selection of a combo box
        
        # First check that the object has combo boxes
        if (not self.xcombo) and (not self.ycombo):
            return None
        
        if callback == "x":
            pass
