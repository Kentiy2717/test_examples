# Константы для test_FB_DP

START_VALUE = {
    'Input':       {'register': 40111,  'start_value': False},
    'ChFlt':       {'register': 40112,  'start_value': False},
    'ModFlt':      {'register': 40113,  'start_value': False},
    'SensFlt':     {'register': 40114,  'start_value': False},
    'ExtFlt':      {'register': 40115,  'start_value': False},
    'Period':      {'register': 40401,  'start_value': 100},
    'T01':         {'register': 8000,   'start_value': 0},
    'CmdOp':       {'register': 8001,   'start_value': 4},
}

WORK_MODES = ('Oos', 'Imt1', 'Imt0', 'Fld', 'Tst')
SWITCH = ('Invers', 'MsgOff')
INPUT_REGISTER = START_VALUE['Input']['register']
CMDOP_REGISTER = START_VALUE['CmdOp']['register']
OUT_REGISTER = 40013
STATUS1_REGISTER = 7200
STATUS2_REGISTER = 7202
BAD_REGISTER = 40014
OOS_REGISTER = 40015
TST_REGISTER = 40016
IMT1_REGISTER = 40017
IMT0_REGISTER = 40018
FLD_REGISTER = 40019
IECINIT_REGISTER = 40020
PANEL_MODE_REGISTER = 23274
PANEL_STATE_REGISTER = 23275
PANEL_ALM_REGISTER = 23276
PANEL_SIG_REGISTER = 23277

# Команды управления (CmdOp)
CMDOP = {
    'Oos':        1,	                  # Установить режим "Маскирование"
    'Imt1':       2,	                  # Установить режим "Имитация"
    'Imt0':       3,	                  # Установить режим "Имитация"
    'Fld':        4,	                  # Установить режим "Полевая обработка"
    'Tst':        5,	                  # Установить режим "Тестирование"
    'Invers':     10,	                  # Включить/Отключить инверсию
    'MsgOff':     20,       # нет ножки   # Включить/Отключить Генерацию сообщений
    'Kvitir':     31,	                  # Квитировать
}

# Статус слово 1 (Status1)
STATUS1 = {
    'Oos':        1,    # Включен режим "Маскирование"
    'Imt1':       2,    # Включен режим "Имитация 1"
    'Imt0':       3,    # Включен режим "Имитация 0"
    'Fld':        4,    # Включен режим "Полевая обработка"
    'Tst':        5,    # Включен режим "Тестирование"
    'DP_Oos':     6,    # Состояние "Замаскирован"
    'Bad':        7,    # Недостоверность значения
    'DP_Act':     8,    # Параметр сработал
    'DP_Inact':   9,    # Параметр не активен
    'Invers':     10,   # Инверсия входного сигнала
    'MsgOff':     20,   # Генерация сообщений отключена
    'Kvitir':     31,   # Требуется квитирование
}

STATUS2 = {           # !!!! ОДИНАКОВО С PanelAlm !!!!!
    'ChFlt':      0,  # Неисправность канала
    'ModFlt':     1,  # Неисправность модуля
    'SensFlt':    2,  # Неисправность датчика
    'ExtFlt':     3,  # Внешняя ошибка
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
}

# Режим управления для Панели оператора (PanelMode)
PANELMODE = {
    'None':       0,    # Режим не установлен
    'Oos':        1,    # Режим "Маскирование"
    'Imt1':       2,    # Режим "Имитация 1"
    'Imt0':       3,    # Режим "Имитация 0"
    'Fld':        4,    # Режим "Полевая обработка"
    'Tst':        5,    # Режим "Тестирование"
}

# Текущее состояние	(PanelState)
PANELSTATE = {
    'None':      0,	    # Состояние не установлено
    'Oos':       1,	    # Состояние замаскирован
    'Bad':       2,	    # INVALID. Параметр недостоверен
    'DP_Act':    3,     # Параметр сработал
    'DP_Inact':  4,     # Параметр не активен
}

# Текущее состояние	(PanelSig)
PANELSIG = {
    'Invers':    0,     # Инверсия входного сигнала
    'MsgOff':    1,	    # 'Генерация сообщений отключена'],
    'Kvitir':    2  	# 'Требуется квитирование'],
}
