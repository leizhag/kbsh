import shlex
import subprocess


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


def switch_context(ctx):
    kubectl_config_use_context = "kubectl config use-context " + ctx
    cmd_process = subprocess.Popen(kubectl_config_use_context, shell=True, stdout=subprocess.PIPE)
    cmd_process.wait()
