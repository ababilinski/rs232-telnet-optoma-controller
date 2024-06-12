# Define buttons and their associated Telnet commands
directional_buttons = {
    'Up': '~XX140 10',
    'Down': '~XX140 14',
    'Left': '~XX140 11',
    'Right': '~XX140 13',
    'Enter': '~XX140 12',
}

zoom_buttons = {
    '+': '~XX307 1',
    '-': '~XX307 2'
}

lens_shift_buttons = {
    'Up': '~XX84 3',
    'Down': '~XX84 4',
    'Left': '~XX84 5',
    'Right': '~XX84 6',
}

system_buttons = {
    "Power Status": "~XX124 1",
    "Power": "~XX140 1",
    "Power On": "~XX00 1",
    "Power Off": "~XX00 0",
    "Menu": "~XX140 20",
    "Pattern": "~XX140 73",
    "Exit": "~XX140 74",
    "Return": "~XX140 82",
}
advanced_warp_inner_buttons = {
    "Warp Inner On": "~XX146 0",
    "Warp Inner Off": "~XX146 1",
}
advanced_warp_buttons = {
    "Advanced Calibration": "~XX142 5",
    "Advanced 9x9 Grid": "~XX144 4",
    "Advanced 5x5 Grid": "~XX144 3",
    "Warp Inner On": "~XX146 0",
    "Warp Inner Off": "~XX146 1",
    "Warp Setting": "~XX543 6",
    "Blend Setting": "~XX169 1",
}
image_shift = {
    "Horizontal Shift": "~XX365 0~100",
    "Vertical Shift": "~XX366 0~100"
}

grid_color_buttons = {
    "Green": "~XX143 1",
    "Magenta": "~XX143 2",
    "Red": "~XX143 3",
    "Cyan": "~XX143 4"
}

grid_background_buttons = {
    "Black": "~XX145 1",
    "Transparent": "~XX145 2"
}

wall_color_buttons = {
    "Off": "~XX506 0",
    "BlackBoard": "~XX506 1",
    "Light Yellow": "~XX506 7",
    "Light Green": "~XX506 3",
    "Light Blue": "~XX506 4",
    "Pink": "~XX506 5",
    "Gray": "~XX506 6" 
}

aspect_ratio_buttons = {
    "Auto": "~XX60 7",
    "4:3": "~XX60 1",
    "16:9": "~XX60 2",
    "16:10": "~XX60 3",
    "LBX": "~XX60 5",
    "Native": "~XX60 6"
}
dynamic_black_buttons = {
    "Dynamic Black On": "~XX506 0",
    "Dynamic Black Off": "~XX506 1"
}
extreme_black_buttons = {
    "Extreme Black Off": "~XX218 0",
    "Extreme Black On": "~~XX218 1"
}
picture_mode_buttons = {
    "None": "~XX20 0",
    "Presentation": "~XX506 1",
    "Bright": "~XX506 2",
    "Cinema": "~XX506 3",
    "sRGB": "~XX506 4",
    "HDR": "~XX506 21",
    "DICOM SIM.": "~XX506 13",
    "Blending": "~XX506 19"
}

gamma_mode_buttons = {
    "Film": "~XX35 1",
    "Graphics": "~XX35 3",
    "Standard(2.2)": "~XX35 4",
    "Vivid": "~XX35 21",
    "Blackboard": "~XX35 10",
    "DICOM SIM.": "~XX35 5",
    "1.8": "~XX35 6",
    "2.0": "~XX35 13",
    "2.4": "~XX35 12",
    "2.6": "~XX35 8"
}
hdr_buttons = {
    "Auto": "~XX20 1",
    "HDR Off": "~XX565 0"
}
picture_settings_buttons = {
    "Brightness +": "~XX46 2",
    "Brightness -": "~XX46 1",
    "Contrast -": "~XX47 1",
    "Contrast +": "~XX47 2",
}
picture_settings_slider = {
    "Get Contrast": "~XX126 1",
    "Set Contrast": "~XX22",
    "Get Brightness": "~XX125 1",
    "Set Brightness": "~XX21"
    
    
}

grid_points_buttons = {
    "2x2": "~XX144 1",
    "3x3": "~XX144 2",
    "5x5": "~XX144 3",
    "9x9": "~XX144 4",
    "17x17": "~XX144 5",
}

test_pattern_buttons = {
    "Off": "~XX195 0",
    "Green Grid": "~XX195 3",
    "Magenta Grid": "~XX195 4",
    "White Grid": "~XX195 1",
    "NSI Contrast 4x4": "~XX195 14",
}

color_settings = {
    "Color": "~XX45 0~100",
    "Tint": "~XX44 0~100"
}

gamma_settings = {
    "Film": "~XX35 1",
    "Graphics": "~XX35 3"
}
communication_settings = {
    "Get Projector ID": "~XX558 18"
}
system_info_response = {
    "0": "Standby Mode",
    "1": "Warming up ...",
    "2": "Cooling Down ...",
    "3": "Out of Range",
    "4": "lightsource Fail ( LED Fail)",
    "5": "Thermal Switch Error",
    "6": "Fan Lock",
    "7": "Over Temperature",
    "8": "LightSource Hours Running Out",
    "9": "Cover Open",
    "10": "lightsource Ignite Fail",
    "11": "Format Board Power On Fail",
    "12": "Color Wheel Unexpected Stop",
    "13": "Over Temperature",
    "14": "FAN 1 Lock",
    "15": "FAN 2 Lock",
    "16": "FAN 3 Lock",
    "17": "FAN 4 Lock",
    "18": "FAN 5 Lock",
    "19": "LAN fail then restart",
    "20": "LD lower than 60%",
    "21": "LD NTC (1) Over Temperature",
    "22": "LD NTC (2) Over Temperature",
    "23": "High Ambient Temperature",
    "24": "System Ready",
    "26": "FAN 6 Lock",
    "27": "FAN 7 Lock",
    "28": "FAN 8 Lock",
    "29": "FAN 9 Lock",
    "30": "FAN 10 Lock",
    "31": "FAN 11 Lock",
    "32": "FAN 12 Lock",
    "33": "FAN 13 Lock",
    "34": "FAN 14 Lock"
}

