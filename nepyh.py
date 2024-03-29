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

# Source code info:
This code follow PEP 8 style guide and it use 4 spaces for indentation.
"""

from PyQt6 import QtCore, QtWidgets, QtGui  # import PyQt6 for GUI
from pathlib import Path
from netaddr import IPNetwork  # used for custom Jinja2 templates
import os  # import OS module to create directory
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
__version__ = 'v1.0.4-beta'
__status__ = 'Production'
__maintainer__ = 'cyb3rw0lf'
__homepage__ = 'https://github.com/cyb3rw0lf/nepyh'
__email__ = 'w0lf.code@pm.me'
__issues__ = 'https://github.com/cyb3rw0lf/nepyh/issues'
__usage__ = ('Chose a Database file in YAML format and a Template file in Jinja2 format.\n'
             "It's mandatory that YAML file start with a list.")
__logfile__ = f'{Path(__file__).stem}.log'
__YAMLlint__ = 'http://www.yamllint.com/'

script_path = Path(__file__).resolve().parent
__icon__ = os.path.join(script_path, 'assets', 'nepyh_icon.png')
defFolder = time.strftime('%Y%m%d-%H%M%S')


# Output files are written inside My Documents folder for Windows and inside script folder for Mac OS and Linux
if platform.system() == 'Darwin':       # macOS
    myDocuments = script_path
elif platform.system() == 'Windows':    # Windows
    # Get My Documents folder path on Windows
    CSIDL_PERSONAL = 5       # My Documents
    SHGFP_TYPE_CURRENT = 0   # Get current, not default value
    myDoc = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, myDoc)
    myDocuments = Path(myDoc.value)
else:                                   # linux variants
    myDocuments = script_path


###############################
##     START of GUI code     ##
###############################

# Drag and Drop filename to QLineEdit
class DragDropQLineEdit(QtWidgets.QLineEdit):
    def __init__(self, title, parent, fileType):
        super().__init__(title, parent)
        self.fileType = fileType
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = []
        for url in event.mimeData().urls():
            files.append(url.toLocalFile())
        setValidFile(self.fileType, files[0], self)

# Main GUI


class MainGUI(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainGUI, self).__init__()

        # Create empty text box
        # textEdit = QtWidgets.QTextEdit()
        # self.setCentralWidget(textEdit)

        # Menubar Quit action:
        quitAction = QtGui.QAction('&Quit', self)
        quitAction.setShortcut('Ctrl+Q')
        quitAction.setStatusTip('Exit application')
        quitAction.triggered.connect(QtWidgets.QApplication.quit)

        # Menubar Documentation action:
        documentationAction = QtGui.QAction('&Documentation', self)
        documentationAction.setShortcut('F1')
        documentationAction.setStatusTip('Help and guidelines on NEPyH')
        documentationAction.triggered.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl(__homepage__)))

        # Menubar YAML lint action:
        yamllintAction = QtGui.QAction('&YAML lint', self)
        yamllintAction.setStatusTip('Online YAML validation tool')
        yamllintAction.triggered.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl(__YAMLlint__)))

        # Menubar Issues action:
        issuesAction = QtGui.QAction('&Issues', self)
        issuesAction.setStatusTip('Report bugs and issues')
        issuesAction.triggered.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl(__issues__)))

        # Menubar SW Upgrade action:
        swupgradeAction = QtGui.QAction('&SW Upgrade', self)
        swupgradeAction.setStatusTip('Check for new software versions')

        # Menubar About action:
        aboutAction = QtGui.QAction('&About', self)
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
        # toolbar = self.addToolBar('CFG Gen')
        # toolbar.addAction(changeLayoutCFG)
        # toolbar = self.addToolBar('Shut / No Shut')

        # Create a central Widgets
        centralWidget = QtWidgets.QWidget()

        # Create a Layout for the central Widget
        centralLayout = QtWidgets.QGridLayout()

        # Config generator Layout elements
        # Labels
        self.databaseLb = QtWidgets.QLabel('Database: (YAML)')
        self.templateLb = QtWidgets.QLabel('Template: (Jinja2)')
        self.projectLb = QtWidgets.QLabel('Project name:')
        self.fileExtLb = QtWidgets.QLabel('Output file extension:')
        # Text lines
        self.databaseEdit = DragDropQLineEdit('< Drag & Drop a YAML file or Browse >', self, 'YAML')
        self.databaseEdit.focusInEvent = bind(
            lambda w, e: QtCore.QTimer.singleShot(0, w.selectAll),
            self.databaseEdit)  # This is needed to select all text when click on LineEdit
        self.templateEdit = DragDropQLineEdit('< Drag & Drop a Jinja2 file or Browse >', self, 'JINJA')
        self.templateEdit.focusInEvent = bind(
            lambda w, e: QtCore.QTimer.singleShot(0, w.selectAll),
            self.templateEdit)  # This is needed to select all text when click on LineEdit
        self.projectEdit = QtWidgets.QLineEdit(defFolder)
        self.projectEdit.focusInEvent = bind(
            lambda w, e: QtCore.QTimer.singleShot(0, w.selectAll),
            self.projectEdit)  # This is needed to select all text when click on LineEdit
        self.fileExtEdit = QtWidgets.QLineEdit('.txt')
        self.fileExtEdit.focusInEvent = bind(
            lambda w, e: QtCore.QTimer.singleShot(0, w.selectAll),
            self.fileExtEdit)  # This is needed to select all text when click on LineEdit
        # Buttons
        self.databaseBtn = QtWidgets.QPushButton('Browse')
        self.databaseBtn.clicked.connect(lambda: self._getFilePath(self.databaseEdit))
        self.templateBtn = QtWidgets.QPushButton('Browse')
        self.templateBtn.clicked.connect(lambda: self._getFilePath(self.templateEdit))
        self.projectBtn = QtWidgets.QPushButton('Update')
        self.projectBtn.clicked.connect(self._updateDefFolder)
        self.cfgenBtn = QtWidgets.QPushButton('Run')
        self.cfgenBtn.clicked.connect(self.config_gen)

        # Config generator Layout - make a grid and stitch all together
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
        # centralWidget.setLayout(centralLayout)
        centralWidget.setLayout(cfgenLayout)

        # Set the Widget
        self.setCentralWidget(centralWidget)

        # Set main windows size, position, title and icons
        self.resize(600, 10)
        self.center()
        self.setWindowTitle(__appName__)
        self.setWindowIcon(QtGui.QIcon(__icon__))
        self.show()

        # Override system excepthook to show error within the GUI
        sys.excepthook = self._excepthook

    def center(self):  # [GUI] Move the main window to the center of the screen
        qr = self.frameGeometry()
        cp = QtGui.QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):  # [GUI] The main window is closed
        event.accept()

    def about(self):  # [GUI] Ab out window
        aboutMsg = QtWidgets.QMessageBox()
        aboutMsg.setContentsMargins(10, 0, 40, 0)
        aboutMsg.setWindowTitle('About')
        aboutMsg.setText(f'\n   {__appName__}\n\n'
                         f'        Author: {__author__}\n'
                         f'        Version: {__version__}\n'
                         f'        License:  {__license__}\n\n'
                         f'        {__homepage__}'
                         )
        aboutMsg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        aboutMsg.exec()

    ###############################
    ##      END of GUI code      ##
    ###############################

    def _updateDefFolder(self):
        defFolder = time.strftime('%Y%m%d-%H%M%S')
        self.projectEdit.setText(defFolder)

    def _getFilePath(self, textField):
        fileName = ''
        if textField.fileType == 'YAML':
            fileName = QtWidgets.QFileDialog.getOpenFileName(self, 'Select file', '.', '*.yml *.yaml')[0]

        if textField.fileType == 'JINJA':
            fileName = QtWidgets.QFileDialog.getOpenFileName(self, 'Select file', '.', '*.j2 *.jinja')[0]

        setValidFile(textField.fileType, fileName, textField)

    def _excepthook(self, excType, excValue, tracebackobj):
        """
        Global function to catch unhandled exceptions.

        @param excType exception type
        @param excValue exception value
        @param tracebackobj traceback object
        """
        infoVersion = f'Version: {__version__} \n'
        separator = '-' * 80
        notice = ('An unhandled exception occurred.\n'
                  f'Please report the problem via email to <{__email__}>\n'
                  f'A log has been written to {__logfile__}\n\n'
                  'Expand for more details:')
        timeString = time.strftime("%Y-%m-%d, %H:%M:%S")

        tbinfofile = io.StringIO()
        traceback.print_tb(tracebackobj, None, tbinfofile)
        tbinfofile.seek(0)
        tbinfo = tbinfofile.read()
        errmsg = f'{str(excType)}: \n{str(excValue)}'
        sections = [separator, timeString, separator, errmsg, separator, tbinfo]
        msg = '\n'.join(sections)
        logging.error(infoVersion + msg)
        errorbox = QtWidgets.QMessageBox()
        errorbox.setContentsMargins(10, 0, 40, 0)
        errorbox.setIcon(QtWidgets.QMessageBox.Icon.Critical)
        errorbox.setWindowTitle('Unhandled Error')
        errorbox.setText(notice)
        errorbox.setDetailedText(str(infoVersion) + str(msg))
        errorbox.exec()

    def handleErrors(self, errorText, errorArgs):
        logging.error(errorText + errorArgs)
        err_msg = QtWidgets.QMessageBox()
        err_msg.setContentsMargins(10, 0, 40, 0)
        err_msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
        err_msg.setWindowTitle('Error')
        err_msg.setText(errorText)
        err_msg.setDetailedText(errorArgs)
        err_msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        err_msg.exec()

    def openFile(self, filepath):
        if platform.system() == 'Darwin':       # macOS
            subprocess.call(('open', filepath))
        elif platform.system() == 'Windows':    # Windows
            os.startfile(filepath)
        else:                                   # linux variants
            subprocess.call(('xdg-open', filepath))

    def checkdir(self, out_path):  # This function will check if the destination folder already exist and create one if not
        attempts = 0
        while attempts < 3:  # Try multiple time to fix when file is already opened
            try:
                os.makedirs(out_path)
                return True
            except OSError as exc:
                if exc.errno == errno.EEXIST:
                    reply = QtWidgets.QMessageBox.question(
                        self, 'Warning', 'Project folder already exists and will be overwritten, continue?', QtWidgets.QMessageBox.StandardButton.Yes
                        | QtWidgets.QMessageBox.StandardButton.No, QtWidgets.QMessageBox.StandardButton.No)
                    if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                        shutil.rmtree(out_path)
                    else:
                        return False
                elif exc.errno == 13:
                    errorArgs = 'One of the files is already in use, please close the application and try again.\n'
                    errorArgs = errorArgs + str(exc.args)
                    logging.debug(errorArgs)
                    attempts += 1
                else:
                    logging.debug(str(exc.args))
                    attempts += 1

    # Jinja2 filters to handle IP Addresses
    def j2filter_ip(self, text):
        return str(IPNetwork(text).ip)

    def j2filter_ipadd(self, text, num):
        return str(IPNetwork(text).ip.__add__(int(num)))

    def j2filter_network(self, text):
        return str(IPNetwork(text).network)

    def j2filter_broadcast(self, text):
        return str(IPNetwork(text).broadcast)

    def j2filter_bitmask(self, text):
        return str(IPNetwork(text).prefixlen)

    def j2filter_netmask(self, text):
        return str(IPNetwork(text).netmask)

    def j2filter_wildmask(self, text):
        return str(IPNetwork(text).hostmask)

    def config_gen(self):  # This function cover the config generator
        out_path = os.path.join(myDocuments, 'NEPyH_Outputs', Path(self.projectEdit.text()))
        db_path = self.databaseEdit.text()
        tp_path = Path(self.templateEdit.text()).parent
        tp_name = Path(self.templateEdit.text()).name
        fileExt = self.fileExtEdit.text()

        if self.checkdir(out_path) == False:
            return

        report = ''  # Initialize final report to the user for each config_gen() cycle

        # Load data from YAML into Python dictionary
        infomsg = 'Load YAML database...'
        report += f'{infomsg}\n'
        logging.info(infomsg)
        try:
            input_db = yaml.load(open(db_path), Loader=yaml.SafeLoader)
        except yaml.YAMLError as exc:
            errorText = ('An error occurred while parsing YAML file\n\n'
                         'Please correct data and retry.\n')
            if hasattr(exc, 'problem_mark'):
                if exc.context != None:
                    errorArgs = ('Parser says:\n'
                                 f'{str(exc.problem_mark)}\n'
                                 f'{str(exc.problem)} {str(exc.context)}\n\n'
                                 f'Use lint to validate your code: {__YAMLlint__}')
                    self.handleErrors(errorText, errorArgs)
                    return
                else:
                    errorArgs = ('Parser says:\n'
                                 f'{str(exc.problem_mark)}\n'
                                 f'{str(exc.problem)}\n\n'
                                 f'Use lint to validate your code: {__YAMLlint__}')
                    self.handleErrors(errorText, errorArgs)
                    return

        # Load Jinja2 template
        infomsg = 'Create Jinja2 Environment...'
        report += f'{infomsg}\n'
        logging.info(infomsg)
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(tp_path)), trim_blocks=True, lstrip_blocks=True)
        env.filters['ip'] = self.j2filter_ip
        env.filters['ipadd'] = self.j2filter_ipadd
        env.filters['network'] = self.j2filter_network
        env.filters['broadcast'] = self.j2filter_broadcast
        env.filters['bitmask'] = self.j2filter_bitmask
        env.filters['netmask'] = self.j2filter_netmask
        env.filters['wildmask'] = self.j2filter_wildmask

        infomsg = 'Load Jinja2 Template...'
        report += f'{infomsg}\n'
        logging.info(infomsg)
        try:
            input_tp = env.get_template(tp_name)
        except jinja2.TemplateNotFound:
            errorText = f'{tp_name}: File not found\n'
            errorArgs = f"File '{tp_name}' not found in {str(tp_path)}\n"
            self.handleErrors(errorText, errorArgs)
            return
        except jinja2.TemplateSyntaxError as exc:
            errorText = ('An error occurred while reading Jinja2 template\n\n'
                         'Please correct data and retry.\n')
            errorArgs = ('Syntax check failed:\n'
                         f' {exc.message} '
                         f'in {exc.filename} at line {exc.lineno}')
            self.handleErrors(errorText, errorArgs)
            return

        # Render the template with data and print the output
        infomsg = 'Rendering templates...'
        report += f'{infomsg}\n'
        logging.info(infomsg)
        try:
            for entry in input_db:
                result = input_tp.render(entry)
                out_file_name = next(iter(entry.values())) + fileExt
                out_file = open(os.path.join(out_path, out_file_name), 'w')
                out_file.write(result)
                out_file.close()
                infomsg = f"Configuration '{out_file_name}' created..."
                report += f'{infomsg}\n'
                logging.info(infomsg)
        except ValueError as exc:
            errorText = ('An error occurred while rendering the templates\n'
                         'The YAML file must start with a list of dictionary\n\n'
                         'Please correct data and retry.\n')
            errorArgs = (str(traceback.format_exc()))
            self.handleErrors(errorText, errorArgs)
            return
        except jinja2.UndefinedError as exc:
            errorText = ('An error occurred while parsing Jinja2 template\n\n'
                         'Please correct data and retry.\n')
            errorArgs = exc.message
            self.handleErrors(errorText, errorArgs)
            return

        # Final messagebox when configuration is correctly generated
        end_msg = QtWidgets.QMessageBox()
        end_msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
        end_msg.setWindowTitle('Task Finished')
        end_msg.setText(f"\nProject '{self.projectEdit.text()}' completed!\n\n"
                        'The files have been generated in the folder: \n'
                        f"  '{str(out_path)}'\n")
        end_msg.setDetailedText(report)
        end_msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok | QtWidgets.QMessageBox.StandardButton.Open)
        result = end_msg.exec()
        if result == QtWidgets.QMessageBox.StandardButton.Open:
            self.openFile(str(out_path))


def setValidFile(fileType, fileName, textField):
    # Set error message for invalid file
    errorMsg = f'< Not a valid {fileType} file >'

    # Validate YAML file
    if fileType == 'YAML':
        try:
            # Load the file as YAML
            yaml.load(open(fileName), Loader=yaml.SafeLoader)
            textField.setText(fileName)
        except:
            textField.setText(errorMsg)

    # Validate JINJA file
    elif fileType == 'JINJA':
        try:
            # Load the file as Jinja template
            env = jinja2.Environment()
            with open(fileName) as template:
                env.parse(template.read())

            # YAML files can also be loaded as Jinja template without errors
            # try to understand if the file extension is of a YAML file
            root, ext = os.path.splitext(fileName)
            if ext.lower() in ['.yaml', '.yml']:
                textField.setText(errorMsg)
            else:
                textField.setText(fileName)
        except:
            textField.setText(errorMsg)


def bind(func, to):  # This is needed to select all text when click on LineEdit
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
    status = app.exec()
    logging.info('Session Finished')
    sys.exit(status)


if __name__ == '__main__':
    main()
