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
        self.window_main = gtk.Window()
        
        # Initialise and connect signals
        self.window_main.connect("destroy", gtk.main_quit)
        self.window_main.set_default_size(600,400)
        self.window_main.set_title("Launder GTK+")
        
        # Create the configurator container
        self.config = gtk.HBox()
        
        # Create the matplotlib container
        self.mpl = ContainerMPL()
        
        # Create containers for layout
        self.hbox = gtk.HBox()
        self.hbox.pack_start(self.config)
        self.hbox.pack_start(self.mpl.vbox)
        self.window_main.add(self.hbox)
        
        self.window_main.show_all()
    
    def main(self):
        gtk.main()

# Definition of a container for a matplotlib widget
class ContainerMPL:
    def __init__(self):
        # Create vbox and add to window
        self.vbox = gtk.VBox()
        
        # Create figure and add to vbox
        self.fig = Figure(figsize=(5,4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        self.vbox.pack_start(self.canvas)
        
        # Create the nav toolbar and add to vbox
        self.toolbar = NavToolbar(self.canvas, self.vbox)
        self.vbox.pack_start(self.toolbar, expand=False, fill=False)

#class ContainerConfig:
#    def __init__(self):
        

if __name__ == "__main__":
    app = LaunderApp()
    app.main()
    

print "all okay?"
