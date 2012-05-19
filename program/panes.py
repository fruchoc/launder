"""
panes.py
Windows and panes used to communicate information in the GUI.
(c) William Menz (wjm34) 2012
"""
import sys
import os
import glob
import re
from itertools import cycle

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

# Other libraries
try:
    import datamodel.mops_parser as MParser
    import datamodel.series as Series
    import datamodel.ensemble as Ensemble
    import program.dialogs as Dlg
    import program.output as Out
except:
    print("Couldn't find other sources for " + os.path.abspath( __file__ ))
    sys.exit(4)


class App:
    def __init__(self, consts):
        
        # Store constants
        self.m_consts   = consts
        
        # Create main window
        self.m_window_main = gtk.Window()
        
        # Initialise and connect signals
        self.m_window_main.connect("destroy", gtk.main_quit)
        self.m_window_main.set_default_size(self.m_consts.x_main,\
                                            self.m_consts.y_main)
        self.m_window_main.set_title("Launder GTK+")
        
        # Create main vbox to hold toolbar and everything else
        self.m_vbox_main = gtk.VBox(homogeneous=False)
        self.m_window_main.add(self.m_vbox_main)
        
        # Create a hbox for some padding
        self.m_hbox_main = gtk.HBox(homogeneous=False)
        self.m_vbox_main.pack_start(self.m_hbox_main,  \
                                    padding = self.m_consts.m_pad)

        
        # Add the control pane
        self.m_control_pane = ControlPane(self)
        self.m_hbox_main.pack_start(self.m_control_pane.m_vbox,  \
                                    padding = self.m_consts.m_pad)
        
        # Add the trajectory MPL PlotPane
        self.m_trj_pane = TrajectoryPane(self.m_window_main, \
                                         "Trajectories", self.m_consts, \
                                         "time, s")
        self.m_hbox_main.pack_start(self.m_trj_pane.m_vbox,  \
                                    padding = self.m_consts.m_pad)
        
        self.m_psd_pane = PSDPane(self.m_window_main, \
                                         "PSDs", self.m_consts, \
                                          "diameter, nm")
        self.m_hbox_main.pack_start(self.m_psd_pane.m_vbox,  \
                                    padding = self.m_consts.m_pad)
        
        self.m_window_main.show_all()

    def main(self):
        gtk.main()

class ControlPane:
    def __init__(self, app):
        # Initialise empty variables
        self.m_auto_files = []
        self.m_selected_files = []
        self.m_types = app.m_consts
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
        self.m_b_delete = gtk.ToolButton(gtk.STOCK_DELETE)
        self.m_b_delete.set_tooltip_text("Delete file entry")
        self.m_b_delete.connect("clicked", self.removeSelectedFile, )
        self.m_auto.connect("clicked", self.autoFindFiles, )
        self.m_auto.connect("clicked", self.appendFilesToTreeView, "auto")
        self.m_quit = gtk.ToolButton(gtk.STOCK_QUIT)
        self.m_quit.set_tooltip_text("Quit")
        self.m_quit.connect("clicked", gtk.main_quit)
        
        # Insert buttons
        self.m_toolbar.insert(self.m_open, 0)
        self.m_toolbar.insert(self.m_auto, 1)
        self.m_toolbar.insert(self.m_b_delete, 2)
        self.m_toolbar.insert(self.m_quit, 3)
        
        # Add toolbar to pane's vbox
        self.m_vbox.pack_start(self.m_toolbar, fill=False, expand=False)
        
        # Create the frame for filepath info
        file_frame = gtk.Frame()
        file_frame.set_label("Simulation info")
        file_frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        file_vbox = gtk.VBox(homogeneous=False)
        hbox      = gtk.HBox(homogeneous=False)
        hbox.pack_start(file_vbox, padding = self.m_types.m_pad)
        
        # Add the file list pane
        label = gtk.Label("Available files")
        label.set_justify(gtk.JUSTIFY_LEFT)
        file_vbox.pack_start(label, fill=False, expand=False)
        file_frame.add(hbox)
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
                                    padding = self.m_types.m_pad)
        
        # Add buttons - load selected button
        self.m_button_loadfile = gtk.Button("Load selected")
        self.m_button_loadfile.connect("clicked",self.loadSelectedFile)
        file_vbox.pack_start(self.m_button_loadfile, expand=False, \
                             padding = self.m_types.m_pad)
        # Add buttons - get stats button
        self.m_button_getstats = gtk.Button("Get statistics")
        self.m_button_getstats.connect("clicked",self.getStats, None)
        file_vbox.pack_start(self.m_button_getstats, expand=False, \
                             padding = self.m_types.m_pad)
        
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
        
        filetype = self.m_types.checkForKnownFile(fname)
        if filetype < 0:
            print("Unknown file! Deleting from list.")
            self.m_file_tree_store.remove(selection[1])
            return None
        elif filetype > 0:
            self.m_dialog = Dlg.LoadCSVDialog(fname, self.m_types, filetype)
            self.m_dialog.m_window.connect("destroy", self.getLoadCSVDialogResults, )
        elif filetype == 0:
            dialog = Dlg.LoadPSLDialog(fname, self.m_app.m_psd_pane, self.m_types)
            return None
    
    def removeSelectedFile(self, widget):
        # Removes the file entry from the tresstore
        selection = self.m_file_tree_view.get_selection().get_selected()
        if selection[1] == None:
            print("Nothing selected!")
        else:
            self.m_file_tree_store.remove(selection[1])
    
    def getStats(self, widget, data=None):
        # Gets the XML statistics of the file
        
        selection = self.m_file_tree_view.get_selection().get_selected()
        if selection[1] == None:
            print("Nothing selected!")
            return None
        else:
            fname = selection[0].get_value(selection[1], 0)
        
        dialog = Dlg.GetStatsDialog(fname, self.m_types)
    
    def getLoadCSVDialogResults(self, widget, data=None):
        # Returns the results from the loadCSV class
        results = self.m_dialog.m_results
        
        # Parse the file 
        if len(results) > 0:
            parser = MParser.TrajectoryParser(self.m_dialog.m_fname)
            allseries = parser.start(results)
            
            # Now pass the series list over to the PlotPane
            self.m_app.m_trj_pane.addSeries(allseries)
        
        del self.m_dialog

    
    def findFiles(self, searchtext):
        # Helper function to search for searchtext, and return lists of files
        # Need for filename matching
        filelist = glob.glob(searchtext)
        if len(filelist) == 0:
            return []
        else:
            return filelist

class PlotPane:
    # A display class which contains a MPL canvas, plot container and
    # various other capabilities to enable rapid GUI-driven plots based 
    # on the list of series in the plot container.
    
    def __init__(self, window, name, consts, xlabel):
        # Must pass pointer to the main window reference, to allow MPL toolbar
        # to be properly initialised.
        
        # Initialise the list of series to be plotted
        self.m_series_dict = {}
        self.m_xlDefaul    = xlabel
        self.m_styles      = PlotStyles()
        self.m_consts      = consts
        
        # Series currently being plotted
        self.m_plotted = {}
        
        # Is the plot editor open?
        self.m_editOpen = False
        
        # Initialise a h/vbox for storage of all the plot elements.
        self.m_vbox = gtk.VBox(homogeneous=False)
        self.m_hbox = gtk.HBox(homogeneous=False)
        self.m_vbox.pack_start(self.m_hbox, padding=self.m_consts.m_pad)
        
        # Create a frame to hold everything
        self.m_main_vbox = gtk.VBox(homogeneous=False)
        self.m_main_hbox = gtk.HBox()           # Hbox for padding
        self.m_main_hbox.pack_start(self.m_main_vbox, padding=self.m_consts.m_pad)
        #self.m_main_vbox.set_size_request(400,300)
        frame = gtk.Frame()
        frame.set_label(name)
        frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        self.m_hbox.add(frame)
        frame.add(self.m_main_hbox)
        
        # Initialise the buttons
        hbox = self.createCommandButtons()
        
         # Create the MPL canvas
        self.createMPLCanvas()     
           
        # Create the MPL toolbar
        self.m_mpl_toolbar = self.createMPLToolbar(self.m_canvas, window)
        self.m_main_vbox.pack_start(self.m_mpl_toolbar, expand=False)
        self.m_main_vbox.pack_start(self.m_canvas, padding=self.m_consts.m_pad)
        
        # Add the buttons after the plot
        self.m_main_vbox.pack_start(hbox, expand=False)
               
        # Create a scroller and plot list pane
        scroller = self.createPlotList()
        box = gtk.HBox(homogeneous=False)
        box.set_size_request(self.m_consts.x_lv,self.m_consts.y_lv)
        box.pack_start(scroller)
        self.m_main_vbox.pack_start(box, expand=False, \
                                    padding=self.m_consts.m_pad)
        
        # Add the series controller
        sidepane = SidePane(self)
        box.pack_start(sidepane.vbox, expand=False)
    
    def addColumn(self, title, colID):
        col = gtk.TreeViewColumn(title, gtk.CellRendererText(), \
                             text=colID)
        col.set_resizable(True)
        col.set_sort_column_id(colID)
        self.m_listview.append_column(col)
    
    
    def createMPLCanvas(self):        
        # Create the figure
        #self.m_figure = Figure(figsize=(5,4), dpi=100)
        self.m_figure = Figure()
        self.m_canvas = FigureCanvas(self.m_figure)
        self.initialisePlot()
    
    def initialisePlot(self):
        self.m_plotted = {}
        self.m_axes = self.m_figure.add_subplot(111)
        self.m_axes.set_xlabel(self.m_xlDefaul)
        self.m_figure.subplots_adjust(bottom=0.15)
        self.m_figure.subplots_adjust(left=0.15)
        self.toggleLogAxis(self.m_b_logx_toggle, "x")
        self.toggleLogAxis(self.m_b_logy_toggle, "y")
        self.m_canvas.draw()
    
    def createMPLToolbar(self, canvas, window):
        # Create the toolbar
        toolbar = NavToolbar(canvas, window)
        return toolbar
    
    def createCommandButtons(self):
        # Create handy buttons for plotting thins with MPL]
        
        self.m_b_plot_selection = gtk.Button("Plot selected")
        self.m_b_logx_toggle    = gtk.CheckButton("LogX?")
        self.m_b_logy_toggle    = gtk.CheckButton("LogY?")
        self.m_b_editor         = gtk.Button("Edit plot")
        self.m_b_reset          = gtk.Button("Reset")
        
        # Add some tooltips
        self.m_b_plot_selection.set_tooltip_text("Plot the selected series")
        self.m_b_logx_toggle.set_tooltip_text("Toggle Log10 x scale")
        self.m_b_logy_toggle.set_tooltip_text("Toggle log10 y scale")
        self.m_b_editor.set_tooltip_text("Open the plot editor")
        self.m_b_reset.set_tooltip_text("Reset the plot")
        
        # Connect some signals
        self.m_b_plot_selection.connect("clicked", self.plotSelected, None)
        self.m_b_logx_toggle.connect("toggled", self.toggleLogAxis, "x")
        self.m_b_logy_toggle.connect("toggled", self.toggleLogAxis, "y")
        self.m_b_editor.connect("clicked", self.editAxes, None)
        self.m_b_reset.connect("clicked", self.resetPlot, None)
        
        hbox = gtk.HBox(homogeneous=False)
        hbox.pack_start(self.m_b_plot_selection, expand=False)
        hbox.pack_start(self.m_b_logx_toggle, expand=False)
        hbox.pack_start(self.m_b_logy_toggle, expand=False)

        
        hbox.pack_end(self.m_b_reset, expand=False)
        hbox.pack_end(self.m_b_editor, expand=False)
        
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
    

    
    def plotSelected(self, widget, data=None):
        # Plots the selected series on the itemlist
        selection = self.m_listview.get_selection()
        if selection.count_selected_rows() > 0:
            (model, pathlist) = selection.get_selected_rows()
            
            id_list = []
            name_list = []
            unit_list = []
            
            for path in pathlist:
                id_list.append(model[path[0]][0])
                name_list.append(model[path[0]][1])
                unit_list.append(model[path[0]][2])
            
            if not checkListOfStrings(unit_list):
                if type(unit_list[0]) == type(1.0):
                    self.m_axes.set_ylabel("kernel density, 1/nm")
                    lines = []
                    for id in id_list:
                        lines.append(self.plotSeries(self.m_series_dict[id]))
                        self.m_plotted[id] = self.m_series_dict[id]
                else:
                    print("Wrong units being plotted on same axis!")
                    print("Nothing plotted.")
            else:
                self.m_axes.set_ylabel("parameter, {0}".format(unit_list[0]))
                lines = []
                for id in id_list:
                    lines.append(self.plotSeries(self.m_series_dict[id]))
                    self.m_plotted[id] = self.m_series_dict[id]
                    
    
    def plotSeries(self, series):
        # Displays the selected series in the MPL figure
        line = self.m_axes.plot(series.m_xvalues, series.m_yvalues, \
                         self.m_styles.getNextStyle(), label=series.m_name)
        #line[0].set_picker(True)
        self.m_axes.set_autoscale_on(True)
        self.m_axes.legend(loc=0, prop={'size':10})
        self.m_canvas.draw()
        return line
    
    def addSeries(self, serieslist):
        # Add a series to the plotlist from series list.
        
        for item in serieslist:
            # Get the ID of the run
            entry = [getNextIndex(self.m_series_dict)]
            entry += item.getPlotPaneList()
            
            # Add the series to the dictionary
            appendDict(self.m_series_dict, item)
            
            # Add it to the listview
            self.m_liststore.append(entry)
    
    def removeSelected(self):
        # Removes the selected series from the list
        
        selection = self.m_listview.get_selection()
        
        if selection.count_selected_rows() > 0:
            (model, pathlist) = selection.get_selected_rows()
            
            # Reverse doesn't seem to work?
            for path in reversed(pathlist):
                del self.m_liststore[path[0]]
        else:
            print("Nothing selected.")
    
    def clearSeries(self):
        # Clears all the series and resets the plot
        
        self.m_liststore.clear()
        for k in self.m_series_dict.keys():
            del self.m_series_dict[k]
        self.m_series_dict = {}
        
        self.resetPlot(None, None)
    
    def editAxes(self, widget, data=None):
        if not self.m_editOpen: editor = PlotEditor(self)
    
    def resetPlot(self, widget, data=None):
        # Removes all the lines from the figure
        for i in range(0, len(self.m_axes.lines)):
            self.m_axes.lines.pop(0)
        self.m_figure.clear()
        self.initialisePlot()
    
    def chooseSaveFile(self):
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
        filter.set_name("DSV files")
        filter.add_pattern("*.csv")
        filter.add_pattern("*.dat")
        filter.add_pattern("*.dsv")
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
            print 'Saving file cancelled!'
            filename = None
        
        dialog.destroy()
        
        return filename
    
    def setDelimiter(self, widget, data=None):
        # Sets the delimiter when saving files.
        print 1
    
    def saveSeries(self):
        # Saves the selected series
        
        selection = self.m_listview.get_selection()
        if selection.count_selected_rows() > 0:
            (model, pathlist) = selection.get_selected_rows()
            
            id_list = []
            name_list = []
            
            for path in pathlist:
                id_list.append(model[path[0]][0])
                name_list.append(model[path[0]][1])
            
            # Loop over all series to save them as a separate file
            for id in id_list:

                # Call file saver dialog
                oname = self.chooseSaveFile()
                if oname != None:
                    print("Saving file " + oname)
                    
                    parser = Out.DSVOut(oname)
                    data = self.m_series_dict[id].getOutputData()
                    parser.parseData(data, ",")
                    parser.close()
                    
                else:
                    print("File saving cancelled.")
        else:
            print "Nothing selected."

class TrajectoryPane(PlotPane):
    
    def createPlotList(self):
        # Create the liststore
        # Create the scroller
        scroller     = gtk.ScrolledWindow()
        scroller.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        scroller.set_shadow_type(gtk.SHADOW_IN)
        
        # Use columns: param / unit / PlotAvg / PlotCI
        self.m_liststore = gtk.ListStore(type(1), type("a"), type("a"))
        self.m_listview  = gtk.TreeView(self.m_liststore)
        self.m_listview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        scroller.add_with_viewport(self.m_listview)
        
        # Create columns
        self.addColumn("ID", 0) 
        self.addColumn("Parameter", 1)
        self.addColumn("Units", 2) 
        
        return scroller
    
    def toggleCIs(self, widget, data):
        # Activates plotting of CIs instead of averages
        print("Not implemented yet")
        if widget.get_active():
            pass
        else:
            pass
    
    def plotCIs(self, widget, data=None):
        # Plots the CIs of a dictionary of series
        
        for id in data.keys():
            pass

class PSDPane(PlotPane):
    
    def createPlotList(self):
        # Create the liststore
        # Create the scroller
        scroller     = gtk.ScrolledWindow()
        scroller.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        scroller.set_shadow_type(gtk.SHADOW_IN)
        
        # Use columns: param / unit / PlotAvg / PlotCI
        self.m_liststore = gtk.ListStore(type(1), type("a"), type(1.0), type("a"))
        self.m_listview  = gtk.TreeView(self.m_liststore)
        self.m_listview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        scroller.add_with_viewport(self.m_listview)
        
        # Create columns
        self.addColumn("ID", 0) 
        self.addColumn("Diam. Type", 1)
        self.addColumn("h", 2)
        self.addColumn("Parent", 3) 
        
        return scroller


class SidePane:
    # Pane for adding/removing individual series
    
    def __init__(self, pane):
        self.m_plotpane = pane
        
        self.vbox = gtk.VBox()
        
        # Create the toolbar
        toolbar = gtk.Toolbar()
        toolbar.set_style(gtk.TOOLBAR_ICONS)
        toolbar.set_orientation(gtk.ORIENTATION_VERTICAL)
        self.vbox.add(toolbar)
        
        # Delete button
        b_delete = gtk.ToolButton(gtk.STOCK_REMOVE)
        b_delete.set_tooltip_text("Delete series")
        b_delete.connect("clicked", self.deleteSeries, )
        toolbar.insert(b_delete, 0)
        
        # Add misc. series button
        b_add    = gtk.ToolButton(gtk.STOCK_ADD)
        b_add.set_tooltip_text("Add miscellaneous series")
        b_add.connect("clicked", self.addMiscSeries, )
        toolbar.insert(b_add, 1)
        
        # Clear all series button
        b_clear  = gtk.ToolButton(gtk.STOCK_CLEAR)
        b_clear.set_tooltip_text("Clear all series")
        b_clear.connect("clicked", self.clearAllSeries, )
        toolbar.insert(b_clear, 2)
        
        # Save selected series button
        b_save  = gtk.ToolButton(gtk.STOCK_SAVE)
        b_save.set_tooltip_text("Save selected series")
        b_save.connect("clicked", self.saveSeries, )
        toolbar.insert(b_save, 3)
        
    
    def deleteSeries(self, widget, data=None):
        # Deletes a series entry (or multiple)
        self.m_plotpane.removeSelected()
    
    def addMiscSeries(self, widget, data=None):
        # Adds a miscellaneous series from a data file
        Dlg.LoadMiscFileDialog(self.m_plotpane, self.m_plotpane.m_consts)
    
    def clearAllSeries(self, widget, data=None):
        self.m_plotpane.clearSeries()

    def saveSeries(self, widget, data=None):
        # Saves the selected series, defer to plotpane.
        self.m_plotpane.saveSeries()

class PlotEditor:
    # A class to edit the properties of a MPL plot in a PlotPane.
    
    def destroy(self, widget, data=None):
        self.m_window.destroy()
        self.m_pane.m_editOpen = False
    
    def __init__(self, pane):
        self.m_pane = pane
        self.m_axes = pane.m_axes
        self.m_canvas = pane.m_canvas
        pane.m_editOpen = True
        
        self.m_window = gtk.Window()
        self.m_window.connect("destroy", self.destroy, )
        #self.m_window.set_default_size(400,300)
        self.m_window.set_title("Edit plot characteristics..")
        
        box = gtk.VBox()
        self.m_window.add(box)
        
        padhbox = gtk.HBox()
        box.pack_start(padhbox, padding=self.m_pane.m_consts.m_pad)
        padvbox = gtk.VBox(homogeneous=False)
        padhbox.pack_start(padvbox, padding=self.m_pane.m_consts.m_pad)
        
        (self.xl_text, xl_but, xl_box) = self.createButtonEntry("Set x label")
        padvbox.pack_start(xl_box, fill=False, expand=False)
        xl_but.connect("clicked", self.setLabel, "x")
        (self.yl_text, yl_but, yl_box) = self.createButtonEntry("Set y label")
        padvbox.pack_start(yl_box, fill=False, expand=False)
        yl_but.connect("clicked", self.setLabel, "y")
        
        # CREATE X/Y LIMITS SETTERS
        (self.xr_min, self.xr_max, xr_but, xr_box) = self.createLimits("x")
        padvbox.pack_start(xr_box, fill=False, expand=False)
        xr_but.connect("clicked", self.setLimits, "x")
        
        (self.yr_min, self.yr_max, yr_but, yr_box) = self.createLimits("y")
        padvbox.pack_start(yr_box, fill=False, expand=False)
        yr_but.connect("clicked", self.setLimits, "y")
        
        self.m_window.show_all()
    
    def createButtonEntry(self, text):
        entry = gtk.Entry()
        button = gtk.Button(text)
        hbox = gtk.HBox(homogeneous=False)
        hbox.pack_start(entry, padding=2)
        hbox.pack_start(button, padding=2, fill=False)
        
        return (entry, button, hbox)
    
    def createLimits(self, text):
        # Creates fields for x/y limits
        hbox = gtk.HBox(homogeneous=False)
        
        label1 = gtk.Label("Min:")
        hbox.pack_start(label1)
        entry1 = gtk.Entry(10)
        hbox.pack_start(entry1, expand=False, \
                        padding=self.m_pane.m_consts.m_pad)
        
        label2 = gtk.Label("Max:")
        hbox.pack_start(label2)
        entry2 = gtk.Entry(10)
        hbox.pack_start(entry2, expand=False, \
                        padding=self.m_pane.m_consts.m_pad)
        
        button = gtk.Button("Set " + text + " limit")
        hbox.pack_start(button)
        
        return (entry1, entry2, button, hbox)
    
    def setLabel(self, widget, data):
        # Sets the x/y labels of the current axis
        if data == "x":
            text = self.xl_text.get_text()
            self.m_axes.set_xlabel(text)
        elif data == "y":
            text = self.yl_text.get_text()
            self.m_axes.set_ylabel(text)
            
        self.update()
    
    def setLimits(self, widget, data):
        
        if data == "x":
            if (self.xr_min.get_text() != "" and \
                self.xr_max.get_text() != ""):
                minval = float(self.xr_min.get_text())
                maxval = float(self.xr_max.get_text())
                self.m_axes.set_xlim(minval, maxval)
        elif data == "y":
            if (self.yr_min.get_text() != "" and \
                self.yr_max.get_text() != ""):
                minval = float(self.yr_min.get_text())
                maxval = float(self.yr_max.get_text())
                self.m_axes.set_ylim(minval, maxval)
        
        self.update()
    
    def update(self):
        self.m_canvas.draw()
        

class PlotStyles:
    styles = ["-", "--", "-.", ":"]
    
    cycler = cycle(styles)
    
    def getNextStyle(self):
        return next(self.cycler)

def checkListOfStrings(stringlist):
    # Checks if all the elements of a list are identical.
    if len(stringlist) < 2:
        if type(stringlist[0]) == type(1.0): return False
        return True
        
    else:
        val = stringlist[0]
        ans = True
        for item in stringlist[1:]:
            if val != item: ans = False
        return ans

def appendDict(dictionary, entry):
    dictionary[len(dictionary)] = entry

def getNextIndex(dictionary):
    if len(dictionary) < 1:
        return 0
    else:
        return max(dictionary.keys()) + 1
