# Константы для test_fb_ap

START_VALUE = {
    'CmdOp':       {'register': 801,    'start_value': 4},
    'Input':       {'register': 40500,  'start_value': 12.0},
    'RangeMax':    {'register': 40504,	'start_value': 20.0},
    'RangeMin':    {'register': 40502,	'start_value': 4.0},
    'DeltaV':      {'register': 2022,   'start_value': 0.0},
    'Period':      {'register': 40400,  'start_value': 100},
    'ImitInput':   {'register': 2000,   'start_value': 50.0},
    'MaxEV':       {'register': 2006,   'start_value': 100.0},
    'MinEV':       {'register': 2004,   'start_value': 0.0},
    'T01':         {'register': 800,    'start_value': 1},
    'SpeedLim':    {'register': 2002,   'start_value': 5.0},
    'AHLim':       {'register': 2008,   'start_value': 90.0},
    'WHLim':       {'register': 2010,   'start_value': 80.0},
    'THLim':       {'register': 2012,   'start_value': 70.0},
    'TLLim':       {'register': 2014,   'start_value': 30.0},
    'WLLim':       {'register': 2016,   'start_value': 20.0},
    'ALLim':       {'register': 2018,   'start_value': 10.0},
    'Hyst':        {'register': 2020,   'start_value': 1.5},
    'Kf':          {'register': 2024,   'start_value': 0.85},
    'AlarmOff':    {'register': 40100,  'start_value': False},
    'ChFlt':       {'register': 40101,  'start_value': False},
    'ModFlt':      {'register': 40102,  'start_value': False},
    'SensFlt':     {'register': 40103,  'start_value': False},
    'ExtFlt':      {'register': 40104,  'start_value': False},
    'ALLimEn':     {'register': 40105,  'start_value': False},
    'WLLimEn':     {'register': 40106,  'start_value': False},
    'TLLimEn':     {'register': 40107,  'start_value': False},
    'THLimEn':     {'register': 40108,  'start_value': False},
    'WHLimEn':     {'register': 40109,  'start_value': False},
    'AHLimEn':     {'register': 40110,  'start_value': False},    
}




# Словарь с номерами регистров ([REGISTER]), со значениями для проверки ([VALUE][0], [VALUE][1]) и
# дефолтными значениями для записи необходимых данных для работы системы.
REGISTERS_AND_VALUE_WRITE_FOR_BEGIN_TEST = {  # LEGS
    'CmdOp':       {'register': 801,    'TEST_VALUES': [-4,   0, 4],        'START_VALUE': 4},          # номер регистра для записи команд управления
    'Input':       {'register': 40500,  'TEST_VALUES': [-4.1, 0.0, 12.0],   'START_VALUE': 12.0},          # номер регистра для чтения и записи аналогового параметра (нижний уровень).
    'RangeMax':    {'register': 40504,	'TEST_VALUES': [-4.1, 0.0, 20.0],   'START_VALUE': 20.0},        # Максимальное физическое значение.
    'RangeMin':    {'register': 40502,	'TEST_VALUES': [-4.1, 0.0, 4.0],    'START_VALUE': 4.0},        # Минимальное физическое значение.
    'DeltaV':      {'register': 2022,   'TEST_VALUES': [-4.1, 0.5, 0.0],    'START_VALUE': 0.0},        # Дельта по значению.
    'Period':      {'register': 40400,  'TEST_VALUES': [-4,   0,   100],    'START_VALUE': 100},         # Период отправки в МЭК.
    'ImitInput':   {'register': 2000,   'TEST_VALUES': [-4.1, 0.0, 50.0],   'START_VALUE': 50.0},      # Значение имитации.
    'MaxEV':       {'register': 2006,   'TEST_VALUES': [-4.1, 0.0, 100.0],  'START_VALUE': 100.0},          # Максимальное инженерное значение 100 *С.
    'MinEV':       {'register': 2004,   'TEST_VALUES': [-4.1, 0.0, 0.0],    'START_VALUE': 0.0},          # Минимальное инженерное значение 0 *С.
    'T01':         {'register': 800,    'TEST_VALUES': [-4,   0,   1],      'START_VALUE': 1},            # Задержка на срабатывание уставки [мс].
    'SpeedLim':    {'register': 2002,   'TEST_VALUES': [-4.1, 0.0, 5.0],    'START_VALUE': 5.0},      # Максимальная скорость изменения параметра в промежутки времени.
    'AHLim':       {'register': 2008,   'TEST_VALUES': [-4.1, 0.0, 90.0],   'START_VALUE': 90.0},        # !!!!!!!!!!!!!!!!!ДОДЕЛАЯ ОПИСАНИЯ!!!!!!!!!!!!!!
    'WHLim':       {'register': 2010,   'TEST_VALUES': [-4.1, 0.0, 80.0],   'START_VALUE': 80.0},        # !!!!!!!!!!!!!!!!!ДОДЕЛАЯ ОПИСАНИЯ!!!!!!!!!!!!!! 
    'THLim':       {'register': 2012,   'TEST_VALUES': [-4.1, 0.0, 70.0],   'START_VALUE': 70.0},        # !!!!!!!!!!!!!!!!!ДОДЕЛАЯ ОПИСАНИЯ!!!!!!!!!!!!!! 
    'TLLim':       {'register': 2014,   'TEST_VALUES': [-4.1, 0.0, 30.0],   'START_VALUE': 30.0},        # !!!!!!!!!!!!!!!!!ДОДЕЛАЯ ОПИСАНИЯ!!!!!!!!!!!!!! 
    'WLLim':       {'register': 2016,   'TEST_VALUES': [-4.1, 0.0, 20.0],   'START_VALUE': 20.0},        # !!!!!!!!!!!!!!!!!ДОДЕЛАЯ ОПИСАНИЯ!!!!!!!!!!!!!! 
    'ALLim':       {'register': 2018,   'TEST_VALUES': [-4.1, 0.0, 10.0],   'START_VALUE': 10.0},        # !!!!!!!!!!!!!!!!!ДОДЕЛАЯ ОПИСАНИЯ!!!!!!!!!!!!!! 
    'Hyst':        {'register': 2020,   'TEST_VALUES': [-4.1, 0.0, 1.5],    'START_VALUE': 1.5},        # !!!!!!!!!!!!!!!!!ДОДЕЛАЯ ОПИСАНИЯ!!!!!!!!!!!!!!
    'Kf':          {'register': 2024,   'TEST_VALUES': [-4.1, 0.0, 0.85],   'START_VALUE': 0.85},        # !!!!!!!!!!!!!!!!!ДОДЕЛАЯ ОПИСАНИЯ!!!!!!!!!!!!!! 
}





OUT_REGISTER = 1200                 # номер регистра для чтения и записи аналогового параметра (средний уровень).
OUTMA_REGISTER = 1202               # номер регистра для чтения аналогового параметра в mA (средний уровень).
RANGEMIN_REGISTER = 40504	        # Максимальное физическое значение 5 В
RANGEMAX_REGISTER = 40502	        # Минимальное физическое значение 1 В
MINEV_REGISTER = 2004	            # Минимальное инженерное значение
MAXEV_REGISTER = 2006	            # Максимальное инженерное значение



STATUS1_REGISTER = 0                # номер регистра Status1
STATUS2_REGISTER = 2                # номер регистра Status2
PANEL_MODE_REGISTER = 21674         # номер регистра PanelMode
PANEL_STATE_REGISTER = 21675        # номер регистра PanelState
PANEL_ALM_REGISTER = 21676          # номер регистра PanelAlm
PANEL_SIG_REGISTER = 21677          # номер регистра PanelSig
MESSAGES_START_REGISTER = 29000     # номер стартового регистра с сообщениями
MESSAGES_STOP_REGISTER = 29100   # количество регистров с сообщениями (по 2 на сообщение)

# Команды управления (CmdOp)
CMDOP = {
    'Oos':        1,	                  # Установить режим "Маскирование"
    'Imit':       2,	                  # Установить режим "Имитация"
    'Fld':        4,	                  # Установить режим "Полевая обработка"
    'Tst':        5,	                  # Установить режим "Тестирование"
    'SpeedAct':   19,	                  # Включить/Отключить расчёт скорости изменения параметра
    'MsgOff':     20,       # нет ножки   # Включить/Отключить Генерацию сообщений
    'FiltOff':    21,	    # нет ножки   # Включить/Отключить Фильтр
    'ALLimEn':    22,	                  # Включить/Отключить Минимально аварийный порог
    'WLLimEn':    23,	                  # Включить/Отключить Минимально предельный порог
    'TLLimEn':    24,	                  # Включить/Отключить Минимально нормативный порог
    'THLimEn':    25,	                  # Включить/Отключить Максимально нормативный порог
    'WHLimEn':    26,	                  # Включить/Отключить Максимально предельный порог
    'AHLimEn':    27,	                  # Включить/Отключить Максимально аварийный порог
    'Kvitir':     31,	                  # Квитировать
}

SWITCHES_CMDOP = {
    'SpeedOff':   'Включить/Отключить расчёт скорости изменения параметра',
    'MsgOff':     'Включить/Отключить Генерацию сообщений',                  # нет ножки
    'FiltOff':    'Включить/Отключить Фильтр',                               # нет ножки
    'ALLimEn':    'Включить/Отключить Минимально аварийный порог',
    'WLLimEn':    'Включить/Отключить Минимально предельный порог',
    'TLLimEn':    'Включить/Отключить Минимально нормативный порог',
    'THLimEn':    'Включить/Отключить Максимально нормативный порог',
    'WHLimEn':    'Включить/Отключить Максимально предельный порог',
    'AHLimEn':    'Включить/Отключить Максимально аварийный порог',
}

SWITCHES_ST1_PANSIG_MESSAGE = {  # SWITCH
    # 'SpeedMax':   {'CmdOp': 18, 'St1': 18, 'PSig': 0, },  # 'Messages':хз пока 	 }, # надо тут?   # 'Скорость изменения параметра максимальна',],
    'SpeedOff':   {'CmdOp': 19, 'St1': 19, 'PSig': 1, },  # 'Messages':хз пока 	 },    # 'Расчёт скорости изменения параметра',],
    'MsgOff':     {'CmdOp': 20, 'St1': 20, 'PSig': 2, },  # 'Messages':хз пока 	 },      # 'Генерация сообщений отключена',],
    'FiltOff':    {'CmdOp': 21, 'St1': 21, 'PSig': 3, },  # 'Messages':хз пока 	 },        # 'Фильтр',],
    'ALLimEn':    {'CmdOp': 22, 'St1': 22, 'PSig': 4, },  # 'Messages':хз пока 	 },       # 'Минимально аварийный порог включен',],
    'WLLimEn':    {'CmdOp': 23, 'St1': 23, 'PSig': 5, },  # 'Messages':хз пока 	 },       # 'Минимально предельный порог включен',],
    'TLLimEn':    {'CmdOp': 24, 'St1': 24, 'PSig': 6, },  # 'Messages':хз пока 	 },       # 'Минимально нормативный порог включен',],
    'THLimEn':    {'CmdOp': 25, 'St1': 25, 'PSig': 7, },  # 'Messages':хз пока 	 },       # 'Максимально нормативный порог включен',],
    'WHLimEn':    {'CmdOp': 26, 'St1': 26, 'PSig': 8, },  # 'Messages':хз пока 	 },       # 'Максимально предельный порог включен',],
    'AHLimEn':    {'CmdOp': 27, 'St1': 27, 'PSig': 9, },  # 'Messages':хз пока 	 },       # 'Максимально аварийный порог включен',],
    'Kvitir':     {'CmdOp': 31, 'St1': 31, 'PSig': 10,},  # 'Messages':хз пока    },      # 'Требуется квитирование',],
}

# Статус слово 1 (Status1)
STATUS1 = {
    'Oos':        1,    # 'Включен режим "Маскирование"',],
    'Imit':       2,    # 'Включен режим "Имитация"',],
    'Fld':        4,    # 'Включен режим "Полевая обработка"',],
    'Tst':        5,    # 'Включен режим "Тестирование"',],
    'Bad':        7,    # 'Недостоверность значения',],
    'ALAct':      8,    # 'Сработала нижняя аварийная уставка (НАУ)',],
    'WLAct':      9,    # 'Сработала нижняя предельная уставка (НПУ)',],
    'TLAct':      10,   # 'Сработала нижняя нормативная уставка (ННУ)',],
    'OutNorm':    11,   # 'Значение в норме',],
    'THAct':      12,   # 'Сработала верхняя нормативная уставка (ВНУ)',],
    'WHAct':      13,   # 'Сработала верхняя предельная уставка (ВПУ)',],
    'AHAct':      14,   # 'Сработала верхняя аварийная уставка (ВАУ)',],
    'SpeedMax':   18,   # 'Скорость изменения параметра максимальна',],
    'SpeedOff':   19,   # 'Расчёт скорости изменения параметра',],
    'MsgOff':     20,   # 'Генерация сообщений отключена',],
    'Filt':       21,   # 'Фильтр',],
    'ALLimEn':    22,   # 'Минимально аварийный порог включен',],
    'WLLimEn':    23,   # 'Минимально предельный порог включен',],
    'TLLimEn':    24,   # 'Минимально нормативный порог включен',],
    'THLimEn':    25,   # 'Максимально нормативный порог включен',],
    'WHLimEn':    26,   # 'Максимально предельный порог включен',],
    'AHLimEn':    27,   # 'Максимально аварийный порог включен',],
    'Kvitir':     31,   # 'Требуется квитирование',],
}

# Текущее состояние	(PanelSig)
PANELSIG = {
    'SpeedMax':  0,	    #  'Скорость изменения параметра максимальна'],
    'SpeedOff':  1,	    #  'Расчёт скорости изменения параметра'],
    'MsgOff':    2,	    #  'Генерация сообщений отключена'],
    'Filt':      3,	    #  'Фильтр'],
    'ALLim':     4,	    #  'Минимально аварийный порог включен'],
    'WLLim':     5,	    #  'Минимально предельный порог включен'],
    'TLLim':     6,	    #  'Минимально нормативный порог включен'],
    'THLim':     7,	    #  'Максимально нормативный порог включен'],
    'WHLim':     8,	    #  'Максимально предельный порог включен'],
    'AHLim':     9,	    #  'Максимально аварийный порог включен'],
    'Kvitir':    10,	#  'Требуется квитирование'],
}

# Режим управления для Панели оператора (PanelMode)
PANELMODE = {
    'None':       0,    # Режим не установлен
    'Oos':        1,    # Режим "Маскирование"',],
    'Imit':       2,    # Режим "Имитация"',],
    'Fld':        4,    # Режим "Полевая обработка"',],
    'Tst':        5,    # Режим "Тестирование"',],
}





# Значения уставок (нижний уровень)
LOWER_LIMIT_VALUE_LOW_LEVEL = 0     # нижний предел измерений
MIN_ALARM_VALUE_LOW_LEVEL = 10      # минимальное аварийное значение
MIN_PREALARM_VALUE_LOW_LEVEL = 20   # минимальное предельное значение
MIN_NORMATIVE_VALUE_LOW_LEVEL = 30  # минимальное нормативное значение
NORMAL_VALUE_LOW_LEVEL = 60         # нормальное значение
MAX_NORMATIVE_VALUE_LOW_LEVEL = 70  # максимальное нормативное значение
MAX_PREALARM_VALUE_LOW_LEVEL = 80   # максимальное предельное значение
MAX_ALARM_VALUE_LOW_LEVEL = 90      # максимальное аварийное значение
UPPER_LIMIT_VALUE_LOW_LEVEL = 100   # верхний предел измерений

# Значения уставок (средний уровень)
LOWER_LIMIT_VALUE_MID_LEVEL = 0     # нижний предел измерений
MIN_ALARM_VALUE_MID_LEVEL = 10      # минимальное аварийное значение
MIN_PREALARM_VALUE_MID_LEVEL = 20   # минимальное предельное значение
MIN_NORMATIVE_VALUE_MID_LEVEL = 30  # минимальное нормативное значение
NORMAL_VALUE_MID_LEVEL = 60         # нормальное значение
MAX_NORMATIVE_VALUE_MID_LEVEL = 70  # максимальное нормативное значение
MAX_PREALARM_VALUE_MID_LEVEL = 80   # максимальное предельное значение
MAX_ALARM_VALUE_MID_LEVEL = 90      # максимальное аварийное значение
UPPER_LIMIT_VALUE_MID_LEVEL = 100   # верхний предел измерений

# Список списков предельных значений, где 0 элемент это регистр, а 1 элемент - значение для записи
LIST_LIMIT_VALUE_MID_LEVEL = [
    [None, LOWER_LIMIT_VALUE_MID_LEVEL],
    [None, MIN_ALARM_VALUE_MID_LEVEL],
    [None, MIN_PREALARM_VALUE_MID_LEVEL],
    [None, MIN_NORMATIVE_VALUE_MID_LEVEL],
    [None, MAX_NORMATIVE_VALUE_MID_LEVEL],
    [None, MAX_PREALARM_VALUE_MID_LEVEL],
    [None, MAX_ALARM_VALUE_MID_LEVEL],
    [None, UPPER_LIMIT_VALUE_MID_LEVEL],
]

VALUES_FOR_LOW_LEVEL = [1, 2, 3, 4, 5]
VALUES_FOR_MID_LEVEL = [40, 45, 50, 55, 60]

# Список регистров для проверки статусов аналогового параметра, начиная с обрыва и заканчивая КЗ.
REGISTERS_FOR_CHECK_STATUS = [None, None, None, None, None, None, None]

# Словарь для проверки статусов аналогового параметра, начиная с обрыва и заканчивая КЗ.
# разобрать какая тут информация будет
STATUS_FOR_CHECK_STATUS = {
    'Обрыв':                             [None, None, None, None, None, None, None, None, None],
    'Минимальное аварийное значение':    [None, None, None, None, None, None, None, None, None],
    'Минимальное предельное значение':   [None, None, None, None, None, None, None, None, None],
    'Минимальное нормативное значение':  [None, None, None, None, None, None, None, None, None],
    'Нормальное значение':               [None, None, None, None, None, None, None, None, None],
    'Максимальное нормативное значение': [None, None, None, None, None, None, None, None, None],
    'Максимальное предельное значение':  [None, None, None, None, None, None, None, None, None],
    'Максимальное аварийное значение':   [None, None, None, None, None, None, None, None, None],
    'КЗ': 0
}
