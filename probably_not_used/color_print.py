def print_red(text):
    print("\033[31m{}".format(text))


def print_green(text):
    print("\033[32m{}".format(text))


def print_blue(text):
    print("\033[34m{}".format(text))


def print_white(text):
    print("\033[37m{}".format(text))


def print_error(hendler, expected_val, result_val):
    print_red(hendler)
    print_green(expected_val)
    print_red(result_val)
    print_white('')
