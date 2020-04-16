import shlex


def get_shell_option_value(cmd, *options):
    found = False
    try:
        tokens = shlex.split(cmd)
    except ValueError:
        return
    for token in tokens:
        if found:
            return token
        if token in '<|>':
            return
        if token in options:
            found = True
