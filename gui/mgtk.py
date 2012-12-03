import glob
import os

# Imports from the other program libraries
import structure.lparser
import structure.core

# GUI imports: gtk, pygtk and matplotlib.
try:
    import pygtk
    pygtk.require("2.0")
    import gobject
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
        
        self.win_series = MSeriesBrowser()
        self.win_series.make()
        self.win_series.show()
        self.win_files.connect_series_window(self.win_series)
    
    def main(self):
        gtk.main()
    
class MWindow(object):
    # An abstract class.
    
    def __init__(self):
        # Create the window object
        self.win = gtk.Window()
        self.win.connect("destroy", self.destroy, )
        
        # Ask for some size
        self.win.set_size_request(500, 350)
    
    def destroy(self, callback = None):
        self.win.destroy()
    
    def show(self):
        self.win.show_all()
    
    # Declare some constants for general use
    name = "mview"
    
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
        fw = MFileLoader(fname, self.win_series)
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
    
    def connect_series_window(self, win_series):
        # Connects the series window to this one
        self.win_series = win_series
    
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
    
    def __init__(self, fname, win_series):
        super(MFileLoader, self).__init__()
        self._set_win_title(self.win, "Loading " + fname)
        
        # Need to store a reference to the win_series window to enable
        # creation of series in the store.
        self.win_series = win_series
        
        # Ask for some size
        self.win.set_size_request(300, 180)
        
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
        self.data = data_dict["data"]
        self.keys = data_dict["keys"]
        
        # Create some elements in the window
        vb = gtk.VBox(homogeneous = False)
        self.win.add(vb)
        vb.pack_start(gtk.Label("Generic DSV file found."), expand=False,
                      padding=10)
        
        # X axis chooser
        hbx = gtk.HBox(homogeneous = False)
        vb.pack_start(hbx, expand=False, fill=False)
        hbx.pack_start(gtk.Label("Y-axis column:"), expand=False, 
                        padding=10)
        self.xcombo = self.__make_combo(self.keys)
        hbx.pack_start(self.xcombo, expand=False)
        
        # Y axis chooser
        hby = gtk.HBox(homogeneous = False)
        vb.pack_start(hby, expand=False, fill=False)
        hby.pack_start(gtk.Label("Y-axis column:"), expand=False,
                        padding=10)
        self.ycombo = self.__make_combo(self.keys)
        hby.pack_start(self.ycombo, expand=False)
        
        # Name for series field
        hbn = gtk.HBox(homogeneous = False)
        vb.pack_start(hbn, expand=False, fill=False)
        self.entry = gtk.Entry(20)
        self.entry.set_text("Enter name")
        hbn.pack_start(gtk.Label("name of series:"), expand=False, padding=10)
        hbn.pack_start(self.entry, expand=False)
        
        # Add series button
        but1 = gtk.Button("Add series")
        but1.connect("clicked", self.add_series, )
        hbb = gtk.HBox(homogeneous=False)
        hbb.pack_end(but1, expand=False, fill=False, padding=5)
        
        but2 = gtk.Button("Add all Y")
        but2.connect("clicked", self.add_all_series, )
        hbb.pack_end(but2, expand=False, fill=False, padding=5)
        vb.pack_start(hbb, expand=False, fill=False, padding=10)
    
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

    def __get_combo(self, box):
        # Gets the selection of a combo box
        
        index = box.get_active()
        model = box.get_model()
        return model[index][0]
    
    def __add_to_window(self, series):
        # Adds a series object to the Series Browser window
        self.win_series.add_series(series, self.fname)
    
    def add_series(self, callback = None):
        # Adds a series
        if self.xcombo and self.ycombo and self.entry:
            print "Adding a generic series."
            
            # Generic, let's find the choices from the ComboBox
            xkey = self.__get_combo(self.xcombo)
            ykey = self.__get_combo(self.ycombo)
            name = self.entry.get_text()
            
            # Create the series
            tx = structure.core.Trj(xkey, self.data[xkey])
            ty = structure.core.Trj(ykey, self.data[ykey])
            s = structure.core.Series(name, tx, ty)
            self.__add_to_window(s)
    
    def add_all_series(self, callback = None):
        # For a specified x series, add all the y series.
        if self.xcombo and self.ycombo:
            print("Adding all y series for the specified x series.")
            
            xkey = self.__get_combo(self.xcombo)
            # Get all the ykeys
            ylist = []
            for k in self.keys:
                if k != xkey: ylist.append(k)
            
            # Now create the series
            tx = structure.core.Trj(xkey, self.data[xkey])
            for k in ylist:
                ty = structure.core.Trj(k, self.data[k])
                s = structure.core.Series(k + " vs " + xkey, tx, ty)
                self.__add_to_window(s)
        
        # Kill window as the user is probably finished with it.
        self.destroy()

class MSeriesBrowser(MWindow):
    # The Series Browser lists all the series currently available for plotting.
    # Should be able to take generic structure.core.Series objects from any
    # file types, and send them to matplotlib windows.
    
    # The Series Browser also owns any matplotlib windows which may be open.
    
    def __init__(self):
        super(MSeriesBrowser, self).__init__()
        self._set_win_title(self.win, "Series Browser")
        
        self.win.set_size_request(500, 300)
        
    
    def __make_col(self, label, id):
        # Adds a column to the list view
        cell = gtk.CellRendererText()
        
        # Increment the text display in the column by one, so that the generic
        # object is not displayed.
        col = gtk.TreeViewColumn(label, cell, text=id+1)
        col.set_resizable(True)
        col.set_sort_column_id(id)
        return col
    
    def __get_selections(self):
        # Gets selections of the store.
        
        sel = self.view.get_selection()
        paths = []
        if sel.count_selected_rows() > 0:
            (model, paths) = sel.get_selected_rows()
        return paths
    
    def make(self):
        # Makes the window
        
        # Create a vbox to hold everything
        vb = gtk.VBox(homogeneous=False)
        self.win.add(vb)
        
        # Create a toolbar.
        tools = gtk.Toolbar()
        tools.set_style(gtk.TOOLBAR_ICONS)
        vb.pack_start(tools, expand=False, fill=False)
        
        # Create an export button
        save = gtk.ToolButton(gtk.STOCK_SAVE)
        save.set_tooltip_text("Save the selected series")
        save.connect("clicked", self.save_series, )
        tools.insert(save, 0)
        
        # Create a remove button
        delete = gtk.ToolButton(gtk.STOCK_REMOVE)
        delete.set_tooltip_text("Delete series")
        delete.connect("clicked", self.remove_series, )
        tools.insert(delete, 1)
        
        # Create a clear button
        clear = gtk.ToolButton(gtk.STOCK_CLEAR)
        clear.set_tooltip_text("Clear all series")
        clear.connect("clicked", self.clear_series, )
        tools.insert(clear, 2)
        
        # Insert a separator
        tools.insert(gtk.SeparatorToolItem(), 3)
        
        # NOW ADD SOME PLOTTING BUTTONS
        new = gtk.ToolButton(gtk.STOCK_NEW)
        new.set_tooltip_text("Generate new plot of series")
        new.set_label("New plot")
        tools.insert(new, 4)
        
        # Create a list store to display available series
        # Put a structure.core.Series object as the first column.
        self.store = gtk.ListStore(gobject.TYPE_PYOBJECT, str, str, str, str)
        self.view  = gtk.TreeView(self.store)
        self.view.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        
        # Create a scroller
        scroller = gtk.ScrolledWindow()
        scroller.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        scroller.add_with_viewport(self.view)
        vb.pack_start(scroller, expand=True, fill=True)
        
        # Add the columns
        self.view.append_column(self.__make_col("Name", 0))
        self.view.append_column(self.__make_col("X Trj", 1))
        self.view.append_column(self.__make_col("Y Trj", 2))
        self.view.append_column(self.__make_col("File", 3))
    
    def add_series(self, series, fname):
        # Adds a series object from a file fname
        
        # Check the series has a filename
        if not series.filename: series.set_file(fname)
        
        self.store.append(series.get_data_list())
    
    def remove_series(self, callback=None):
        # Deletes the series from the list
        for path in self.__get_selections():
            self.store.remove(self.store.get_iter(path))
    
    def clear_series(self, callback=None):
        # Clear all series
        
        self.store.clear()
    
    def choose_save(self, series):
        # Choose a filename to save to.
        if gtk.pygtk_version < (2,3,90):
            raise SystemExit("PyGtk 2.3.90 or later required!")
        
        dlg = gtk.FileChooserDialog("Select file to save series " + series.name,
                               None,
                               gtk.FILE_CHOOSER_ACTION_SAVE,
                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        dlg.set_default_response(gtk.RESPONSE_OK)
        dlg.set_select_multiple(False)
        
        r = dlg.run()
        fname = ""
        if r == gtk.RESPONSE_OK:
            fname = dlg.get_filename()
        
        dlg.destroy()
        return fname
    
    def save_series(self, callback=None):
        
        # Loop over paths
        for path in self.__get_selections():
            # Get the Series object
            s = self.store.get_value(self.store.get_iter(path), 0)
            
            # Get a filename
            f = self.choose_save(s)
            if f:
                # Open a parser and write
                p = structure.lparser.DSVWriter(f)
                p.write_series(s)
                p.close()
                