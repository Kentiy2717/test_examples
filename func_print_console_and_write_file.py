from termcolor import cprint

from probably_not_used.constants import DETAIL_REPORT_ON

count_test = 1


def write_to_file(message):
    with open('logs.txt', 'a', encoding='utf-8') as f:
        f.write(message + '\n')


def write_to_file_num(count_test):
    with open('logs.txt', 'a', encoding='utf-8') as f:
        f.write(str(count_test) + ') ')


def print_title(message):
    global count_test
    print('_____________________________________________________\n')
    cprint(f'{count_test})', end=' ', color='grey')
    cprint(message, color='yellow', attrs=['underline'])
    write_to_file_num(count_test)
    count_test += 1
    write_to_file(message)


def print_failed_test(message):
    print('')
    cprint(message, on_color='on_red')
    print('')
    write_to_file(message)


def print_error(message):
    cprint(message, color='red')
    write_to_file(message)


def print_passed(message):
    cprint(message, color='green')
    write_to_file(message)


def print_text_grey(message):
    if DETAIL_REPORT_ON is True:
        cprint(message, color='grey')
        write_to_file(message)


def print_text_grey_start(message):
    cprint(message, color='grey')
    write_to_file(message)


def print_text_white(message):
    cprint(message, color='white')
    write_to_file(message)
