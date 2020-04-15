import shlex


def get_shell_option_value(cmd, *options):
    found = False
    for token in shlex.split(cmd):
        if found:
            return token
        if token in '<|>':
            return
        if token in options:
            found = True
