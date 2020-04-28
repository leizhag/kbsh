from __future__ import print_function, absolute_import, unicode_literals

import logging
import os
import subprocess
import sys

import click
import yaml
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.lexers import PygmentsLexer

from .client import KubernetesClient, kubeconfig_filepath
from .completer import KubectlCompleter, shell_cmd_from_user_input
from .lexer import KubectlLexer
from .style import StyleFactory
from .toolbar import Toolbar
from .utils import switch_context

logger = logging.getLogger(__name__)

inline_help = True
bindings = KeyBindings()
client = KubernetesClient()
api = client.get_core_v1_api()


class KubeConfig(object):
    clustername = user = ""
    namespace = "default"
    current_context_index = 0
    current_context_name = ""
    template_set_namespace = "kubectl config set-context {} --namespace={}"

    @staticmethod
    def parse_kubeconfig():
        if not os.path.exists(os.path.expanduser(kubeconfig_filepath)):
            return ("", "", "")

        with open(os.path.expanduser(kubeconfig_filepath), "r") as fd:
            docs = yaml.safe_load_all(fd)
            for doc in docs:
                current_context = doc.get("current-context", "")
                contexts = doc.get("contexts")
                if contexts:
                    for index, context in enumerate(contexts):
                        if context['name'] == current_context:
                            KubeConfig.current_context_index = index
                            KubeConfig.current_context_name = context['name']
                            if 'cluster' in context['context']:
                                KubeConfig.clustername = context['context']['cluster']
                            if 'namespace' in context['context']:
                                KubeConfig.namespace = context['context']['namespace']
                            if 'user' in context['context']:
                                KubeConfig.user = context['context']['user']
                            return (KubeConfig.clustername, KubeConfig.user, KubeConfig.namespace)
        return ("", "", "")

    @staticmethod
    def parse_contexts():
        if not os.path.exists(os.path.expanduser(kubeconfig_filepath)):
            return

        with open(os.path.expanduser(kubeconfig_filepath), "r") as fd:
            docs = yaml.safe_load_all(fd)
            for doc in docs:
                return doc.get("contexts")

    startup_contexts = [ctx['name'] for ctx in parse_contexts.__func__()]

    @staticmethod
    def switch_to_next_cluster():
        contexts = KubeConfig.parse_contexts()
        if contexts:
            KubeConfig.current_context_index = (KubeConfig.current_context_index + 1) % len(contexts)
            cluster_name = contexts[KubeConfig.current_context_index]['name']
            KubeConfig.switch_context(cluster_name)

    @staticmethod
    def list_namespaces():
        return client.get_resource("namespace")

    @staticmethod
    def list_namespace_names():
        return (ns[0] for ns in client.get_resource("namespace"))

    @staticmethod
    def switch_to_next_namespace(current_namespace):
        namespace_resources = KubeConfig.list_namespaces()
        namespaces = sorted(res[0] for res in namespace_resources)
        index = (namespaces.index(current_namespace) + 1) % len(namespaces)
        next_namespace = namespaces[index]
        KubeConfig.switch_namespace(next_namespace)

    @classmethod
    def switch_context(cls, ctx):
        switch_context(ctx)

    @classmethod
    def switch_namespace(cls, ns):
        kubectl_config_set_namespace = KubeConfig.template_set_namespace.format(KubeConfig.current_context_name, ns)
        cmd_process = subprocess.Popen(kubectl_config_set_namespace, shell=True, stdout=subprocess.PIPE)
        cmd_process.wait()

    # TODO: performance
    @classmethod
    def switch_context_and_namespace(cls, ctx, ns):
        kubectl_config_use_context = "kubectl config use-context " + ctx
        cmd_process = subprocess.Popen(kubectl_config_use_context, shell=True, stdout=subprocess.PIPE)
        cmd_process.wait()
        kubectl_config_set_namespace = KubeConfig.template_set_namespace.format(ctx, ns)
        cmd_process = subprocess.Popen(kubectl_config_set_namespace, shell=True, stdout=subprocess.PIPE)
        cmd_process.wait()


def make_resource_getter(resource):
    return lambda: client.get_resource(resource)


suffix_to_suggestor = {
    '-n': KubeConfig.list_namespace_names,
    '-c': lambda: KubeConfig.startup_contexts,
}

resources = [resource.name for resource in api.get_api_resources().resources]
for resource in resources:
    suffix_to_suggestor[resource] = make_resource_getter(resource)
completer = KubectlCompleter(suffix_to_suggestor)


class Kubeshell(object):
    clustername = user = ""
    namespace = "default"

    @staticmethod
    def get_message():
        prompt_style = 'class:danger' if Kubeshell.clustername == 'prod' else 'class:prompt'
        return [
            (prompt_style, '⎈  k8s:('),
            ('class:state', Kubeshell.clustername),
            (prompt_style, '/'),
            ('class:state', Kubeshell.namespace),
            (prompt_style, ') ⎈  '),
        ]

    def __init__(self, refresh_resources=True):
        shell_dir = os.path.expanduser("~/.kube/shell/")
        self.history = FileHistory(os.path.join(shell_dir, "history"))
        if not os.path.exists(shell_dir):
            os.makedirs(shell_dir)
        self.toolbar = Toolbar(KubeConfig.startup_contexts, KubeConfig.list_namespace_names,
                               self.get_cluster_name, self.get_namespace, self.get_user, self.get_inline_help)

    @bindings.add('c-x')
    def _(event):
        try:
            KubeConfig.switch_to_next_cluster()
            Kubeshell.clustername, Kubeshell.user, Kubeshell.namespace = KubeConfig.parse_kubeconfig()
        except Exception as e:
            logger.warning("failed switching clusters", exc_info=1)

    @bindings.add('c-n')
    def _(event):
        try:
            KubeConfig.switch_to_next_namespace(Kubeshell.namespace)
            Kubeshell.clustername, Kubeshell.user, Kubeshell.namespace = KubeConfig.parse_kubeconfig()
        except Exception as e:
            logger.warning("failed namespace switching", exc_info=1)

    @bindings.add('c-q')
    def _(event):
        global inline_help
        inline_help = not inline_help
        completer.set_inline_help(inline_help)

    def get_cluster_name(self):
        return Kubeshell.clustername

    def get_namespace(self):
        return Kubeshell.namespace

    def get_user(self):
        return Kubeshell.user

    def get_inline_help(self):
        return inline_help

    def update_state(self, user_input):
        ctx = client.get_context(user_input)
        ns = client.get_namespace(user_input)

        if ctx and ctx != Kubeshell.clustername and ns and ns != Kubeshell.namespace:
            KubeConfig.switch_context_and_namespace(ctx, ns)
            return
        if ctx and ctx != Kubeshell.clustername:
            KubeConfig.switch_context(ctx)
            return
        if ns and ns != Kubeshell.namespace:
            KubeConfig.switch_namespace(ns)

    def run_cli(self):

        logger.info("running kube-shell event loop")
        if not os.path.exists(os.path.expanduser(kubeconfig_filepath)):
            click.secho('Kube-shell uses {0} for server side completion. Could not find {0}. '
                        'Server side completion functionality may not work.'.format(kubeconfig_filepath),
                        fg='red', blink=True, bold=True)

        session = PromptSession(history=self.history)

        while True:
            global inline_help
            try:
                Kubeshell.clustername, Kubeshell.user, Kubeshell.namespace = KubeConfig.parse_kubeconfig()
            except:
                logger.error("unable to parse {} %s".format(kubeconfig_filepath), exc_info=1)
            completer.set_namespace(self.namespace)

            try:
                user_input = session.prompt(
                    self.get_message,
                    auto_suggest=AutoSuggestFromHistory(),
                    style=StyleFactory("vim").style,
                    lexer=PygmentsLexer(KubectlLexer),
                    enable_history_search=False,
                    bottom_toolbar=self.toolbar.handler,
                    key_bindings=bindings,
                    completer=completer,
                    complete_in_thread=True
                )
            except (EOFError, KeyboardInterrupt):
                sys.exit()

            if user_input == "clear":
                click.clear()
            elif user_input == "exit":
                sys.exit()

            user_input = shell_cmd_from_user_input(user_input)

            if user_input:
                p = subprocess.Popen(user_input, shell=True)
                try:
                    _, stderr_data = p.communicate()
                    if not stderr_data:
                        self.update_state(user_input)
                except KeyboardInterrupt:
                    print()
