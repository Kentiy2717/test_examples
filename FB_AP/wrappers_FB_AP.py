from common.constants import START_LIMIT, START_LIMIT_VALUE
from common.func_print_console_and_write_file import print_error
from FB_AP.constants_FB_AP import START_VALUE


def reset_initial_values(func):
    def wrapper(*args, **kwargs):
        from common.common_read_and_write_functions import this_is_write_error
        from FB_AP.assist_function_FB_AP import switch_position
        for name, reg_and_val in START_VALUE.items():
            if this_is_write_error(address=reg_and_val['register'], value=reg_and_val['pre_values']) is True:
                print_error(f'Ошибка записи предварительного значения на ножку {name}')
            if this_is_write_error(address=reg_and_val['register'], value=reg_and_val['start_value']) is True:
                print_error(f'Ошибка записи стартового значения на ножку {name}')

            # Если перзаписываем ножки из списка, то необходимо записать сначала False, True, False.
            # Это связано с особенностями перезаписи этих ножек после ребута ПЛК.
            if name in ['ALLimEn', 'WLLimEn', 'TLLimEn', 'THLimEn', 'WHLimEn', 'AHLimEn']:
                this_is_write_error(address=reg_and_val['register'], value=True)
                this_is_write_error(address=reg_and_val['register'], value=False)
        switch_position(command='MsgOff', required_bool_value=False)
        switch_position(command='SpeedOff', required_bool_value=False)
        result = func(*args, **kwargs)
        return result
    return wrapper


def start_with_limits_values(func):
    def wrapper(*args, **kwargs):
        from common.common_read_and_write_functions import this_is_write_error
        if START_LIMIT is True:
            for name, reg_and_val in START_VALUE.items():
                if this_is_write_error(address=reg_and_val['register'], value=START_LIMIT_VALUE) is True:
                    print_error(f'Ошибка записи на ножку {name}')
        result = func(*args, **kwargs)
        return result
    return wrapper
