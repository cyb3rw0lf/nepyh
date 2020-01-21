#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
##############################################
### N.E.Py.H. - Network Engineer Python Helper ###
##############################################

This program uses a Database in YAML format and a Template in Jinja2 format in order to generate configuration.
It's mandatory that the YAML file start with a list.
Mainly though for Network Elements, the render is done by creating a file for each dictionary in the list.
The filename is the value of the first dictionary found in the list.

### Source code info:
This code follow PEP 8 style guide and it use 4 spaces for indentation.
"""

import os # import OS module to create directory
import errno
import sys
import time
from PyQt5 import QtCore, QtWidgets, QtGui # import PyQt5 for GUI, to install "pip3 install PyQt5"
import types
import shutil
import jinja2
import yaml
from pathlib import Path

__author__ = "Emanuele Rossi a.k.a. cyb3rw0lf"
__credits__ = ["cyb3rw0lf"]

__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "cyb3rw0lf"
__homepage__ = "https://github.com/cyb3rw0lf/nepyh"
__email__ = "cyb3rw0lf@protonmail.com"
__issues__ = "https://github.com/cyb3rw0lf/nepyh/issues"
__status__ = "Production"
__usage__ = "Chose a Database file in YAML format and a Template file in Jinja2 format. It's mandatory that YAML file start with a list."

defFolder = time.strftime("%Y%m%d-%H%M%S")
script_path = Path(__file__).resolve().parent

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
        self.setWindowTitle('NEPyH - Network Engineer Python Helper v' + __version__)
        self.setWindowIcon(QtGui.QIcon(str(script_path / 'nepyh.png')))
        self.show()

    def center(self): # Move the main window to the center of the screen
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        event.accept()
        # Ask for exit confirmation when click on 'x' button 
        # reply = QtWidgets.QMessageBox.question(self, 'Message',
        #      "Are you sure to quit?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        # if reply == QtWidgets.QMessageBox.Yes:
        #     event.accept()
        # else:
        #     event.ignore()

    def getcsvPath(self):
        self.databaseEdit.setText(QtWidgets.QFileDialog.getOpenFileName(self, "Select file", '.', "*.yml")[0])

    def gettpPath(self):
        self.templateEdit.setText(QtWidgets.QFileDialog.getOpenFileName(self, 'Select file', '.', "*.j2")[0])

    def checkdir(self, out_path): # This function will check if the destination folder already exist and create one if not
        try:
            os.makedirs(out_path)
        except OSError as exception:
            if exception.errno == errno.EEXIST:
                reply = QtWidgets.QMessageBox.question(self, 'Message',
                 "Project folder already exists and will be overwritten, continue?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
                if reply == QtWidgets.QMessageBox.Yes:
                    shutil.rmtree(out_path)
                    self.checkdir(out_path)
            elif exception.errno != errno.EEXIST:
                self.allerrors(OSError.args)
                raise

    def updateDefFolder(self):
        defFolder = time.strftime("%Y%m%d-%H%M%S")
        self.projectEdit.setText(defFolder)

    def allerrors(self, errorArgs):
        err_msg = QtWidgets.QMessageBox()
        err_msg.setIcon(QtWidgets.QMessageBox.Critical)
        err_msg.setWindowTitle("Error")
        err_msg.setText("Project " + self.projectEdit.text() + " failed with unhandled error!")
        err_msg.setDetailedText(errorArgs)
        err_msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        err_msg.adjustSize()
        err_msg.exec_()

    def config_gen(self): # This function cover the config generator
        out_path = script_path / 'outputs' / Path(self.projectEdit.text())
        db_path = self.databaseEdit.text()
        tp_path = Path(self.templateEdit.text()).parent
        tp_name = Path(self.templateEdit.text()).name
        fileExt = self.fileExtEdit.text()

        self.checkdir(out_path)
        
        # Load data from YAML into Python dictionary
        print("Load YAML database...")
        try:
            input_db=yaml.load(open(db_path), Loader=yaml.SafeLoader)
        except yaml.YAMLError as exc:
            errorArgs = "Error while parsing YAML file:"
            if hasattr(exc, "problem_mark"):
                if exc.context != None:
                    errorArgs = errorArgs + "  parser says\n" + str(exc.problem_mark) + "\n  " + str(exc.problem) + " " + str(exc.context) + "\nPlease correct data and retry."
                    print(errorArgs)
                    self.allerrors(errorArgs)
                else:
                    errorArgs = errorArgs + "  parser says\n" + str(exc.problem_mark) + "\n  " + str(exc.problem) + "\nPlease correct data and retry."
                    print(errorArgs)
                    self.allerrors(errorArgs)
            else:
                errorArgs = errorArgs + str(exc.args)
                print(errorArgs)
                self.allerrors(errorArgs)
            return

        # Load Jinja2 template
        print("Create Jinja2 Environment...")
        try:
            env = jinja2.Environment(loader = jinja2.FileSystemLoader(str(tp_path)), trim_blocks=True, lstrip_blocks=True)
        except jinja2.TemplateError as exc:
            errorArgs = "Error while loading Jinja2 Environment:"
            errorArgs = errorArgs + str(exc.args)
            print(errorArgs)
            self.allerrors(errorArgs)
            return
        
        print("Load Jinja2 Template...")
        try:
            input_tp = env.get_template(tp_name)
        except jinja2.TemplateSyntaxError as exc:
            errorArgs = "Syntax Error while parsing Jinja2 template:"
            errorArgs = errorArgs + str(exc.args)
            print(errorArgs)
            self.allerrors(errorArgs)
            return
        except jinja2.TemplateError as exc:
            errorArgs = "Template Error while parsing Jinja2 template:"
            errorArgs = errorArgs + str(exc.args)
            print(errorArgs)
            self.allerrors(errorArgs)
            return

        # Render the template with data and print the output
        print("Rendering templates...")
        for entry in input_db:
            result = input_tp.render(entry)
            out_file_name=next(iter(entry.values())) + fileExt
            out_file = open(out_path / out_file_name, 'w')
            out_file.write(result)
            out_file.close()
            print("Configuration '%s' created..." % (out_file_name))
        end_msg = QtWidgets.QMessageBox()
        end_msg.setIcon(QtWidgets.QMessageBox.Information)
        end_msg.setWindowTitle("Task Finished")
        end_msg.setText("Project " + self.projectEdit.text() + " completed!\nThe files have been generated in the folder:\n" + str(out_path))
        end_msg.setDetailedText("< put logs here >")
        end_msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        end_msg.adjustSize()
        end_msg.exec_()

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

