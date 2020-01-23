#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
##################################################
##  N.E.Py.H. - Network Engineer Python Helper  ##
##################################################

This program uses a Database in YAML format and a Template in Jinja2 format in order to generate configuration.
It's mandatory that the YAML file start with a list.
Mainly though for Network Elements, the render is done by creating a file for each dictionary in the list.
The filename is the value of the first dictionary found in the list.

### Source code info:
This code follow PEP 8 style guide and it use 4 spaces for indentation.
"""

from PyQt5 import QtCore, QtWidgets, QtGui # import PyQt5 for GUI, to install 'pip3 install PyQt5'
from pathlib import Path
import os # import OS module to create directory
import errno
import sys
import time
import types
import shutil
import jinja2
import yaml
import io
import traceback
import logging
import ctypes.wintypes
import subprocess
import platform

__author__ = 'Emanuele Rossi'
__credits__ = ['cyb3rw0lf']
__appName__ = 'N.E.Py.H. - Network Engineer Python Helper'
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'Production'
__maintainer__ = 'cyb3rw0lf'
__homepage__ = 'https://github.com/cyb3rw0lf/nepyh'
__email__ = 'cyb3rw0lf@protonmail.com'
__issues__ = 'https://github.com/cyb3rw0lf/nepyh/issues'
__usage__ = ('Chose a Database file in YAML format and a Template file in Jinja2 format.\n'
             "It's mandatory that YAML file start with a list.")
__logfile__ = 'logfile.log'
__YAMLlint__ = 'http://www.yamllint.com/'

defFolder = time.strftime('%Y%m%d-%H%M%S')
script_path = Path(__file__).resolve().parent
__icon__ = str(script_path / 'assets' / 'nepyh_icon.png')


if platform.system() == 'Darwin':       # macOS
    myDocuments = script_path
elif platform.system() == 'Windows':    # Windows
    # Get My Documents folder path on Windows to write output files
    CSIDL_PERSONAL = 5       # My Documents
    SHGFP_TYPE_CURRENT = 0   # Get current, not default value
    myDoc = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, myDoc)
    myDocuments = Path(myDoc.value)
else:                                   # linux variants
    myDocuments = script_path


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
        documentationAction.setShortcut('F1')
        documentationAction.setStatusTip('Help and guidelines on NEPyH')
        documentationAction.triggered.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl(__homepage__)))

        # Menubar YAML lint action:
        yamllintAction = QtWidgets.QAction('&YAML lint', self)
        yamllintAction.setStatusTip('Online YAML validation tool')
        yamllintAction.triggered.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl(__YAMLlint__)))
        
        # Menubar Issues action:
        issuesAction = QtWidgets.QAction('&Issues', self)
        issuesAction.setStatusTip('Report bugs and issues')
        issuesAction.triggered.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl(__issues__)))

        # Menubar SW Upgrade action:
        swupgradeAction = QtWidgets.QAction('&SW Upgrade', self)
        swupgradeAction.setStatusTip('Check for new software versions')

        # Menubar About action:
        aboutAction = QtWidgets.QAction('&About', self)
        aboutAction.setStatusTip('Information about NEPyH')
        aboutAction.triggered.connect(lambda: self.about())

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
        helpMenu.addAction(yamllintAction)
        helpMenu.addAction(issuesAction)
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
        self.databaseLb = QtWidgets.QLabel('Database: (YAML)')
        self.templateLb = QtWidgets.QLabel('Template: (Jinja2)')
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
        self.databaseBtn.clicked.connect(self.getdbPath)
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
        self.setWindowTitle(__appName__)
        self.setWindowIcon(QtGui.QIcon(__icon__))
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
        #      'Are you sure to quit?', QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        # if reply == QtWidgets.QMessageBox.Yes:
        #     event.accept()
        # else:
        #     event.ignore()

    def about(self):
        aboutMsg = QtWidgets.QMessageBox()
        aboutMsg.setWindowTitle('About')
        aboutMsg.setText(__appName__ + '\n\n' + 
                         'Author: ' + __author__ + '\n' + 
                         'Version: ' + __version__ + '\n' +
                         'License: ' + __license__ + '\n\n' +
                         __homepage__ + '\n'
                        )
        aboutMsg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        # aboutMsg.adjustSize()
        aboutMsg.exec_()

    def openFile(self, filepath):
        if platform.system() == 'Darwin':       # macOS
            subprocess.call(('open', filepath))
        elif platform.system() == 'Windows':    # Windows
            os.startfile(filepath)
        else:                                   # linux variants
            subprocess.call(('xdg-open', filepath))

    def getdbPath(self):
        self.databaseEdit.setText(QtWidgets.QFileDialog.getOpenFileName(self, 'Select file', '.', '*.yml')[0])

    def gettpPath(self):
        self.templateEdit.setText(QtWidgets.QFileDialog.getOpenFileName(self, 'Select file', '.', '*.j2')[0])

    def checkdir(self, out_path): # This function will check if the destination folder already exist and create one if not
        success = False
        attempts = 0
        while attempts < 3 and not success:
            try:
                os.makedirs(out_path)
                success = True
            except OSError as exc:
                if exc.errno == errno.EEXIST:
                    reply = QtWidgets.QMessageBox.question(self, 'Warning',
                    'Project folder already exists and will be overwritten, continue?',
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
                    if reply == QtWidgets.QMessageBox.Yes:
                        shutil.rmtree(out_path)
                    else:
                        return
                elif exc.errno == 13:
                    errorArgs = 'One of the files is already in use, please close the application and try again.\n'
                    errorArgs = errorArgs + str(exc.args)
                    logging.debug(errorArgs)
                    attempts += 1
                else:
                    logging.debug(str(exc.args))
                    attempts += 1

    def updateDefFolder(self):
        defFolder = time.strftime('%Y%m%d-%H%M%S')
        self.projectEdit.setText(defFolder)

    def handleErrors(self, errorText, errorArgs):
        logging.error(errorText + errorArgs)
        err_msg = QtWidgets.QMessageBox()
        err_msg.setIcon(QtWidgets.QMessageBox.Critical)
        err_msg.setWindowTitle('Error')
        err_msg.setText(errorText)
        err_msg.setDetailedText(errorArgs)
        err_msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        err_msg.exec_()

    def excepthook(excType, excValue, tracebackobj):
        """
        Global function to catch unhandled exceptions.
        
        @param excType exception type
        @param excValue exception value
        @param tracebackobj traceback object
        """
        infoVersion = 'Version: %s \n' % __version__
        separator = '-' * 80
        notice = ('An unhandled exception occurred.\n' + 
                 'Please report the problem via email to <%s>\n' 
                 'A log has been written to %s\n\n'
                 'Expand for more details:') % (__email__, __logfile__)
        timeString = time.strftime("%Y-%m-%d, %H:%M:%S")
        
        tbinfofile = io.StringIO()
        traceback.print_tb(tracebackobj, None, tbinfofile)
        tbinfofile.seek(0)
        tbinfo = tbinfofile.read()
        errmsg = '%s: \n%s' % (str(excType), str(excValue))
        sections = [separator, timeString, separator, errmsg, separator, tbinfo]
        msg = '\n'.join(sections)
        logging.error(infoVersion + msg)
        errorbox = QtWidgets.QMessageBox()
        errorbox.setIcon(QtWidgets.QMessageBox.Critical)
        errorbox.setWindowTitle('Unhandled Error')
        errorbox.setText(notice)
        errorbox.setDetailedText(str(infoVersion) + str(msg))
        errorbox.exec_()
    
    sys.excepthook = excepthook
    
    def config_gen(self): # This function cover the config generator
        # out_path = script_path / 'outputs' / Path(self.projectEdit.text())
        out_path = myDocuments / 'NEPyH_Outputs' / Path(self.projectEdit.text())
        db_path = self.databaseEdit.text()
        tp_path = Path(self.templateEdit.text()).parent
        tp_name = Path(self.templateEdit.text()).name
        fileExt = self.fileExtEdit.text()

        self.checkdir(out_path)
        
        # Load data from YAML into Python dictionary
        logging.info('Load YAML database...')
        try:
            input_db=yaml.load(open(db_path), Loader=yaml.SafeLoader)
        except yaml.YAMLError as exc:
            errorText = ('An error occurred while parsing YAML file\n\n'
                         'Please correct data and retry.\n')
            if hasattr(exc, 'problem_mark'):
                if exc.context != None:
                    errorArgs = ('Parser says:\n'
                                 '%s\n'
                                 '%s %s\n\n'
                                 'Use lint to validate your code: %s'
                                % (str(exc.problem_mark), str(exc.problem), str(exc.context), __YAMLlint__))
                    self.handleErrors(errorText, errorArgs)
                    return
                else:
                    errorArgs = ('Parser says:\n'
                                 '%s\n'
                                 '%s\n\n'
                                 'Use lint to validate your code: %s'
                                 % (str(exc.problem_mark), str(exc.problem), __YAMLlint__))
                    self.handleErrors(errorText, errorArgs)
                    return

        # Load Jinja2 template
        logging.info('Create Jinja2 Environment...')
        env = jinja2.Environment(loader = jinja2.FileSystemLoader(str(tp_path)), trim_blocks=True, lstrip_blocks=True)
        
        logging.info('Load Jinja2 Template...')
        try:
            input_tp = env.get_template(tp_name)
        except jinja2.TemplateNotFound:
            errorText = tp_name + ': File not found\n'
            errorArgs = "File '%s' not found in %s\n" % (tp_name, str(tp_path))
            self.handleErrors(errorText, errorArgs)
            return
        except jinja2.TemplateSyntaxError as exc:
            errorText = ('An error occurred while reading Jinja2 template\n\n'
                         'Please correct data and retry.\n')
            errorArgs = ('Syntax check failed:\n'
                         ' %s '
                         'in %s at line %d'
                         % (exc.message, exc.filename, exc.lineno))
            self.handleErrors(errorText, errorArgs)
            return

        # Render the template with data and print the output
        logging.info('Rendering templates...')
        try:
            for entry in input_db:
                result = input_tp.render(entry)
                out_file_name=next(iter(entry.values())) + fileExt
                out_file = open(out_path / out_file_name, 'w')
                out_file.write(result)
                out_file.close()
                logging.info("Configuration '%s' created..." % (out_file_name))
        except ValueError as exc:
            errorText = ('An error occurred while rendering the templates\n'
                         'The YAML file must start with a list of dictionary\n\n'
                         'Please correct data and retry.\n')
            errorArgs = (str(traceback.format_exc()))
            self.handleErrors(errorText, errorArgs)
            return
        end_msg = QtWidgets.QMessageBox()
        end_msg.setIcon(QtWidgets.QMessageBox.Information)
        end_msg.setWindowTitle('Task Finished')
        end_msg.setText("\nProject '%s' completed!\n\n"
                        'The files have been generated in the folder: \n'
                        "  '%s'\n" % (self.projectEdit.text(), str(out_path)))
        end_msg.setDetailedText('< print partial logs from last config_gen() >')
        end_msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Open)
        result = end_msg.exec_()
        if result == QtWidgets.QMessageBox.Open:
            self.openFile(str(out_path))

def bind(func, to):
    'Bind function to instance, unbind if needed'
    return types.MethodType(func.__func__ if hasattr(func, '__self__') else func, to)

def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)-15s %(levelname)-8s %(message)s',
        handlers=[
        logging.FileHandler(__logfile__.format(), mode='w'),
        logging.StreamHandler()
        ])
    logging.info('Session Started')
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainGUI()
    status = app.exec_()
    logging.info('Session Finished')
    sys.exit(status)

if __name__ == '__main__':
    main()

