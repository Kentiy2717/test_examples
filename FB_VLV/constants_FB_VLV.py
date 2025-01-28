# Константы для test_FB_VLV

START_VALUE = {
    'Tls':         {'register': 11000, 'pre_values': 5, 'start_value': 2},
    'Tmp':         {'register': 11001, 'pre_values': 180, 'start_value': 10},
    'Terr':        {'register': 11002, 'pre_values': 2, 'start_value': 1},
    'Tpulse':      {'register': 11003, 'pre_values': 2, 'start_value': 1},
    'CmdOp':       {'register': 11800, 'pre_values': 0, 'start_value': 3},
    'Delta':       {'register': 40508, 'pre_values': 1.0, 'start_value': 2.0},
    'SetPos':      {'register': 12800, 'pre_values': 1.0, 'start_value': 0.0},
    'AutSet':      {'register': 40510, 'pre_values': 1.0, 'start_value': 0.0},
    'InPos':       {'register': 40512, 'pre_values': 1.0, 'start_value': 0.0},
    'RLControl':   {'register': 40123, 'pre_values': True, 'start_value': False},
    'RLKey':       {'register': 40124, 'pre_values': True, 'start_value': False},
    'LocalClose':  {'register': 40125, 'pre_values': False, 'start_value': True},
    'LocalOpen':   {'register': 40126, 'pre_values': True, 'start_value': False},
    'LocalStop':   {'register': 40127, 'pre_values': True, 'start_value': False},
    'AutClose':    {'register': 40128, 'pre_values': False, 'start_value': True},
    'AutOpen':     {'register': 40129, 'pre_values': True, 'start_value': False},
    'FbkClose':    {'register': 40130, 'pre_values': False, 'start_value': True},
    'FbkOpen':     {'register': 40131, 'pre_values': True, 'start_value': False},
    'FbkClosing':  {'register': 40132, 'pre_values': True, 'start_value': False},
    'FbkOpening':  {'register': 40133, 'pre_values': True, 'start_value': False},
    'FbkMoving':   {'register': 40134, 'pre_values': True, 'start_value': False},
    'Fault':       {'register': 40135, 'pre_values': True, 'start_value': False},
    'ModDI_FLT':   {'register': 40136, 'pre_values': True, 'start_value': False},
    'ModDO_FLT':   {'register': 40137, 'pre_values': True, 'start_value': False},
    'CCOpen':      {'register': 40138, 'pre_values': True, 'start_value': False},
    'CCClose':     {'register': 40139, 'pre_values': True, 'start_value': False},
    'CCStop':      {'register': 40140, 'pre_values': True, 'start_value': False},
    'ExtFlt':      {'register': 40141, 'pre_values': True, 'start_value': False},
    'VolCtrl':     {'register': 40142, 'pre_values': True, 'start_value': False},
    'Permission':  {'register': 40143, 'pre_values': True, 'start_value': False},
    'InterlockO':  {'register': 40144, 'pre_values': True, 'start_value': False},
    'InterlockC':  {'register': 40145, 'pre_values': True, 'start_value': False},
    'Protect':     {'register': 40146, 'pre_values': True, 'start_value': False},
    'SafeOn':      {'register': 40147, 'pre_values': True, 'start_value': False},
    'SafePos':     {'register': 40148, 'pre_values': True, 'start_value': False},
    'PosFbk':      {'register': 40149, 'pre_values': True, 'start_value': False},
    'OffUnState':  {'register': 40150, 'pre_values': True, 'start_value': False},
    'Fbking':      {'register': 40151, 'pre_values': True, 'start_value': False},
}

WORK_MODES = ('Oos', 'Auto', 'Local', 'Man', 'Imt',)
CMDOP_REGISTER = START_VALUE['CmdOp']['register']
#SWITCH = ('MsgOff', 'WHLimEn', 'AHLimEn')
P_CLOSE_REGISTER = 40031
P_OPEN_REGISTER = 40032
P_STOP_REGISTER = 40033
CTRL_REGISTER = 40034
STATUS1_REGISTER = 10200
STATUS2_REGISTER = 10202
OUT_REGISTER = 40514
VU_SET_POS = 12002
VU_POS = 12000
BAD_REGISTER = 40035
OOS_REGISTER = 40036
LOCAL_REGISTER = 40037
IMT_REGISTER = 40038
AUTO_REGISTER = 40039
MAN_REGISTER = 40040
OPEN_REGISTER = 40041
OPENING_REGISTER = 40042
CLOSE_REGISTR = 40043
CLOSING_REGISTR = 40044
MOVING_REGISTER = 40045
PANEL_MODE_REGISTER = 25074
PANEL_STATE_REGISTER = 25075
PANEL_ALM_REGISTER = 25076
PANEL_SIG_REGISTER = 25077

# Команды управления (CmdOp)
CMDOP = {
    'Oos':          1,    # Установить режим "Ремонт"
    'Imt':          2,    # Установить режим "Имитация"
    'Local':        3,    # Установить режим "Местный"
    'Auto':         4,    # Установить режим "Авто"
    'Man':          5,    # Установить режим "Дистанционный"
    'Unlock':       7,    # Деблокировать
    'Open':         8,    # Открыть арматуру
    'Close':        9,    # Закрыть арматуру
    'Pos':          12,   # Включить/Отключить положение от оператора
    'Stop':         17,   # Остановить арматуру
    'MsgOff':       20,   # Включить/Отключить Генерацию сообщений
    'MskPerm':      27,   # Включить/Отключить Маска на Запрет управления
    'MskInter':     28,	  # Включить/Отключить Маска на Блокировку
    'MskProtect':   29,	  # Включить/Отключить Маска на Защиту
    'Kvitir':       31,   # Квитировать
    'KvitirNoMsg':  100,  # Квитировать без сообщения
}

# Статус слово 1 (Status1)
STATUS1 = {
    'Oos':          1,    # Установить режим "Ремонт"
    'Imt':          2,    # Установить режим "Имитация"
    'Local':        3,    # Установить режим "Местный"
    'Auto':         4,    # Установить режим "Авто"
    'Man':          5,    # Установить режим "Дистанционный"
    'DP_Oos':       6,    # Состояние "Ремонт"
    'Bad':          7,    # Авария
    'Open':         8,    # Открыта
    'Close':        9,    # Закрыта
    'Opening':      10,   # Открывается
    'Closing':      11,   # Закрывается
    'Pos':          12,   # Ручное управление положением
    'RDYOpen':      13,   # Готов к открытию
    'RDYClose':     14,   # Готов к закрытию
    'RDYStop':      15,   # Готов к останову
    'Middle':       16,   # В промежутке
    'Move':         17,   # Арматура в движении
    'FbkOpen':      18,   # Концевик Открыто
    'FbkClose':     19,   # Концевик Закрыто
    'MsgOff':       20,   # Генерация сообщений отключена
    'MskPerm':      27,   # Включить/Отключить Маска на Запрет управления
    'MskInter':     28,	  # Включить/Отключить Маска на Блокировку
    'MskProject':   29,	  # Включить/Отключить Маска на Защиту
    'Kvitir':       31,   # Квитировать
}

STATUS2 = {           # !!!! ОДИНАКОВО С PanelAlm !!!!!
    'ModDIFlt':    0,  # Неисправность модуля дискретного ввода
    'ModDOFlt':    1,  # Неисправность модуля дискретного вывода
    'Fault':       2,  # Авария привода
    'ExtFlt':      3,  # Внешняя ошибка
    'Perm':        4,  # Наличие запрета на управление
    'InterO':      5,  # Сработала блокировка на открытие
    'Protect':     6,  # Наличие защиты
    'UnState':     7,  # Несанкционированное изменение состояния
    'CmdFlt':      8,  # Невыполнение команды управления
    'VolCtrl':     9,  # Отсутсвует напряжение
    'CCOpen':      10,  # Неисправность цепей открытия
    'CCClose':     11,  # Неисправность цепей закрытия
    'CCStop':      12,  # Неисправность цепей останова
    'NoMove':      13,  # Нет движения после команды
    'InterC':      14,  # Наличие блокировки на закрытие
    'Undef':       15,  # Неопределенное состояние
    'BadMoving':   16,  # Неопределенное Движение
}

# VALUE_UNRELIABILITY = {
#     'ChFlt':      'Неисправность канала',
#     'ModFlt':     'Неисправность модуля',
#     'SensFlt':    'Неисправность датчика',
#     'ExtFlt':     'Внешняя ошибка',
#     'HightErr':   'Выход за верхнюю границу измерения',
#     'LowErr':     'Выход за нижнюю границу измерения',
# }

# Режим управления для Панели оператора (PanelMode)
PANELMODE = {
    'None':       0,    # Режим не установлен
    'Oos':        1,    # Режим "Ремонт"
    'Local':      2,    # Режим "Местный"
    'Man':        3,    # Режим "Дистанция"
    'Auto':       4,    # Режим "Автомат"
}

# Текущее состояние	(PanelState)
PANELSTATE = {
    'None':      0,	    # Состояние не установлено
    'Oos':       1,	    # Состояние ремонт
    'Close':     2,	    # Закрыта
    'Open':      3,     # Открыта
    'Opening':   4,     # Открывается
    'Closing':   5,	    # Закрывается
    'Middle':    6,	    # Промежуток
}

PANEL_ALM = {
    'Bad':        0,	    # Общая авария
    'ModDIFlt':   1,	    # Неисправность модуля дискретного ввода
    'ModDOFlt':   11,	    # Неисправность модуля дискретного вывода
    'Fault':      2,	    # Авария привода
    'ExtFlt':     3,	    # Внешняя ошибка
    'UnState':    4,	    # Несанкционированное изменение состояния
    'NoMove':     5,	    # Нет движения после команды
    'CmdFlt':     6,	    # Невыполнение команды управления
    'Undef':      7,	    # Неопределенное состояние
    'Protect':    8,	    # Наличие защиты
    'CC':         9,	    # Неисправность цепей
    'VolCtrl':    10,	    # Отсутствует напряжение
    'BadMoving':  12,	    # Неопределенное движение
}

# Текущее состояние	(PanelSig)
PANELSIG = {
    'Imit':        0,	    # Имитация
    'Moving':      1,	    # В движении
    'Pos':         2,	    # Ручное управление положением
    'RDYOpen':     3,	    # Готовность к открытию
    'RDYClose':    4,	    # Готовность к закрытию
    'RDYStop':     5,	    # Готовность к останову
    'FbkOpen':     6,	    # Концевик открыто
    'FbkClose':    7,	    # Концевик закрыто
    'MsgOff':      8,	    # Сообщения отключены
    'MskPerm':     9,	    # Маска на запрет управления
    'MskInter':    10,	    # Маска на блокировку управления
    'MskProtect':  11,	    # Маска на защиту
    'Permission':  12,	    # Запрет управления
    'InterO':      13,	    # Блокировка открытия
    'InterC':      14,	    # Блокировка закрытия
}
