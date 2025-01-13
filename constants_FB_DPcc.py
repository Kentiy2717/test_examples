# Константы для test_FB_DPcc

START_VALUE = {
    'Input':      {'register': 40506,   'start_value': 5.0},
    'DeltaV':     {'register': 18066,   'start_value': 0.0},
    'Period':     {'register': 40403,   'start_value': 100},
    'MaxEV':      {'register': 18058,   'start_value': 20.0},
    'MinEV':      {'register': 18056,   'start_value': 4.0},
    'T01':        {'register': 17654,   'start_value': 0},
    'AHLim':      {'register': 18060,   'start_value': 15.0},
    'WHLim':      {'register': 18062,   'start_value': 10.0},
    'Hyst':       {'register': 18064,   'start_value': 0.5},
    'AlarmOff':   {'register': 40116,   'start_value': False},
    'ChFlt':      {'register': 40117,   'start_value': False},
    'ModFlt':     {'register': 40118,   'start_value': False},
    'SensFlt':    {'register': 40119,   'start_value': False},
    'ExtFlt':     {'register': 40120,   'start_value': False},
    'WHLimEn':    {'register': 40121,   'start_value': False},
    'AHLimEn':    {'register': 40122,   'start_value': False},
    'CmdOp':      {'register': 17655,   'start_value': 4},
}

WORK_MODES = ('Oos', 'Imt2', 'Imt1', 'Imt0', 'Fld', 'Tst')
SWITCH = ('MsgOff', 'WHLimEn', 'AHLimEn')
INPUT_REGISTER = START_VALUE['Input']['register']
CMDOP_REGISTER = START_VALUE['CmdOp']['register']
OUT_REGISTER = 18054
STATUS1_REGISTER = 16854
STATUS2_REGISTER = 16856
BAD_REGISTER = 40021
OOS_REGISTER = 40022
TST_REGISTER = 40023
IMT0_REGISTER = 40024
IMT1_REGISTER = 40025
IMT2_REGISTER = 40026
FLD_REGISTER = 40027
AH_ACT = 40029
WH_ACT = 40030
IECINIT_REGISTER = 40028
PANEL_MODE_REGISTER = 27724
PANEL_STATE_REGISTER = 27725
PANEL_ALM_REGISTER = 27726
PANEL_SIG_REGISTER = 27727

# Команды управления (CmdOp)
CMDOP = {
    'Oos':        1,    # Установить режим "Маскирование"
    'Imt0':       2,    # Установить режим "Имитация 0"
    'Imt1':       3,    # Установить режим "Имитация 1"
    'Fld':        4,    # Установить режим "Полевая обработка"
    'Tst':        5,    # Установить режим "Тестирование"
    'MsgOff':     20,   # Включить/Отключить Генерацию сообщений
    'FiltOff':    21,   # Включить/Отключить Фильтр
    'WHLimEn':    26,	# Включить/Отключить Максимально предельный порог
    'AHLimEn':    27,	# Включить/Отключить Максимально аварийный порог
    'Imt2':       30,   # Установить режим "Имитация 2"
    'Kvitir':     31,   # Квитировать
}

# Статус слово 1 (Status1)
STATUS1 = {
    'Oos':        1,    # Включен режим "Маскирование"
    'Imt1':       3,    # Включен режим "Имитация 1"
    'Imt0':       2,    # Включен режим "Имитация 0"
    'Fld':        4,    # Включен режим "Полевая обработка"
    'Tst':        5,    # Включен режим "Тестирование"
    'DP_Oos':     6,    # Состояние "Замаскирован"
    'Bad':        7,    # Недостоверность значения
    'OutNorm':    11,   # Значение в норме
    'WHAct':      13,   # Сработала верхняя предельная уставка (ВПУ)
    'AHAct':      14,   # Сработала верхняя аварийная уставка (ВАУ)
    'MsgOff':     20,   # Генерация сообщений отключена
    'WHLimEn':    26,   # Максимально предельный порог включен
    'AHLimEn':    27,   # Максимально аварийный порог включен
    'Imt2':       30,   # Включен режим "Имитация 2"
    'Kvitir':     31,   # Требуется квитирование
}

STATUS2 = {           # !!!! ОДИНАКОВО С PanelAlm !!!!!
    'ChFlt':      0,  # Неисправность канала
    'ModFlt':     1,  # Неисправность модуля
    'SensFlt':    2,  # Неисправность датчика
    'ExtFlt':     3,  # Внешняя ошибка
    'HightErr':   4,  # Выход за верхнюю границу измерения
    'LowErr':     5,  # Выход за нижнюю границу измерения
}
'''
Словарь с именем и номером бита для Status2 и PanelAlm.\n
!!!!!! ЗНАЧЕНИЯ ДЛЯ Status2 ОДИНАКОВЫ С PanelAlm !!!!!!!
'''

VALUE_UNRELIABILITY = {
    'ChFlt':      'Неисправность канала',
    'ModFlt':     'Неисправность модуля',
    'SensFlt':    'Неисправность датчика',
    'ExtFlt':     'Внешняя ошибка',
    'HightErr':   'Выход за верхнюю границу измерения',
    'LowErr':     'Выход за нижнюю границу измерения',
}

# Режим управления для Панели оператора (PanelMode)
PANELMODE = {
    'None':       0,    # Режим не установлен
    'Oos':        1,    # Режим "Маскирование"
    'Imt0':       2,    # Режим "Имитация 0"
    'Imt1':       3,    # Режим "Имитация 1"
    'Imt2':       4,    # Режим "Имитация 2"
    'Fld':        5,    # Режим "Полевая обработка"
    'Tst':        6,    # Режим "Тестирование"
}

# Текущее состояние	(PanelState)
PANELSTATE = {
    'None':      0,	    # Состояние не установлено
    'Oos':       1,	    # Состояние замаскирован
    'Bad':       2,	    # INVALID. Параметр недостоверен
    'WHAct':     3,     # H. Верхний предаварийный предел
    'AHAct':     4,     # HH. Верхний аварийный предел
    'OutNorm':   5,	    # В норме
}

# Текущее состояние	(PanelSig)
PANELSIG = {
    'MsgOff':    0,	    # Генерация сообщений отключена
    'WHLimEn':   1,     # Максимально предельный порог включен
    'AHLimEn':   2,     # Максимально аварийный порог включен
    'Kvitir':    3  	# Требуется квитирование
}
