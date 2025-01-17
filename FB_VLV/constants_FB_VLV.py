# Константы для test_FB_VLV

START_VALUE = {
    'Tls':         {'register': 11000, 'pre_values': , 'start_value': },
    'Tmp':         {'register': 11001, 'pre_values': , 'start_value': },
    'Terr':        {'register': 11002, 'pre_values': , 'start_value': },
    'Tpulse':      {'register': 11003, 'pre_values': , 'start_value': },
    'CmdOp':       {'register': 11800, 'pre_values': , 'start_value': },
    'Delta':       {'register': 40508, 'pre_values': , 'start_value': },
    'SetPos':      {'register': 12800, 'pre_values': , 'start_value': },
    'AutSet':      {'register': 40510, 'pre_values': , 'start_value': },
    'InPos':       {'register': 40512, 'pre_values': , 'start_value': },
    'RLControl':   {'register': 40123, 'pre_values': , 'start_value': },
    'RLKey':       {'register': 40124, 'pre_values': , 'start_value': },
    'ManClose':    {'register': 40125, 'pre_values': , 'start_value': },
    'ManOpen':     {'register': 40126, 'pre_values': , 'start_value': },
    'ManStop':     {'register': 40127, 'pre_values': , 'start_value': },
    'AutClose':    {'register': 40128, 'pre_values': , 'start_value': },
    'AutOpen':     {'register': 40129, 'pre_values': , 'start_value': },
    'FbkClose':    {'register': 40130, 'pre_values': , 'start_value': },
    'FbkOpen':     {'register': 40131, 'pre_values': , 'start_value': },
    'Fault':       {'register': 40135, 'pre_values': , 'start_value': },
    'ModDI_FLT':   {'register': 40136, 'pre_values': , 'start_value': },
    'ModDO_FLT':   {'register': 40137, 'pre_values': , 'start_value': },
    'ExtFlt':      {'register': 40141, 'pre_values': , 'start_value': },
    'Permission':  {'register': 40143, 'pre_values': , 'start_value': },
    'InterlockO':  {'register': 40144, 'pre_values': , 'start_value': },
    'InterlockC':  {'register': 40145, 'pre_values': , 'start_value': },
    'Protect':     {'register': 40146, 'pre_values': , 'start_value': },
    'SafeOn':      {'register': 40147, 'pre_values': , 'start_value': },
    'SafePos':     {'register': 40148, 'pre_values': , 'start_value': },
    'PosFbk':      {'register': 40149, 'pre_values': , 'start_value': },
}

WORK_MODES = ('Oos', 'Bad', 'Local', 'Imt', 'Auto', 'Man')
#SWITCH = ('MsgOff', 'WHLimEn', 'AHLimEn')
# INPUT_REGISTER = START_VALUE['Input']['register']
# CMDOP_REGISTER = START_VALUE['CmdOp']['register']
OUT_REGISTER = 40514
# STATUS1_REGISTER = 16854
# STATUS2_REGISTER = 16856
BAD_REGISTER =   40035
OOS_REGISTER =   40036
LOCAL_REGISTER = 40037
IMT_REGISTER =   40038
AUTO_REGISTER =  40039
MAN_REGISTER =   40040 
# IECINIT_REGISTER = 40028
PANEL_IMIT = 
PANEL_MOVE = 
PANEL_POS =  
PANEL_MODE_REGISTER =  25074
PANEL_STATE_REGISTER = 25075
PANEL_ALM_REGISTER =   25076
PANEL_SIG_REGISTER =   25077

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
