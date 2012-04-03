#!/usr/bin/env python

import sys

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

class LaunderApp:
    def __init__(self):
        # Create main window
        self.m_window_main = gtk.Window()
        
        # Initialise and connect signals
        self.m_window_main.connect("destroy", gtk.main_quit)
        self.m_window_main.set_default_size(600,400)
        self.m_window_main.set_title("Launder GTK+")
        
        # Create the key widgets
        self.m_toolbar = Toolbar()
        self.makeMPLVBox()
        
        # Create main vbox for toolbar
        self.m_toolbar_vbox  = gtk.VBox(homogeneous=False)
        self.m_toolbar_vbox.pack_start(self.m_toolbar.vbox, expand=False)
        self.m_toolbar_vbox.pack_start(self.m_mpl_vbox)
        self.m_window_main.add(self.m_toolbar_vbox)
        
        self.m_window_main.show_all()
    
    def makeMPLVBox(self):        
        # Create the figure
        self.m_mpl_fig = Figure(figsize=(5,4), dpi=100)
        self.m_mpl_ax = self.m_mpl_fig.add_subplot(111)
        self.m_mpl_canvas = FigureCanvas(self.m_mpl_fig)
        # Create the toolbar
        self.m_mpl_toolbar = NavToolbar(self.m_mpl_canvas, self.m_window_main)
        
        # Put everything in a vbox!
        self.m_mpl_vbox = gtk.VBox()
        self.m_mpl_vbox.pack_start(self.m_mpl_canvas)
        self.m_mpl_vbox.pack_start(self.m_mpl_toolbar, expand=False, fill=False)
    
    def main(self):
        gtk.main()
        

# Definition of the program toobar widget
class Toolbar:
    def __init__(self):
        # Create toolbar
        self.vbox = gtk.VBox()
        self.toolbar = gtk.Toolbar()
        self.toolbar.set_style(gtk.TOOLBAR_ICONS)
        self.toolbar.set_icon_size(4)
        
        # Add key buttons
        self.b_open = gtk.ToolButton(gtk.STOCK_OPEN)
        self.b_open.connect("clicked", self.chooseFile, )
        self.b_quit = gtk.ToolButton(gtk.STOCK_QUIT)
        self.b_quit.connect("clicked", gtk.main_quit)
        
        # Insert buttons
        self.toolbar.insert(self.b_open, 0)
        self.toolbar.insert(self.b_quit, 1)
        
        self.vbox.pack_start(self.toolbar, fill=False)
    
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
        
        # Add file filters to dialog
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        dialog.add_filter(filter)

        filter = gtk.FileFilter()
        filter.set_name("MOPS outputs")
        filter.add_pattern("*.csv")
        filter.add_pattern("*.sav")
        filter.add_pattern("*.aux")
        filter.add_pattern("*.sim")
        dialog.add_filter(filter)
        
        # Now run the chooser!
        fname = dialog.run()
        
        # Check the response
        if fname == gtk.RESPONSE_OK:
            print dialog.get_filename(), 'selected'
        elif fname == gtk.RESPONSE_CANCEL:
            print 'Closed, no files selected'
        self.m_selected_file = fname
        dialog.destroy()

if __name__ == "__main__":
    app = LaunderApp()
    app.main()
    

print "all okay?"
