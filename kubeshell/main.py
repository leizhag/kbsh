#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import print_function, absolute_import, unicode_literals

import argparse

from app import Kubeshell, KubeConfig

import logging
logger = logging.getLogger(__name__)


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--context', help='The context name to use '
                                                'when starting the kube-shell.')
    args = parser.parse_args()
    if args.context:
        KubeConfig.switch_context(args.context)

    kube_shell= Kubeshell()
    logger.info("session start")
    kube_shell.run_cli()

if __name__ == "__main__":
    cli()
