

verbosity = "[v]"
error = "[x]"
info = "[i]"
warning = "[!]"

def print_marker(message: str, marker: str) -> None:
    """
    Функция print_marker выводит каждую строчку в сообщении message с определенным маркером

    :param message: сообщение, которое необходимо вывести
    :type message: str
    :param marker: маркер
    :type marker: str
    """
    result = list()
    for s in message.split('\n'):
        result.append(f"{marker}: {s}")
    print('\n'.join(result) + '\n')
    return

print_verbose = lambda message: print_marker(message, verbosity)
print_error = lambda message: print_marker(message, error)
print_info = lambda message: print_marker(message, info)
print_warning = lambda message: print_marker(message, warning)