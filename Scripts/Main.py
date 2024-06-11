import re
import telnetlib
import sys
import string
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QTabWidget, \
    QTextEdit, QGroupBox, QGridLayout, QSlider
from PyQt5.QtCore import Qt

from Commands import *

from Scripts.ValidationUtils import *


def load_stylesheet(filename):
    with open(filename, 'r') as file:
        return file.read()


def send_telnet_command(command: str, host: str, port: str) -> dict:
    try:
        with telnetlib.Telnet(host, int(port), 5) as tn:
            tn.write(command.encode('ascii') + b"\n")

            response = tn.read_until(b"\r", timeout=2).decode('ascii').strip().strip('\r\n').strip(
                '\r')  # Read until CR or timeout
            if not response.endswith("\r"):
                response += tn.read_very_eager().decode('ascii').strip().strip('\r\n').strip(
                    '\r')  # Read any remaining data

        return {'success': True, 'code': response, 'error': ""}
    except Exception as e:
        return {'success': False, 'code': "", 'error': str(e)}


def test_telnet_connection(host: str, port: str) -> dict:
    # global telnet_connection
    try:
        # Establish a Telnet connection
        tn = telnetlib.Telnet(host, int(port))
        tn.close()
        return {'success': True, 'error': ""}

    except Exception as e:
        return {'success': False, 'error': str(e)}


class ProjectorController(QWidget):
    def __init__(self):
        super().__init__()
        self.brightness_slider = None
        self.contrast_slider = None
        self.exit_button = None
        self.main_layout = None
        self.tabs = None
        self.return_button = None
        self.menu_button = None
        self.power_off_button = None
        self.power_on_button = None
        self.connect_button = None
        self.projector_id_input = None
        self.port_input = None
        self.host_input = None
        self.status_label = None
        self.command_output = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Projector Controller')

        self.setGeometry(100, 100, 800, 800)
        self.set_dark_theme()
        self.setup_layouts()

    def set_dark_theme(self):
        self.setStyleSheet("""
            QWidget { background-color: #2d2d2d; color: #dcdcdc; }
            QLineEdit, QTextEdit { background-color: #3c3c3c; color: #dcdcdc; border: 1px solid #5c5c5c; }
            QPushButton { background-color: #5c5c5c; color: #dcdcdc; border: 1px solid #7c7c7c; padding: 5px; }
            QPushButton:pressed { background-color: #7c7c7c; }
            QLabel { color: #dcdcdc; }
            QTabWidget::pane { border: 1px solid #5c5c5c; }
            QTabBar::tab { background: #3c3c3c; padding: 10px; }
            QTabBar::tab:selected { background: #5c5c5c; }
            QTabBar::tab:hover { background: #7c7c7c; }
        """)

    def setup_layouts(self):
        self.main_layout = QVBoxLayout()

        connection_layout = self.create_connection_layout()
        custom_command_layout = self.create_custom_command_layout()
        button_layout = self.create_button_layout()

        self.command_output = QTextEdit()
        self.command_output.setReadOnly(True)
        self.status_label = QLabel('Connection Not Tested')
        self.status_label.setStyleSheet('color: red')

        self.main_layout.addLayout(connection_layout)
        self.main_layout.addWidget(self.status_label)
        self.main_layout.addLayout(button_layout)
        self.main_layout.addWidget(self.create_tab_widget())
        self.main_layout.addLayout(custom_command_layout)
        self.main_layout.addWidget(self.command_output)
        self.setLayout(self.main_layout)

    def create_connection_layout(self):
        layout = QHBoxLayout()
        self.host_input = QLineEdit('192.168.86.71')
        self.host_input.setPlaceholderText('IP Address')
        self.port_input = QLineEdit('23')
        self.port_input.setPlaceholderText('Port')
        self.projector_id_input = QLineEdit('01')
        self.projector_id_input.setPlaceholderText('ID')

        self.connect_button = QPushButton('Test Connection')
        self.connect_button.clicked.connect(self.connect)

        layout.addWidget(QLabel('IP Address:'))
        layout.addWidget(self.host_input)
        layout.addWidget(QLabel('Port:'))
        layout.addWidget(self.port_input)
        layout.addWidget(QLabel('ID:'))
        layout.addWidget(self.projector_id_input)
        layout.addWidget(self.connect_button)
        return layout

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
        layout_power = QHBoxLayout()
        layout_options = QHBoxLayout()
        self.power_on_button = QPushButton('On')
        self.power_off_button = QPushButton('Off')
        self.menu_button = QPushButton('Menu')
        self.return_button = QPushButton('Return')
        self.exit_button = QPushButton('Exit')

        self.power_on_button.clicked.connect(lambda: self.send_command(system_buttons['Power On']))
        self.power_off_button.clicked.connect(lambda: self.send_command(system_buttons['Power Off']))
        self.menu_button.clicked.connect(lambda: self.send_command(system_buttons['Menu']))
        self.return_button.clicked.connect(lambda: self.send_command(system_buttons['Return']))
        self.exit_button.clicked.connect(lambda: self.send_command(system_buttons['Exit']))

        layout_power.addWidget(self.power_on_button)
        layout_power.addWidget(self.power_off_button)

        layout_options.addWidget(self.menu_button)
        layout_options.addWidget(self.return_button)
        layout_options.addWidget(self.exit_button)

        layout.addLayout(layout_power)
        layout.addSpacing(5)
        layout.addLayout(layout_options)
        layout.addSpacing(20)

        return layout

    def create_tab_widget(self):
        tab_widget = QTabWidget()

        tab_widget.addTab(self.create_controller_tab(), 'Controller')
        tab_widget.addTab(self.create_advanced_warp_tab(), 'Advanced Warp')
        tab_widget.addTab(self.create_test_patterns_tab(), 'Test Patterns')
        tab_widget.addTab(self.create_display_controls_tab(), 'Display Controls')
        self.tabs = tab_widget
        return tab_widget

    def create_controller_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        navigation_group = self.create_navigation_group()
        lens_shift_group = self.create_lens_shift_group()
        zoom_group = self.create_zoom_group()

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

        grid_background_group = self.create_button_group("Grid Background", grid_background_buttons)
        warp_inner_group = self.create_button_group("Warp Inner", advanced_warp_inner_buttons)
        grid_color_group = self.create_button_group("Grid Color", grid_color_buttons)
        grid_points_group = self.create_button_group("Grid Points", grid_points_buttons)

        layout.addWidget(grid_background_group)
        layout.addWidget(warp_inner_group)
        layout.addWidget(grid_color_group)
        layout.addWidget(grid_points_group)

        tab.setLayout(layout)
        return tab

    def slider_refresh(self, slider: QSlider, label: QLabel, command: str, quite: bool = True):

        value = self.read_command(command, quite)

        # Block signals before updating the slider value
        slider.blockSignals(True)
        slider.setValue(value)
        slider.blockSignals(False)

        label.setText(f"{label.text().split(':')[0]}: {value}")

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
        extreme_black_group = self.create_button_group('Extreme Black', extreme_black_buttons)
        dynamic_black_group = self.create_button_group('Dynamic Black', dynamic_black_buttons)
        aspect_ratio_group = self.create_button_group('Aspect Ratio', aspect_ratio_buttons)
        wall_color_group = self.create_button_group('Wall Color', wall_color_buttons)

        #picture_settings_group = self.create_button_group('Picture Settings', picture_settings_buttons)

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
        layout.addWidget(extreme_black_group)
        layout.addWidget(dynamic_black_group)
        layout.addWidget(aspect_ratio_group)
        layout.addWidget(wall_color_group)
        layout.addWidget(wall_color_group)
        layout.addWidget(slider_group)
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
        self.main_layout.setEnabled(enabled)

    def valid_connection(self) -> bool:
        if not validate_ip(self.host_input.text()) or not validate_port(
                self.port_input.text()) or not validate_projector_id(self.projector_id_input.text()):
            self.update_output("Invalid IP, Port, or Projector ID")
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
            self.update_output(f'Error: [{str(e)}]')

        return 0

    def send_command(self, command: str, quite: bool = False):

        if not self.valid_connection():
            return
        final_command = command.replace('XX', self.projector_id_input.text().zfill(2))
        if not quite:
            self.update_output(f'Sending Command: [{final_command}]')
        self.set_ui_enabled(False)
        result = send_telnet_command(final_command, self.host_input.text(), self.port_input.text())
        if result['success']:
            response_code = result['code']
            if not quite:
                self.update_output(f'Response: [{response_code}]')
        else:
            error_code = result['error']
            if not quite:
                self.update_output(f'Error: {error_code}')
        self.set_ui_enabled(True)
        return result

    def connect(self):
        result = test_telnet_connection(self.host_input.text(), self.port_input.text())
        if result['success']:
            self.status_label.setText("Connection Test Passed")
            self.status_label.setStyleSheet('color: green')
            self.update_output("Connected successfully")
        else:
            error_code = result['error']
            self.status_label.setText(f'Error: {error_code}')
            self.status_label.setStyleSheet('color: red')
            self.update_output(f'Error: {error_code}')

    def update_output(self, text):
        self.command_output.append(text)
        self.command_output.ensureCursorVisible()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ProjectorController()
    ex.show()
    sys.exit(app.exec_())
