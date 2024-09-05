import pandas as pd
from qgis.PyQt.QtWidgets import QMessageBox
from PyQt5.QtWidgets import  QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from .database_functions import save_to_db, create_code

#################################################################################################
#                                                                                               #
#                                  Profile creator (Profiles)                                   #
#                                                                                               #
#################################################################################################

def setup_profile_creator(self, dlg, db_dict, db_path):

    def fill_cbox():
        dlg.comboBoxRef.clear()
        # dlg.comboBoxProfType.clear()
        # dlg.comboBoxDay.clear()
        dlg.comboBoxBaseProfile.clear()
        
        dlg.comboBoxRef.addItems(sorted(db_dict['References']['authorYear'])) 
        dlg.comboBoxRef.setCurrentIndex(-1)
        dlg.comboBoxProfType.setCurrentIndex(-1)
        dlg.comboBoxDay.setCurrentIndex(-1)
        dlg.comboBoxBaseProfile.setCurrentIndex(1)

    def prof_type_changed():
        prof_type = dlg.comboBoxProfType.currentText()
        dlg.comboBoxBaseProfile.clear()
        dlg.comboBoxDay.setCurrentIndex(1)
        day = dlg.comboBoxDay.currentText()

        prof_types = db_dict['Profiles'][db_dict['Profiles']['Profile Type'] == prof_type]
        prof_types = prof_types['descOrigin'][db_dict['Profiles']['Day'] == day]
        dlg.comboBoxBaseProfile.addItems(prof_types.tolist())
    
    def day_changed():
        day = dlg.comboBoxDay.currentText()
        prof_type = dlg.comboBoxProfType.currentText()
        dlg.comboBoxBaseProfile.clear()

        prof_types = db_dict['Profiles'][db_dict['Profiles']['Profile Type'] == prof_type]
        prof_types = prof_types['descOrigin'][db_dict['Profiles']['Day'] == day]

        dlg.comboBoxBaseProfile.addItems(prof_types.tolist())
        dlg.comboBoxBaseProfile.setEnabled(True)

    def base_prof_changed():
        base_prof = dlg.comboBoxBaseProfile.currentText()
        prof_sel = db_dict['Profiles'][(db_dict['Profiles']['descOrigin'] == base_prof) & (db_dict['Profiles']['Day'] == dlg.comboBoxDay.currentText()) & (db_dict['Profiles']['Profile Type'] == dlg.comboBoxProfType.currentText())]
        prof_sel.columns = prof_sel.columns.map(str)
        prof_sel_dict = prof_sel.squeeze().to_dict()

        plotValues = []
        for i in range(0,24):
            Tb = eval('dlg.textBrowser_' + str(i))
            Le = eval('dlg.lineEdit_' + str(i))
            Le.clear()
            Le.setText(str(prof_sel_dict[str(Tb.toPlainText())]))
            # str(prof_sel_dict[str(Tb.toPlainText())])
            # 
            try:
                plotValues.append(float(prof_sel_dict[str(Tb.toPlainText())]))
            except:
                pass
        
        ## Plot the profile
        # Create dataframe from selected profile values
        prof_df = pd.DataFrame(plotValues)
        # Check if df is empty to avoid errors from trying to plot nans
        # TODO Make a plot showing NAN values or make sure that nan is instead -9999 in Database
        if prof_df.empty is True:
            pass
        else:
            # Check if plotViewer.layout() exists, to be sure that no errors are given when cleaning
            if dlg.plotViewer.layout() is None:
                    layout = QVBoxLayout(dlg.plotViewer)
                    dlg.plotViewer.setLayout(layout)
            else:
                layout = dlg.plotViewer.layout()
            
            # clean dlg.plotViewer
            for i in reversed(range(layout.count())):
                plt.close()
                widget_to_remove = layout.itemAt(i).widget()
                layout.removeWidget(widget_to_remove)
                widget_to_remove.setParent(None)
            
            # Create plot from dataframe
            fig, ax = plt.subplots()
            # Adjust figure size # THIS MIGHT NEED TO CHANGE. Check at more screens than just one..
            fig.subplots_adjust(0.1, 0.2, 0.9, 1)
            prof_df.plot(ax = ax,
                    legend=None)
            ax.set_xlim([0,23])
            ax.set_xticks([0,6,12,18,23])
            ax.minorticks_on()
            ax.set_xlabel('Hours')
            # Add plot to FigureCanvas object and add to layout Widget
            canvas = FigureCanvas(fig)
            plt.close()
            layout.addWidget(canvas)
    
    def update_plot():
        a =  dlg.comboBoxProfType.currentText() # Not sure why this has to be here, but if i remove it, nothing works...

        plotValues = []
        for i in range(0, 24): 
            Le = eval('dlg.lineEdit_' + str(i))
            val = Le.text()
            plotValues.append(float(val))

        prof_df = pd.DataFrame(plotValues)

        if dlg.plotViewer.layout() is None:
                layout = QVBoxLayout(dlg.plotViewer)
                dlg.plotViewer.setLayout(layout)
        else:
            layout = dlg.plotViewer.layout()
        
        # clean dlg.plotViewer
        for i in reversed(range(layout.count())):
            plt.close()
            widget_to_remove = layout.itemAt(i).widget()
            layout.removeWidget(widget_to_remove)
            widget_to_remove.setParent(None)
        
        # Create plot from dataframe
        fig, ax = plt.subplots()
        # Adjust figure size # THIS MIGHT NEED TO CHANGE. Check at more screens than just one..
        fig.subplots_adjust(0.1, 0.2, 0.9, 1)
        prof_df.plot(ax = ax,
                legend=None)
        ax.set_xlim([0,23])
        ax.set_xticks([0,6,12,18,23])
        ax.minorticks_on()
        ax.set_xlabel('Hours')
        # Add plot to FigureCanvas object and add to layout Widget
        canvas = FigureCanvas(fig)
        plt.close()
        layout.addWidget(canvas)

        
    def ref_changed():
        dlg.textBrowserRef.clear()

        try:
            ID = db_dict['References'][db_dict['References']['authorYear'] ==  dlg.comboBoxRef.currentText()].index.item()
            dlg.textBrowserRef.setText(
                '<b>Author: ' +'</b>' + str(db_dict['References'].loc[ID, 'Author']) + '<br><br><b>' +
                'Year: ' + '</b> '+ str(db_dict['References'].loc[ID, 'Year']) + '<br><br><b>' +
                'Title: ' + '</b> ' +  str(db_dict['References'].loc[ID, 'Title']) + '<br><br><b>' +
                'Journal: ' + '</b>' + str(db_dict['References'].loc[ID, 'Journal']) + '<br><br><b>'
            )
        except:
            pass
    def add_profile():

        dict_reclass = {
            'ID' : create_code('Profiles'),
            'General Type' : 'Reg',
            'Profile Type' : dlg.comboBoxProfType.currentText(), 
            'Day' : dlg.comboBoxDay.currentText(),
            'Description' : dlg.textEditDesc.value(),
            'Origin' : dlg.textEditOrig.value(),
            'Ref' : db_dict['References'][db_dict['References']['authorYear'] ==  dlg.comboBoxRef.currentText()].index.item() 
        }

        for i in range(0, 24): 
            Tb = eval('dlg.textBrowser_' + str(i))
            Le = eval('dlg.lineEdit_' + str(i))
            col = Tb.toPlainText()
            val = Le.text()
            dict_reclass[col] = val

        dict_reclass['Ref'] = db_dict[  'References'][db_dict['References']['authorYear'] ==  dlg.comboBoxRef.currentText()].index.item() 
        new_edit = pd.DataFrame([dict_reclass]).set_index('ID')
        db_dict['Profiles'] = pd.concat([db_dict['Profiles'], new_edit])
    
        # Write to db
        save_to_db(db_path, db_dict)

        QMessageBox.information(None, 'Succesful', 'Profile Entry added to your local database')
        fill_cbox()
    
    def tab_update():
        if self.dlg.tabWidget.currentIndex() == 5:
            fill_cbox()

    def to_ref_edit():
        self.dlg.tabWidget.setCurrentIndex(10)
    

    dlg.pushButtonToRefManager.clicked.connect(to_ref_edit)
    self.dlg.tabWidget.currentChanged.connect(tab_update)
    dlg.pushButtonGen.clicked.connect(add_profile)
    dlg.pushButtonUpdatePlot.clicked.connect(update_plot)
    dlg.comboBoxRef.currentIndexChanged.connect(ref_changed) 
    dlg.comboBoxProfType.currentIndexChanged.connect(prof_type_changed)
    dlg.comboBoxBaseProfile.currentIndexChanged.connect(base_prof_changed)
    dlg.comboBoxDay.currentIndexChanged.connect(day_changed)
