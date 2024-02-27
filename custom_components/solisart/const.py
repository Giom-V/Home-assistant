"""Constants for the Solisart integration."""

DOMAIN = "solisart"
URL = "https://my.solisart.fr/"
URL_DATA = "https://my.solisart.fr/admin/divers/ajax/lecture_valeurs_donnees.php"
URL_UPDATE = "https://my.solisart.fr/admin/divers/ajax/ecriture_valeurs_donnees.php"
SOLISART_ID = "U0MxTTIwMjM0MDAx" #TODO: This should be recovered when logging in

# Data ids from Solisart
HOLIDAY_MODE = 135
HOLIDAY_MODE_TEMPERATURE = 134
T1_PANELS_OUT = 584
T2_PANELS_IN = 585
T4_TANK_TOP = 586
T3_TANK_BOTTOM = 587
T7_CIRCUIT_COLD = 590
T8_CIRCUIT_HOT = 591
T9_EXTERIOR = 592
Z1_SPA = 594
Z2_FIRST_FLOOR = 595
Z3_GROUND_FLOOR = 596
Z7_UNDERFLOOR = 597
HEAT_PUMP_STATUS = 606
C4_WATER_HEAT_PUMP = 614
C5_WATER_SUN = 615
C6_SPA = 617
C7_UNDERFLOOR = 618
C2_FIRST_FLOOR = 619
C3_GROUND_FLOOR = 620
S10_SPA_FILTER = 623
V3V_HEAT_PUMP = 628
V3V_SUN = 627 #To be confirmed, maybe it just never work
V3V_SUN2 = 629 #To be confirmed, maybe it just never work
TARGET_SPA = 631
TARGET_FIRST_FLOOR = 632
TARGET_GROUND_FLOOR = 633
TARGET_UNDERFLOOR = 634
TARGET_WATER = 635

# Specific values
HOLIDAY_MODE_ON = "checked"
HOLIDAY_MODE_OFF = ""
HEAT_PUMP_ON = "On"
HEAT_PUMP_OFF = "Off"

# Sensors
TEMPERATURE_SENSORS = [
    ["Température vacances", HOLIDAY_MODE_TEMPERATURE],
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
    ["V3V PAC", V3V_HEAT_PUMP],
    ["V3V panneaux solaires", V3V_SUN],
    ["V3V 629", V3V_SUN2],
]