from __future__ import absolute_import, unicode_literals, print_function

import json
import logging
import os
import os.path
import shlex

from fuzzyfinder import fuzzyfinder
from prompt_toolkit.completion import Completer, Completion

from .client import KubernetesClient
from .parser import Parser
from .utils import get_shell_option_value

logger = logging.getLogger(__name__)

# TODO: configurable
user_input_prefix_to_shell_cmd_prefix = {
    'g ': 'get ',
    'd ': 'describe ',
    'e ': 'exec -it ',
    'l ': 'logs ',
    'lt ': 'logs --tail ',
    'ld ': 'logs deploy/',
}

user_input_part_to_shell_cmd_part = {
    ' -t ': ' --tail ',
    ' -c ': ' --context ',
    ' --sort-by-age': ' --sort-by="{.metadata.creationTimestamp}"',
}

formats_to_highlight = {'yaml', 'json'}


def highlight(cmd, format):
    return cmd + '| pygmentize -l ' + format


def shell_cmd_from_user_input(user_input):
    if user_input.startswith('!'):
        return user_input[1:]

    for user_input_prefix, shell_cmd_prefix in user_input_prefix_to_shell_cmd_prefix.items():
        if user_input.startswith(user_input_prefix):
            user_input = user_input.replace(user_input_prefix, shell_cmd_prefix, 1)
            break

    for user_input_part, shell_cmd_part in user_input_part_to_shell_cmd_part.items():
        user_input = user_input.replace(user_input_part, shell_cmd_part, 1)

    output_format = get_shell_option_value(user_input, '-o', '--output')
    if output_format in formats_to_highlight:
        user_input = highlight(user_input, output_format)

    return "kubectl " + user_input


class KubectlCompleter(Completer):

    def __init__(self, suffix_to_suggestor=None):
        if suffix_to_suggestor is None:
            suffix_to_suggestor = {}
        self.end_to_suggestor = suffix_to_suggestor
        self.inline_help = True
        self.namespace = ""
        self.kube_client = KubernetesClient()

        try:
            DATA_DIR = os.path.dirname(os.path.realpath(__file__))
            DATA_PATH = os.path.join(DATA_DIR, 'data/cli.json')
            with open(DATA_PATH) as json_file:
                self.kubectl_dict = json.load(json_file)
            self.parser = Parser(DATA_PATH)
        except Exception as ex:
            logger.error("got an exception" + ex.message)

    def set_inline_help(self, val):
        self.inline_help = val

    def set_namespace(self, namespace):
        self.namespace = namespace

    def get_completions(self, document, complete_event, smart_completion=None):
        word_before_cursor = document.get_word_before_cursor(WORD=True)

        cmdline = shell_cmd_from_user_input(document.text_before_cursor.strip())
        try:
            tokens = shlex.split(cmdline)

            for suffix, suggestor in self.end_to_suggestor.items():
                if (tokens and not word_before_cursor and tokens[-1] == suffix
                        or len(tokens) > 1 and tokens[-2] == suffix):
                    for key in fuzzyfinder(word_before_cursor, suggestor()):
                        yield Completion(key, -len(word_before_cursor), display=key)
                    return

            _, _, suggestions = self.parser.parse_tokens(tokens)
            valid_keys = fuzzyfinder(word_before_cursor, suggestions.keys())
            for key in valid_keys:
                yield Completion(key, -len(word_before_cursor), display=key, display_meta=suggestions[key])
        except ValueError:
            pass
