from func_print_console_and_write_file import print_error
from constants_FB_DP import START_VALUE, SWITCH
from read_and_write_functions_FB_DPcc import write_CmdOp


def reset_initial_values(func):
    def wrapper(*args, **kwargs):
        from common_read_and_write_functions import this_is_write_error
        from assist_function_FB_DP import switch_position
        for name, reg_and_val in START_VALUE.items():
            if this_is_write_error(address=reg_and_val['register'], value=reg_and_val['start_value']) is True:
                print_error(f'Ошибка записи на ножку {name}')
        for command in SWITCH:
            switch_position(command=command, required_bool_value=False)
        write_CmdOp(command='Kvitir')
        result = func(*args, **kwargs)
        return result
    return wrapper
