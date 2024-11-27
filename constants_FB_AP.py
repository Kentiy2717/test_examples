# Константы для test_fb_ap
HYSTERESIS_MID_LEVEL = 1                      # гистерезис
HYSTERESIS_LOW_LEVEL = None         # гистерезис для записи на нижний уровень

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

VALUES_FOR_LOW_LEVEL = [None, None, None, None, None]
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
