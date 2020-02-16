from __future__ import print_function, absolute_import, unicode_literals
from pygments.token import Token
from pygments.token import Keyword, Name, Operator, Generic, Literal, Text

class Toolbar(object):
    """Show information about the aws-shell in a tool bar.

    :type handler: callable
    :param handler: Wraps the callable `get_toolbar_items`.

    """

    def __init__(self, get_cluster_name, get_namespace, get_user, get_inline_help):
        self.handler = self._create_toolbar_handler(get_cluster_name, get_namespace, get_user, get_inline_help)

    def _create_toolbar_handler(self, get_cluster_name, get_namespace, get_user, get_inline_help):
        def get_toolbar_items(_):
            if get_inline_help():
                help_token = Token.Toolbar.On
                help = "ON"
            else:
                help_token = Token.Toolbar.Off
                help = "OFF"

            return [
                (Keyword, ' [C-X] Context: '),
                (Token.Toolbar, get_cluster_name()),
                (Keyword, ' [C-N] Namespace: '),
                (Token.Toolbar, get_namespace()),
                (Keyword, ' User: '),
                (Token.Toolbar, get_user()),
                (Keyword, ' [C-H] In-line help: '),
                (help_token, '{0}'.format(help)),
                (Keyword, ' [C-C] Exit ')
            ]

        return get_toolbar_items
