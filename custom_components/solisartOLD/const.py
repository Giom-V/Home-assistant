"""Constants for the Solisart integration."""

DOMAIN = "solisart"
URL = "https://my.solisart.fr/"
URL_DATA = "https://my.solisart.fr/admin/divers/ajax/lecture_valeurs_donnees.php"
URL_UPDATE = "https://my.solisart.fr/admin/divers/ajax/ecriture_valeurs_donnees.php"
SOLISART_ID = "U0MxTTIwMjM0MDAx"  # TODO: This should be recovered when logging in

# Data ids from Solisart
# Managed in from https://docs.google.com/spreadsheets/d/1zSFM3KADlwYu5-jf2CWX80POjJc4NUYBUyo_BnBybks/edit#gid=0
HOLIDAY_MODE_TEMPERATURE = 134
HOLIDAY_MODE = 135
BOOST_UNDERFLOOR = 178
BOOST_FIRST_FLOOR = 179
BOOST_GROUND_FLOOR = 180
BOOST_SPA = 181
BOOST_WATER = 184
T1_PANELS_OUT = 584
T2_PANELS_IN = 585
T4_TANK_TOP = 586
T3_TANK_BOTTOM = 587
T7_CIRCUIT_COLD = 590
T8_CIRCUIT_HOT = 591
T9_EXTERIOR = 592
Z7_UNDERFLOOR = 594  # ID could be mismatched with spa
Z2_FIRST_FLOOR = 595
Z3_GROUND_FLOOR = 596
Z1_SPA = 597  # ID could be mismatched with underfloor
HEAT_PUMP_STATUS = 606
C4_WATER_HEAT_PUMP = 614
C5_WATER_SUN = 615
C6_SPA = 617
C7_UNDERFLOOR = 618
C2_FIRST_FLOOR = 619
C3_GROUND_FLOOR = 628
S10_SPA_FILTER = 623
V3V_HEAT_PUMP = 628
V3V_SUN = 627  # To be confirmed, maybe it just never work
V3V_SUN2 = 629  # To be confirmed, maybe it just never work
TARGET_UNDERFLOOR = 631
TARGET_FIRST_FLOOR = 632
TARGET_GROUND_FLOOR = 633
TARGET_SPA = 634
TARGET_WATER = 635
PROG_CONFORT_UNDERFLOOR = 157
PROG_CONFORT_FIRST_FLOOR = 158
PROG_CONFORT_GROUND_FLOOR = 159
PROG_CONFORT_SPA = 160
PROG_CONFORT_WATER = 153
PROG_REDUCED_UNDERFLOOR = 164
PROG_REDUCED_FIRST_FLOOR = 165
PROG_REDUCED_GROUND_FLOOR = 166
PROG_REDUCED_SPA = 167
PROG_REDUCED_WATER = 170
PROG_BOOST_UNDERFLOOR = 171
PROG_BOOST_FIRST_FLOOR = 172
PROG_BOOST_GROUND_FLOOR = 173
PROG_BOOST_SPA = 174
PROG_BOOST_WATER = 177
MODE_UNDERFLOOR = 150
MODE_FIRST_FLOOR = 151
MODE_GROUND_FLOOR = 152
MODE_SPA = 153
MODE_WATER = 156

# Specific values
SWITCH_IS_ON = "checked"
HEAT_PUMP_ON = "On"
HEAT_PUMP_OFF = "Off"
BOOST_ON = "1"
BOOST_OFF = "0"
MODE_OFF = "0"
MODE_SUN_ONLY = "1"
MODE_HEATPUMP = "2"

# Custom values
MAX_TEMPERATURE = 25
MIN_TEMPERATURE = 10
MAX_OFFSET = 5
MIN_OFFSET = 0

# Sensors
TEMPERATURE_SENSORS = [
    ["Température sortie panneaux", T1_PANELS_OUT],
    ["Température entrée panneaux", T2_PANELS_IN],
    ["Température ballon bas", T4_TANK_TOP],
    ["Température ballon haut", T3_TANK_BOTTOM],
    ["Température circuit froid", T7_CIRCUIT_COLD],
    ["Température circuit chaud", T8_CIRCUIT_HOT],
    ["Température extérieure solisart", T9_EXTERIOR],
    ["Température Spa", Z1_SPA],
    ["Température étage", Z2_FIRST_FLOOR],
    ["Température RDC", Z3_GROUND_FLOOR],
    ["Température plancher", Z7_UNDERFLOOR],
    ["Température cible SPA", TARGET_SPA],
    ["Température cible étage", TARGET_FIRST_FLOOR],
    ["Température cible RDC", TARGET_GROUND_FLOOR],
    ["Température cible plancher", TARGET_UNDERFLOOR],
    ["Température cible eau chaude sanitaire", TARGET_WATER],
]

PUMP_SENSORS = [
    ["Circulateur PAC eau chaude sanitaire", C4_WATER_HEAT_PUMP],
    ["Circulateur solaire eau chaude sanitaire", C5_WATER_SUN],
    ["Circulateur SPA", C6_SPA],
    ["Circulateur plancher", C7_UNDERFLOOR],
    ["Circulateur étage", C2_FIRST_FLOOR],
    ["Circulateur RDC", C3_GROUND_FLOOR],
    ["Filtre SPA ", S10_SPA_FILTER],
    [
        "V3V PAC",
        V3V_HEAT_PUMP,
    ],  # TODO: Should be valve (https://developers.home-assistant.io/docs/core/entity/valve/)
    ["V3V panneaux solaires", V3V_SUN],
    ["V3V 629", V3V_SUN2],
]

# SWITCHES
SWITCH_ENTITIES = [
    [
        "Boost RDC",
        "mdi:radiator",
        BOOST_GROUND_FLOOR,
        SWITCH_IS_ON,
        BOOST_ON,
        BOOST_OFF,
    ],
    [
        "Boost étage",
        "mdi:radiator",
        BOOST_FIRST_FLOOR,
        SWITCH_IS_ON,
        BOOST_ON,
        BOOST_OFF,
    ],
    [
        "Boost eau chaude",
        "mdi:water-boiler",
        BOOST_WATER,
        SWITCH_IS_ON,
        BOOST_ON,
        BOOST_OFF,
    ],
    [
        "Boost SPA",
        "mdi:water-boiler",
        BOOST_SPA,
        SWITCH_IS_ON,
        BOOST_ON,
        BOOST_OFF,
    ],
    [
        "Boost plancher chauffant",
        "mdi:water-boiler",
        BOOST_UNDERFLOOR,
        SWITCH_IS_ON,
        BOOST_ON,
        BOOST_OFF,
    ],
    [
        "Mode vacances Solisart",
        "mdi:home-export-outline",
        HOLIDAY_MODE,
        SWITCH_IS_ON,
        BOOST_ON,
        BOOST_OFF,
    ],
]

# Temperature inputs
TEMP_INPUTS = [
    ["Température vacances", HOLIDAY_MODE_TEMPERATURE],
    ["Température confort plancher", PROG_CONFORT_UNDERFLOOR],
    ["Température confort étage", PROG_CONFORT_FIRST_FLOOR],
    ["Température confort RDC", PROG_CONFORT_GROUND_FLOOR],
    ["Température confort spa", PROG_CONFORT_SPA],
    ["Température confort eau chaude", PROG_CONFORT_WATER],
    ["Température réduite plancher", PROG_REDUCED_UNDERFLOOR],
    ["Température réduite étage", PROG_REDUCED_FIRST_FLOOR],
    ["Température réduite RDC", PROG_REDUCED_GROUND_FLOOR],
    ["Température réduite spa", PROG_REDUCED_SPA],
    ["Température réduite eau chaude", PROG_REDUCED_WATER],
]
OFFSET_INPUTS = [
    ["Offset boost plancher", PROG_BOOST_UNDERFLOOR],
    ["Offset boost étage", PROG_BOOST_FIRST_FLOOR],
    ["Offset boost RDC", PROG_BOOST_GROUND_FLOOR],
    ["Offset boost spa", PROG_BOOST_SPA],
    ["Offset boost eau chaude", PROG_BOOST_WATER],
]

# Mode selects
MODE_SELECTS = [
    ["Mode plancher", MODE_UNDERFLOOR],
    ["Mode étage", MODE_FIRST_FLOOR],
    ["Mode RDC", MODE_GROUND_FLOOR],
    ["Mode spa", MODE_SPA],
    ["Mode eau chaude", MODE_WATER],
]
MODES = [
    ["Solaire seul", MODE_SUN_ONLY],
    ["Solaire+PAC", MODE_HEATPUMP],
    ["Off", MODE_OFF],
]
