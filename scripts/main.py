import os
import platform
import sys

import qdarktheme
from PyQt5.QtCore import Qt, QMutex, QSettings, QCoreApplication
from PyQt5.QtGui import QTextCharFormat, QColor, QTextCursor, QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QTabWidget, QTextEdit, QGroupBox, QGridLayout, QSlider, QMenu, QStyleFactory
)

from commands import *
from telnet_worker import *
from validation_utils import *
import ctypes

# Set the DPI awareness in Windows
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    print("Setting Process Dpi Awareness")
except Exception as e:
    print(e)


class ProjectorController(QWidget):
    def __init__(self, host='172.18.41.12', port="23", projector_id='01', parent=None, settings=None):
        super().__init__(parent)
        self.telnet_connection = None
        self.telnet_worker = None
        self.current_host = None
        self.current_port = None
        self.current_projector_id = None

        if settings:
            self.initial_host = settings.value("host", host)
            self.initial_port = settings.value("port", port)
            self.initial_projector_id = settings.value("projector_id", projector_id)
        else:
            self.initial_host = host
            self.initial_port = port
            self.initial_projector_id = projector_id
        self.lock = QMutex()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Telnet Optoma Controller')

        self.setMaximumSize(588, 900)
        self.resize(588, 800)
        #self.set_dark_theme()
        self.setup_layouts()
        self.set_ui_enabled(False)
    def set_dark_theme(self):
        if platform.system() == "Windows":
            self.setStyleSheet("""
                QWidget { background-color: #2d2d2d; color: #dcdcdc; }
                QLineEdit, QTextEdit { background-color: #3c3c3c; color: #dcdcdc; border: 1px solid #5c5c5c; }
                QPushButton { background-color: #5c5c5c; color: #dcdcdc; border: 1px solid #7c7c7c; padding: 5px; }
                QPushButton:pressed { background-color: #7c7c7c; }
                QLabel { color: #dcdcdc; }
                QTabWidget::pane { background-color: #2d2d2d; border: 1px solid #5c5c5c; }
                QTabWidget { background-color: #2d2d2d; }
                QTabBar::tab { background: #3c3c3c; color: #dcdcdc; padding: 10px; border: 1px solid #5c5c5c; }
                QTabBar::tab:selected { background: #5c5c5c; color: #dcdcdc; }
                QTabBar::tab:hover { background: #7c7c7c; color: #dcdcdc; }
                QTabBar::tab:!selected { margin-top: 2px; }
            """)

    def setup_layouts(self):
        self.main_layout = QVBoxLayout()

        self.connection_layout = self.create_connection_layout()
        self.custom_command_layout = self.create_custom_command_layout()
        self.button_layout = self.create_button_layout()
        self.tabs_layout_widget = self.create_tab_widget()

        self.command_output = QTextEdit()
        self.command_output.setReadOnly(True)
        self.status_label = QLabel('Disconnected')
        self.status_label.setStyleSheet('color: red')
        self.command_output.setMaximumHeight(200)  # Set the maximum height to 200 pixels
        self.main_layout.addLayout(self.connection_layout)
        self.main_layout.addWidget(self.status_label)
        self.main_layout.addLayout(self.button_layout)
        self.main_layout.addWidget(self.tabs_layout_widget)
        self.main_layout.addLayout(self.custom_command_layout)
        self.main_layout.addWidget(self.command_output)

        self.setLayout(self.main_layout)

    def create_connection_layout(self):
        layout = QHBoxLayout()
        self.host_input = QLineEdit(self.initial_host)
        self.host_input.setPlaceholderText('IP Address')
        self.port_input = QLineEdit(self.initial_port)
        self.port_input.setPlaceholderText('Port')
        self.projector_id_input = QLineEdit(self.initial_projector_id)
        self.projector_id_input.setPlaceholderText('ID')

        self.connect_button = QPushButton('Connect')
        self.connect_button.clicked.connect(self.connect)

        self.host_input.textChanged.connect(self.disconnect)
        self.port_input.textChanged.connect(self.disconnect)
        self.projector_id_input.textChanged.connect(self.disconnect)

        layout.addWidget(QLabel('IP Address:'))
        layout.addWidget(self.host_input)
        layout.addWidget(QLabel('Port:'))
        layout.addWidget(self.port_input)
        layout.addWidget(QLabel('ID:'))
        layout.addWidget(self.projector_id_input)
        layout.addWidget(self.connect_button)
        return layout

    def disconnect(self):

        new_host = self.host_input.text()
        new_port = self.port_input.text()
        new_projector_id = self.projector_id_input.text().zfill(2)

        if (new_host != self.current_host or
                new_port != self.current_port or
                new_projector_id != self.current_projector_id):
            if self.telnet_worker:
                self.telnet_worker.stop()
            if self.telnet_connection:
                self.telnet_connection.close()
                self.telnet_connection = None
                self.set_ui_enabled(False)
                self.status_label.setText('Disconnected')
                self.status_label.setStyleSheet('color: red')
                self.update_output('Disconnected', "red")

    def read_projector_settings(self):
        value = self.read_command(system_buttons["Power Status"], True)
        if value > 0:
            self.power_status_label.setText('Status: On')
            self.power_status_label.setStyleSheet('color: green')
            self.slider_refresh(self.contrast_slider.findChild(QSlider),
                                self.contrast_slider.findChild(QLabel),
                                picture_settings_slider['Get Contrast'])
            self.slider_refresh(self.brightness_slider.findChild(QSlider),
                                self.brightness_slider.findChild(QLabel),
                                picture_settings_slider['Get Brightness'])
        else:
            self.power_status_label.setText('Status: Off')
            self.power_status_label.setStyleSheet('color: red')

    def create_custom_command_layout(self):
        layout = QHBoxLayout()
        self.custom_command_input = QLineEdit('XX125 1')
        self.custom_command_input.setPlaceholderText('Custom Command')
        custom_command_button = QPushButton('Call')
        custom_command_button.clicked.connect(lambda: self.send_command(f'~{self.custom_command_input.text()}'))

        layout.addWidget(QLabel('Custom Command:'))
        layout.addWidget(self.custom_command_input)
        layout.addWidget(custom_command_button)
        return layout

    def create_button_layout(self):
        layout = QVBoxLayout()
        layout_power_status = QVBoxLayout()
        layout_power = QHBoxLayout()
        group_power = QGroupBox("Power")

        self.power_status_label = QLabel('Status: Off')
        self.power_status_label.setStyleSheet('color: red')
        self.power_on_button = QPushButton('On')
        self.power_off_button = QPushButton('Off')

        self.power_on_button.clicked.connect(lambda: self.send_command(system_buttons['Power On']))
        self.power_off_button.clicked.connect(lambda: self.send_command(system_buttons['Power Off']))

        layout_power.addWidget(self.power_on_button)
        layout_power.addWidget(self.power_off_button)

        layout_power_status.addLayout(layout_power)
        layout_power_status.addWidget(self.power_status_label)
        group_power.setLayout(layout_power_status)

        layout.addWidget(group_power)
        layout.addSpacing(20)

        return layout

    def create_tab_widget(self):
        tab_widget = QTabWidget()

        tab_widget.addTab(self.create_controller_tab(), 'Controller')
        tab_widget.addTab(self.create_advanced_warp_tab(), 'Advanced Warp')
        tab_widget.addTab(self.create_test_patterns_tab(), 'Test Patterns')
        tab_widget.addTab(self.create_display_controls_tab(), 'Display Controls')
        tab_widget.addTab(self.create_additional_display_controls_tab(), 'Additional Display Controls')
        self.tabs = tab_widget
        return tab_widget

    def create_controller_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        controller_top_group = self.create_controller_top_group()
        navigation_group = self.create_navigation_group()
        lens_shift_group = self.create_lens_shift_group()
        zoom_group = self.create_zoom_group()

        layout.addWidget(controller_top_group)
        layout.addWidget(navigation_group)
        layout.addWidget(lens_shift_group)
        layout.addWidget(zoom_group)

        tab.setLayout(layout)
        return tab

    def create_navigation_group(self):
        group = QGroupBox('Navigation')
        layout = QGridLayout()

        up_button = QPushButton('Up')
        down_button = QPushButton('Down')
        left_button = QPushButton('Left')
        right_button = QPushButton('Right')
        enter_button = QPushButton('Enter')

        up_button.clicked.connect(lambda: self.send_command(directional_buttons['Up']))
        down_button.clicked.connect(lambda: self.send_command(directional_buttons['Down']))
        left_button.clicked.connect(lambda: self.send_command(directional_buttons['Left']))
        right_button.clicked.connect(lambda: self.send_command(directional_buttons['Right']))
        enter_button.clicked.connect(lambda: self.send_command(directional_buttons['Enter']))

        layout.addWidget(up_button, 0, 1)
        layout.addWidget(left_button, 1, 0)
        layout.addWidget(enter_button, 1, 1)
        layout.addWidget(right_button, 1, 2)
        layout.addWidget(down_button, 2, 1)

        group.setLayout(layout)
        return group

    def create_lens_shift_group(self):
        group = QGroupBox('Lens Shift')
        layout = QGridLayout()

        up_button = QPushButton('Up')
        down_button = QPushButton('Down')
        left_button = QPushButton('Left')
        right_button = QPushButton('Right')

        up_button.clicked.connect(lambda: self.send_command(lens_shift_buttons['Up']))
        down_button.clicked.connect(lambda: self.send_command(lens_shift_buttons['Down']))
        left_button.clicked.connect(lambda: self.send_command(lens_shift_buttons['Left']))
        right_button.clicked.connect(lambda: self.send_command(lens_shift_buttons['Right']))

        layout.addWidget(up_button, 0, 1)
        layout.addWidget(left_button, 1, 0)
        layout.addWidget(right_button, 1, 2)
        layout.addWidget(down_button, 2, 1)

        group.setLayout(layout)
        return group

    def create_controller_top_group(self):
        group = QGroupBox()
        layout = QHBoxLayout()

        self.menu_button = QPushButton('Menu')
        self.return_button = QPushButton('Return')
        self.exit_button = QPushButton('Exit')

        self.menu_button.clicked.connect(lambda: self.send_command(system_buttons['Menu']))
        self.return_button.clicked.connect(lambda: self.send_command(system_buttons['Return']))
        self.exit_button.clicked.connect(lambda: self.send_command(system_buttons['Exit']))

        layout.addWidget(self.menu_button)
        layout.addWidget(self.return_button)
        layout.addWidget(self.exit_button)

        group.setLayout(layout)
        return group

    def create_zoom_group(self):
        group = QGroupBox('Zoom')
        layout = QHBoxLayout()

        zoom_in_button = QPushButton('+')
        zoom_out_button = QPushButton('-')

        zoom_in_button.clicked.connect(lambda: self.send_command(zoom_buttons['+']))
        zoom_out_button.clicked.connect(lambda: self.send_command(zoom_buttons['-']))

        layout.addWidget(zoom_in_button)
        layout.addWidget(zoom_out_button)

        group.setLayout(layout)
        return group

    def create_advanced_warp_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        warp_type_group = self.create_button_group("Warp Type", warp_control_buttons)
        grid_background_group = self.create_button_group("Grid Background", grid_background_buttons)
        warp_inner_group = self.create_button_group("Warp Inner", advanced_warp_inner_buttons)
        grid_color_group = self.create_button_group("Grid Color", grid_color_buttons)
        grid_points_group = self.create_button_group("Grid Points", grid_points_buttons)

        layout.addWidget(warp_type_group)
        layout.addWidget(grid_background_group)
        layout.addWidget(warp_inner_group)
        layout.addWidget(grid_color_group)
        layout.addWidget(grid_points_group)

        tab.setLayout(layout)
        return tab

    def slider_refresh(self, slider: QSlider, label: QLabel, command: str, quite: bool = True):
        value = self.read_command(command, quite)
        slider.blockSignals(True)
        slider.setValue(value)
        slider.blockSignals(False)
        label_text = label.text().split(':')[0]
        label.setText(f"{label_text}: {value}")

    def send_slider_command(self, command_prefix, value, label: QLabel):
        command = f"{command_prefix} {value}"
        self.send_command(command)
        label.setText(f"{label.text().split(':')[0]}: {value}")

    def create_slider_group(self, label_text, command_prefix, read_command, min_value, max_value,
                            quite_update: bool = True):
        group = QGroupBox(label_text)
        layout = QVBoxLayout()
        val_layout = QHBoxLayout()

        label = QLabel(f"{label_text}: {min_value}")
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_value)
        slider.setMaximum(max_value)
        slider.setValue(min_value)
        slider.valueChanged.connect(lambda value: self.send_slider_command(command_prefix, value, label))
        button = QPushButton('R')
        button.clicked.connect(lambda _, cmd=read_command: self.slider_refresh(slider, label, cmd, quite_update))
        val_layout.addWidget(slider)
        val_layout.addWidget(button)
        layout.addWidget(label)
        layout.addLayout(val_layout)

        group.setLayout(layout)
        return group

    def create_button_group(self, title, buttons):
        group = QGroupBox(title)
        layout = QHBoxLayout()

        for button_text, command in buttons.items():
            button = QPushButton(button_text)
            button.clicked.connect(lambda _, cmd=command: self.send_command(cmd))
            layout.addWidget(button)

        group.setLayout(layout)
        return group

    def create_display_controls_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        hdr_group = self.create_button_group('HDR', hdr_buttons)
        gamma_mode_group = self.create_button_group('Gamma Mode', gamma_mode_buttons)
        picture_mode_group = self.create_button_group('Picture Mode', picture_mode_buttons)
        aspect_ratio_group = self.create_button_group('Aspect Ratio', aspect_ratio_buttons)

        slider_layout = QHBoxLayout()
        self.brightness_slider = self.create_slider_group("Brightness", picture_settings_slider['Set Brightness'],
                                                          picture_settings_slider['Get Brightness'], 0, 100, True)
        self.contrast_slider = self.create_slider_group("Contrast", picture_settings_slider['Set Contrast'],
                                                        picture_settings_slider['Get Contrast'], 0, 100, True)
        slider_group = QGroupBox('Picture Settings')
        slider_layout.addWidget(self.brightness_slider)
        slider_layout.addWidget(self.contrast_slider)
        slider_group.setLayout(slider_layout)
        layout.addWidget(hdr_group)
        layout.addWidget(gamma_mode_group)
        layout.addWidget(picture_mode_group)
        layout.addWidget(aspect_ratio_group)
        layout.addWidget(slider_group)
        tab.setLayout(layout)

        return tab

    def create_additional_display_controls_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()


        picture_mode_group = self.create_button_group('Picture Mode', picture_mode_buttons)
        extreme_black_group = self.create_button_group('Extreme Black', extreme_black_buttons)
        dynamic_black_group = self.create_button_group('Dynamic Black', dynamic_black_buttons)
        wall_color_group = self.create_button_group('Wall Color', wall_color_buttons)

        layout.addWidget(picture_mode_group)
        layout.addWidget(extreme_black_group)
        layout.addWidget(dynamic_black_group)
        layout.addWidget(wall_color_group)
        tab.setLayout(layout)

        return tab
        
    def create_test_patterns_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        test_pattern_group = self.create_button_group("Test Pattern", test_pattern_buttons)
        layout.addWidget(test_pattern_group)

        tab.setLayout(layout)
        return tab

    def set_ui_enabled(self, enabled):

        # Toggle the enabled state of the tab widget and layouts
        self.tabs_layout_widget.setEnabled(enabled)
        self.button_layout.setEnabled(enabled)
        self.custom_command_layout.setEnabled(enabled)

        # if not enabled:
        #     self.tabs_layout_widget.setStyleSheet("color: gray;")
        #     for layout in [self.button_layout, self.custom_command_layout]:
        #         for i in range(layout.count()):
        #             widget = layout.itemAt(i).widget()
        #             if widget is not None:
        #                 widget.setStyleSheet("color: gray;")
        #     # Reset the style to default when enabled
        #     self.tabs_layout_widget.setStyleSheet("")
        #     for layout in [self.button_layout, self.custom_command_layout]:
        #         for i in range(layout.count()):
        #             widget = layout.itemAt(i).widget()
        #             if widget is not None:
        #                 widget.setStyleSheet("")

    def valid_connection(self) -> bool:
        if not validate_ip(self.host_input.text()) or not validate_port(
                self.port_input.text()) or not validate_projector_id(self.projector_id_input.text()):
            self.update_output("Invalid IP, Port, or Projector ID", "red")
            return False
        return True

    def read_command(self, command: str, quite: bool = True) -> int:
        if not self.valid_connection():
            return 0
        try:
            result = self.send_command(command, quite)
            if result['success']:
                response_code = result['code']
                last_int = get_last_int(response_code)
                if last_int is not None:
                    return last_int

        except Exception as e:
            self.update_output(f'Read Command Error: [{str(e)}]', "red")

        return 0

    def send_command(self, command: str, quite: bool = False):
        try:
            if not self.telnet_connection:
                self.update_output("No active connection", "red")
                return
            final_command = command.replace('XX', "01")
            if self.projector_id_input.text():
                final_command = command.replace('XX', self.projector_id_input.text().zfill(2))
            if not quite:
                self.update_output(f'Sending Command: [{final_command}]')
            try:
                # self.lock.lock()
                # try:

                self.telnet_connection.write(final_command.encode('ascii') + b"\n")
                response = self.telnet_connection.read_until(b"\r", timeout=TIMEOUT).decode('ascii').rstrip()
                if not response.endswith("\r"):
                    response += self.telnet_connection.read_very_eager().decode('ascii').rstrip()
                result = {'success': True, 'code': response, 'error': ""}
            # finally:
            #     self.lock.unlock()
            except Exception as e:
                result = {'success': False, 'code': "", 'error': str(e)}

            if not quite:
                if result['success']:
                    self.update_output(f'Response: [{result["code"]}]', "green")
                else:
                    self.update_output(f'Error: {result["error"]}', "red")
        except Exception as f:
            result = {'success': False, 'code': "", 'error': str(f)}

        return result

    def connect(self):
        host = self.host_input.text()
        port = self.port_input.text()

        if not validate_ip(host) or not validate_port(port):
            self.status_label.setText('Error: Invalid IP or Port')
            self.status_label.setStyleSheet('color: red')
            self.update_output('Error: Invalid IP or Port', "red")
            return
        try:
            if self.telnet_worker:
                self.telnet_worker.stop()
            if self.telnet_connection:
                self.telnet_connection.close()
        except Exception as e:
            self.update_output(f'Close Error: {str(e)}', "red")
        try:
            self.telnet_connection = telnetlib.Telnet(host, int(port), TIMEOUT)
            self.set_ui_enabled(True)
            self.status_label.setText("Connected")
            self.status_label.setStyleSheet('color: green')
            self.update_output("Connected successfully", "green")
            self.current_host = host
            self.current_port = port
            self.current_projector_id = self.projector_id_input.text().zfill(2)
            self.read_projector_settings()

            # Start the Telnet worker to listen for messages
            self.telnet_worker = TelnetWorker(host, int(port), self.lock)
            self.telnet_worker.message_received.connect(self.handle_system_message)
            self.telnet_worker.connection_closed.connect(self.handle_connection_closed)
            self.telnet_worker.start()

        except Exception as e:
            self.status_label.setText(f'Connect Error: {str(e)}')
            self.status_label.setStyleSheet('color: red')
            self.update_output(f'Error: {str(e)}', "red")
            self.telnet_connection = None
            self.set_ui_enabled(False)

    def handle_system_message(self, message):
        try:
            if message:
                int_value = extract_digits(message)
                if -1 < int_value < 35:
                    self.update_output(f"System: {system_info_response[str(int_value)]}")
                    if int_value == 0:
                        self.power_status_label.setText('Status: Off')
                        self.power_status_label.setStyleSheet('color: red')
                    elif int_value == 24:
                        self.power_status_label.setText('Status: On')
                        self.power_status_label.setStyleSheet('color: green')

                    else:
                        self.power_status_label.setText(f'Status: {system_info_response[str(int_value)]}')
                        self.power_status_label.setStyleSheet('color: gray')
                else:
                    self.update_output(f"Raw System message received: {message}")
            else:
                self.update_output(f"Empty System Message")
        except Exception as e:
            self.update_output(f'System Message Error: {str(e)}', "red")

    def handle_connection_closed(self):
        self.update_output("Connection closed by the server.")
        self.set_ui_enabled(False)

    def closeEvent(self, event):
        if self.telnet_worker:
            self.telnet_worker.stop()
        if self.telnet_connection:
            self.telnet_connection.close()
        event.accept()

    def save_settings(self, settings, tab_index):
        settings.setValue(f"host", self.host_input.text())
        settings.setValue(f"port", self.port_input.text())
        settings.setValue(f"projector_id", self.projector_id_input.text())

    def update_output(self, text, color=None):
        cursor = self.command_output.textCursor()
        cursor.movePosition(QTextCursor.End)

        format_out = QTextCharFormat()
        if color:
            format_out.setForeground(QColor(color))

        cursor.insertText(text + "\n", format_out)
        self.command_output.ensureCursorVisible()


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Telnet Optoma Controller")

        self.set_dark_theme()

        self.settings = QSettings("Babilin Apps", "Optoma Controller")

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        if self.settings.value("tab_count", 0, int) > 0:
            self.load_tabs()
        else:
            self.add_projector_controller(name="Projector 1", host='172.18.41.12', port='23', projector_id='01')
            self.add_projector_controller(name="Projector 2", host='172.18.41.13', port='23', projector_id='02')
            self.add_projector_controller(name="Projector 3", host='172.18.41.14', port='23', projector_id='03')

        self.add_tab_button = QPushButton("Add Tab")
        self.add_tab_button.clicked.connect(self.add_new_tab)
        self.tab_widget.setCornerWidget(self.add_tab_button, Qt.TopRightCorner)

        # Add Power On/Off All buttons
        self.power_on_all_button = QPushButton("Power On All")
        self.power_off_all_button = QPushButton("Power Off All")
        self.power_on_all_button.clicked.connect(self.power_on_all)
        self.power_off_all_button.clicked.connect(self.power_off_all)

        # Layout for the Power On/Off All buttons
        power_buttons_layout = QHBoxLayout()
        power_buttons_layout.addWidget(self.power_on_all_button)
        power_buttons_layout.addWidget(self.power_off_all_button)

        # Add to main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(power_buttons_layout)
        main_layout.addWidget(self.tab_widget)
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        recommended_size = central_widget.sizeHint()
        print(f"Recommended size: {recommended_size.width()} x {recommended_size.height()}")
  
        self.setMaximumSize(588, 900)
        self.resize(588, 800)
        self.setCentralWidget(central_widget)
        self.tab_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tab_widget.customContextMenuRequested.connect(self.show_context_menu)


    def set_dark_theme(self):
            self.setStyleSheet("""
                QWidget { background-color: #2d2d2d; color: #dcdcdc; }
                QLineEdit, QTextEdit { background-color: #3c3c3c; color: #dcdcdc; border: 1px solid #5c5c5c; }
                QPushButton { background-color: #5c5c5c; color: #dcdcdc; border: 1px solid #7c7c7c; padding: 5px; }
                QPushButton:pressed { background-color: #7c7c7c; }
                QLabel { color: #dcdcdc; }
                QTabWidget::pane { background-color: #2d2d2d; border: 1px solid #5c5c5c; }
                QTabWidget { background-color: #2d2d2d; }
                QTabBar::tab { background: #3c3c3c; color: #dcdcdc; padding: 10px; border: 1px solid #5c5c5c; }
                QTabBar::tab:selected { background: #5c5c5c; color: #dcdcdc; }
                QTabBar::tab:hover { background: #7c7c7c; color: #dcdcdc; }
                QTabBar::tab:!selected { margin-top: 2px; }
            """)

    def add_projector_controller(self, name, host, port, projector_id):
        projector_controller = ProjectorController(host, port, projector_id)
        self.tab_widget.addTab(projector_controller, name)

    def add_projector_controller_from_settings(self, name, settings=None):
        projector_controller = ProjectorController(settings=settings)
        self.tab_widget.addTab(projector_controller, name)

    def load_tabs(self):
        tab_count = self.settings.value("tab_count", 0, int)
        for i in range(tab_count):
            tab_settings = QSettings("Babilin Apps", f"Optoma Controller/Projector {i}")
            tab_name = tab_settings.value(f"name", f"Projector {i + 1}")
            host = tab_settings.value("host", "0")
            port = tab_settings.value("port", "0")
            projector_id = tab_settings.value("projector_id", "0")
            print(f'loading tab: {tab_name}: {host}, {port}, {projector_id}')
            self.add_projector_controller_from_settings(tab_name, settings=tab_settings)

    def save_tabs(self):
        self.settings.setValue("tab_count", self.tab_widget.count())

        for i in range(self.tab_widget.count()):
            tab_name = self.tab_widget.tabText(i)
            tab_settings = QSettings("Babilin Apps", f"Optoma Controller/Projector {i}")
            widget = self.tab_widget.widget(i)
            tab_settings.setValue(f"name", self.tab_widget.tabText(i))
            widget.save_settings(tab_settings, i)
            host = tab_settings.value("host", "0")
            port = tab_settings.value("port", "0")
            projector_id = tab_settings.value("projector_id", "0")
            print(f'saving tab: {tab_name}: {host}, {port}, {projector_id}')

    def add_new_tab(self):
        next_index = self.tab_widget.count() + 1
        new_tab_name = f"Projector {next_index}"
        self.add_projector_controller(new_tab_name, host='172.18.41.12', port='23', projector_id='01')

    def show_context_menu(self, position):
        # Get the index of the tab at the position where the context menu was requested
        tab_index = self.tab_widget.tabBar().tabAt(position)
        if tab_index == -1:
            return  # No tab under the context menu position

        menu = QMenu()
        remove_action = menu.addAction("Remove Tab")
        action = menu.exec_(self.tab_widget.mapToGlobal(position))

        if action == remove_action:
            self.remove_tab(tab_index)

    def remove_tab(self, index):
        if index != -1:
            self.tab_widget.removeTab(index)
            self.renumber_tabs()

    def renumber_tabs(self):
        # Renumber tabs after removing one to maintain order
        for i in range(self.tab_widget.count()):
            new_name = f"Projector {i + 1}"
            self.tab_widget.setTabText(i, new_name)
            
    def closeEvent(self, event):
        self.save_tabs()
        event.accept()

    def power_on_all(self):
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            tab.connect()
            tab.send_command(system_buttons['Power On'])

    def power_off_all(self):
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            tab.connect()
            tab.send_command(system_buttons['Power Off'])


os.environ["QT_QPA_PLATFORM"] = "windows:darkmode=2"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
# Enable High DPI Scaling
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

if __name__ == '__main__':
    if platform.system() == "Windows":
        qdarktheme.enable_hi_dpi()
    app = QApplication(sys.argv)
    print(QStyleFactory.keys())
    print(QApplication.style().objectName())
    print(QApplication.style().metaObject().className())
    print(QApplication.style().metaObject())
    if platform.system() == "Windows":
        qdarktheme.setup_theme("auto")  # Set up the dark theme after QApplication is created
    main_window = MainWindow()
    main_window.show()
    if platform.system() == "Windows":
        # Set the icon for the entire application (not needed for py2app)
        app.setWindowIcon(QIcon("icon.png"))



sys.exit(app.exec_())
