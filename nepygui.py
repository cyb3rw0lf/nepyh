#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
##############################################
### NEPyH - Network Engineer Python Helper ###
##############################################

Author: Emanuele Rossi 
Contact: emanuele.rossi@huawei.com
Website: 

### Source code info:
This code follow PEP 8 style guide and it use 4 spaces for indentation.


NEPyH has three functions: Config generator, shut/no shut interfaces, pre/post check analysis

### Config generator:

Description:

Usage:

### Shut / No Shut interfaces:

Description:

Usage:


### Pre/Post checks:

Description:

Usage:


"""


import os # import OS module to create directory
import errno
import pandas as pd # import pandas for DataFrame management, to install "pip3 install pandas"
import sys
import time
from PyQt5 import QtCore, QtWidgets, QtGui # import PyQt5 for GUI, to install "pip3 install PyQt5"
import types
import shutil

version = "alpha-2.1"
defFolder = time.strftime("%Y%m%d-%H%M%S")

# GUI
class MainGUI(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainGUI, self).__init__()

        # Create empty text box
        #textEdit = QtWidgets.QTextEdit()
        #self.setCentralWidget(textEdit)

        # Menubar Quit action:
        quitAction = QtWidgets.QAction('&Quit', self)
        quitAction.setShortcut('Ctrl+Q')
        quitAction.setStatusTip('Exit application')
        quitAction.triggered.connect(QtWidgets.qApp.quit)

        # Menubar Documentation action:
        documentationAction = QtWidgets.QAction('&Documentation', self)
        documentationAction.setStatusTip('Help and guidelines on NEPyH')

        # Menubar SW Upgrade action:
        swupgradeAction = QtWidgets.QAction('&SW Upgrade', self)
        swupgradeAction.setStatusTip('Check for new software versions')

        # Menubar About action:
        aboutAction = QtWidgets.QAction('&About', self)
        aboutAction.setStatusTip('Information about NEPyH')

        # Create a status bar
        self.statusBar()

        # Create a menu bar
        menubar = self.menuBar()

        # Menubar File
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(quitAction)

        # Menubar Help
        helpMenu = menubar.addMenu('&Help')
        helpMenu.addAction(documentationAction)
        helpMenu.addAction(swupgradeAction)
        helpMenu.addAction(aboutAction)

        # Create a toolbar
        #toolbar = self.addToolBar('CFG Gen')
        #toolbar.addAction(changeLayoutCFG)
        #toolbar = self.addToolBar('Shut / No Shut')

        # Create a central Widgets
        centralWidget = QtWidgets.QWidget()

        # Create a Layout for the central Widget
        centralLayout = QtWidgets.QGridLayout()

        # Config generator Layout elements
        self.databaseLb = QtWidgets.QLabel('Database:')
        self.templateLb = QtWidgets.QLabel('Template:')
        self.projectLb = QtWidgets.QLabel('Project name:')
        self.fileExtLb = QtWidgets.QLabel('Output file extension:')

        self.databaseEdit = QtWidgets.QLineEdit()
        self.templateEdit = QtWidgets.QLineEdit()
        self.projectEdit = QtWidgets.QLineEdit(defFolder)
        # This is needed to select all text when click on LineEdit
        self.projectEdit.focusInEvent = bind(lambda w, e: QtCore.QTimer.singleShot(0, w.selectAll), self.projectEdit)
        self.fileExtEdit = QtWidgets.QLineEdit('.txt')
        # This is needed to select all text when click on LineEdit
        self.fileExtEdit.focusInEvent = bind(lambda w, e: QtCore.QTimer.singleShot(0, w.selectAll), self.fileExtEdit)

        self.databaseBtn = QtWidgets.QPushButton('Browse')
        self.databaseBtn.clicked.connect(self.getcsvPath)
        self.templateBtn = QtWidgets.QPushButton('Browse')
        self.templateBtn.clicked.connect(self.gettpPath)
        self.projectBtn = QtWidgets.QPushButton('Update')
        self.projectBtn.clicked.connect(self.updateDefFolder)
        self.cfgenBtn = QtWidgets.QPushButton('Run')
        self.cfgenBtn.clicked.connect(self.config_gen)

        # Config generator Layout
        cfgenLayout = QtWidgets.QGridLayout()
        cfgenLayout.setSpacing(10)
        cfgenLayout.addWidget(self.databaseLb, 1, 0)
        cfgenLayout.addWidget(self.databaseEdit, 1, 1)
        cfgenLayout.addWidget(self.databaseBtn, 1, 2)

        cfgenLayout.addWidget(self.templateLb, 2, 0)
        cfgenLayout.addWidget(self.templateEdit, 2, 1)
        cfgenLayout.addWidget(self.templateBtn, 2, 2)

        cfgenLayout.addWidget(self.projectLb, 3, 0)
        cfgenLayout.addWidget(self.projectEdit, 3, 1)
        cfgenLayout.addWidget(self.projectBtn, 3, 2)

        cfgenLayout.addWidget(self.fileExtLb, 4, 0)
        cfgenLayout.addWidget(self.fileExtEdit, 4, 1)

        cfgenLayout.addWidget(self.cfgenBtn, 4, 2)

        # Set the default Layout
        #centralWidget.setLayout(centralLayout)
        centralWidget.setLayout(cfgenLayout)

        # Set the Widget
        self.setCentralWidget(centralWidget)

        # Set main windows size, position, title and icons
        self.resize(600,10)
        self.center()
        self.setWindowTitle('NEPyH - Network Engineer Python Helper v'+version)
        self.setWindowIcon(QtGui.QIcon('nepyh.png'))
        self.show()

    def center(self): # Move the main window to the center of the screen
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event): # Ask for exit confirmation when click on 'x' button 
        reply = QtWidgets.QMessageBox.question(self, 'Message',
             "Are you sure to quit?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def getcsvPath(self):
        self.databaseEdit.setText(QtWidgets.QFileDialog.getOpenFileName(self, "Select file", '.', "*.csv")[0])

    def gettpPath(self):
        self.templateEdit.setText(QtWidgets.QFileDialog.getOpenFileName(self, 'Select file', '.')[0])

    def checkdir(self): # This function will check if the destination folder already exist and create one if not
        out_path = self.projectEdit.text()

        try:
            os.makedirs(out_path)
        except OSError as exception:
            if exception.errno == errno.EEXIST:
                reply = QtWidgets.QMessageBox.question(self, 'Message',
                 "Project folder already exists and will be overwritten, continue?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
                if reply == QtWidgets.QMessageBox.Yes:
                    shutil.rmtree(out_path)
                    self.checkdir()
            elif exception.errno != errno.EEXIST:
                QtWidgets.QErrorMessage.showMessage(OSError.args)
                raise

    def updateDefFolder(self):
        defFolder = time.strftime("%Y%m%d-%H%M%S")
        self.projectEdit.setText(defFolder)

    def config_gen(self): # This function cover the config generator
        
        out_path = self.projectEdit.text()
        db_path = self.databaseEdit.text()
        tp_path = self.templateEdit.text()
        fileExt = self.fileExtEdit.text()

        self.checkdir()

        input_db=pd.read_csv(db_path) # load csv file in pandas DataFrame
        
        # Loop for all rows in the DataFrame, create one file for each row using the first column value as filename.
        # If the file already exist, it just append the output.
        for rows in input_db.index:
            hostname=input_db.iloc[rows,0]
            out_file=open(out_path + '/' + hostname + fileExt, 'a')
            input_tp=open(tp_path, 'r')
            
            # Write on the file the row readed during the job
            #out_file.write('# Output from row ' + str(rows) + '\n')
           
            for line in input_tp: # loop for all input file lines
                for i in input_db.columns: # loop for all csv header columns use the column name as string to be replaced with column values
                    line=line.replace(i,str(input_db.loc[rows,i]))
                out_file.write(line)
            out_file.write('\n')
            input_tp.close()
            out_file.close()
        QtWidgets.QMessageBox.about(self, "Task finished", "The job related with project " + self.projectEdit.text() + "is completed!") 

def bind(func, to):
    "Bind function to instance, unbind if needed"
    return types.MethodType(func.__func__ if hasattr(func, "__self__") else func, to)

def main():
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainGUI()
    status = app.exec_()
    sys.exit(status)

if __name__ == '__main__':
    main()

