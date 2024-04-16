# importing libraries
import threading
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWebEngineWidgets import *
from PyQt6.QtSvgWidgets import *

import sys
import os
import re
from typing import List, Tuple


from locator import Locator
import arg_handler

# creating a class
# that inherits the QDialog class    

def _generate_tab_order(dialog: QDialog, widgets: List[QWidget]):
    for i in range(0, len(widgets) -1):
        dialog.setTabOrder(widgets[i], widgets[i + 1])             

class LocatorWindow(QDialog):
    _locator: Locator = None
    _img_label: QSvgWidget = None

    _form_group_box: QGroupBox = None

    _input_path_button: QPushButton = None

    _input_folder_label: QPushButton = None

    _x_input_box: QLineEdit = None

    _y_input_box: QLineEdit = None

    _filter_input_box: QLineEdit = None

    _update_button: QPushButton = None   

    _markers_button: QPushButton = None

    _location_data: QTextEdit = None

    _map_folder_directory: str = ""

    _center_point: Tuple[float, float] = None

    _filter_pattern: re.Pattern = None

    _input_valid: bool = False

    _filter_valid: bool = False

    _coords_valid: bool = False

    # constructor
    def __init__(self ):
        super(LocatorWindow, self).__init__()

        #Configure window
        self.setWindowTitle("7DTD Prefab Locator")
        self.setWindowState(Qt.WindowState.WindowMaximized)

        # creating a group box
        self._form_group_box = QGroupBox("Location Options")

        # Configure x text box
        self._x_input_box = QLineEdit(self)
        self._x_input_box.textChanged.connect(self._coord_text_updated)
        self._x_input_box.returnPressed.connect(lambda: self._update_button.click())

        # Configure y text box
        self._y_input_box = QLineEdit(self)
        self._y_input_box.textChanged.connect(self._coord_text_updated)
        self._y_input_box.returnPressed.connect(lambda: self._update_button.click())

        # Configure filter text box
        self._filter_input_box = QLineEdit(self)
        self._filter_input_box.textChanged.connect(self._filter_text_updated)
        self._filter_input_box.returnPressed.connect(lambda: self._update_button.click())

        # Configure input path button
        self._input_path_button = self._generate_item_and_set_text("Choose input directory", QPushButton)
        self._input_path_button.clicked.connect(self._input_button_clicked)

        # # Configure input folder label
        self._input_folder_label = self._generate_item_and_set_text("Selected folder:", QLabel)
        
        # Configure update button
        self._update_button = self._generate_item_and_set_text("Update Map", QPushButton)
        self._update_button.setEnabled(False)
        self._update_button.clicked.connect(self._update_map_button_clicked)

        self._markers_button = self._generate_item_and_set_text("Update Dashboard", QPushButton)
        self._markers_button.setEnabled(False)
        self._markers_button.clicked.connect(self._update_dashboard_button_clicked)

        # Configure textbox layout
        location_text_layout = QHBoxLayout()

        location_text_layout.addWidget(self._generate_item_and_set_text("X Coord:", QLabel))
        location_text_layout.addWidget(self._x_input_box)

        location_text_layout.addWidget(self._generate_item_and_set_text("Y Coord:", QLabel))
        location_text_layout.addWidget(self._y_input_box)

        location_text_layout.addWidget(self._generate_item_and_set_text("Filter:", QLabel))
        location_text_layout.addWidget(self._filter_input_box)

        # Configure button layout
        location_button_layout = QHBoxLayout()

        location_button_layout.addWidget(self._input_path_button, stretch=1)

        location_button_layout.addWidget(self._input_folder_label, stretch=3)

        location_button_layout.addWidget(self._update_button, stretch=1)

        location_button_layout.addWidget(self._markers_button, stretch=1)


        # Configure group box layout
        location_layout = QVBoxLayout()

        location_layout.addLayout(location_text_layout)
        location_layout.addLayout(location_button_layout)

        self._form_group_box.setLayout(location_layout)

        # Configure data layout
        location_data_layout = QHBoxLayout()

        self._img_label = QSvgWidget(self)

        self._location_data = QTextEdit(self)

        font = QFont("Hack")

        font.setPointSize(10)

        
        # font.setStyleHint(QFont.StyleHint.TypeWriter)


        

        self._location_data.setFont(font)

        self._location_data.setReadOnly(True)
        self._location_data.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        location_data_layout.addWidget(self._img_label, stretch=1)

        location_data_layout.addWidget(self._location_data, stretch=1)
    

        # creating a vertical layout
        main_layout = QVBoxLayout()

        # adding form group box to the layout
        main_layout.addWidget(self._form_group_box)

        main_layout.addLayout(location_data_layout)

        self.setLayout(main_layout)

        self._x_input_box.setFocus()

        
        self._locator = Locator()

        self._x_input_box.setText("0")
        self._y_input_box.setText("0")
        self._filter_input_box.setText(".*")

        _generate_tab_order(self, [self._x_input_box, self._y_input_box, self._filter_input_box, self._input_path_button,  self._update_button])



    
    def _generate_item_and_set_text(self, label_text:str, __class: type):

        label: QWidget = __class(self)

        label.setText(label_text)

        return label 
    

    def _input_button_clicked(self):

        file_dialog = QFileDialog(self)

        appdata = os.path.expandvars(os.path.join(r"%appdata%","7DaysToDie", "GeneratedWorlds"))

        self._map_folder_directory = str(file_dialog.getExistingDirectory(directory=appdata))

        self._input_valid = arg_handler.check_path(self._map_folder_directory)

        if self._input_valid:
            self._locator.set_input_path(self._map_folder_directory)

            self._input_folder_label.setText("Selected folder: " + self._map_folder_directory)

            self._check_updatable()

        else:
            self._input_folder_label.setText("Selected folder:")


    def _filter_text_updated(self):
        self._filter_pattern = arg_handler.validate_filter(self._filter_input_box.text())
        self._filter_valid = self._filter_pattern != None

        if self._filter_valid:
            self._locator.set_filter(self._filter_pattern)
            self._check_updatable()


    def _coord_text_updated(self):
        center_point = arg_handler.convert_coords(self._x_input_box.text() or 0, self._y_input_box.text() or 0)

        self._coords_valid = center_point != None

        if self._coords_valid:
            self._locator.center_point = center_point
            
            self._check_updatable()

    def _check_updatable(self):

        updateable = all([self._coords_valid, self._input_valid, self._filter_valid])

        self._update_button.setEnabled(updateable)
        self._markers_button.setEnabled(updateable)

    def _update_map_button_clicked(self):

        self._locator.locate_prefabs()
        self._locator.locate_spawnpoints()

        data_string = self._locator.generate_data(write_file=False)

        __bytes = self._locator.image.read()

        self._img_label.load(__bytes)

        self._location_data.setText(data_string)

        self._check_updatable()

        self._locator.clear_data()

    def _update_dashboard_button_clicked(self):

        self._locator.locate_prefabs()
        self._locator.locate_spawnpoints()

        t = threading.Thread(target=self._locator.add_markers)

        t.start()


def show_window():

    app = QApplication(sys.argv)

    QFontDatabase.addApplicationFont('Fonts/hack.regular.ttf') 
    window = LocatorWindow()
    window.show()
    sys.exit(app.exec())
