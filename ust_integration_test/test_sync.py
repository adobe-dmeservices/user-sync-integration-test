import logging
import os
import re
from distutils.dir_util import copy_tree
from os.path import join
from subprocess import Popen, PIPE, STDOUT

import yaml
from pytest import fail

from ust_integration_test.resources import get_resource
from ust_integration_test.test_config import get_test_dir
from ust_integration_test.utils import normalize_text


class TestSync():

    def __init__(self, name, test_dir):
        self.config, self.source_dir = self.load_test_env(name)
        self.test_dir = test_dir
        self.test_name = name
        self.logger = logging.getLogger(name)
        self.sync_results = []
        self.check_results = self.config['check_results'] is True
        self.sync_args = self.config.get('sync_args', '')
        self.setup_commands = self.config.get('setup_commands', [])
        self.assertions = self.config.get('assertions', '').splitlines()
        self.root_config = self.config.get('root_config')
        self.fail_on_error = bool(self.config.get('fail_on_error', True))
        self.allowed_errors = self.config.get('allowed_errors') or []
        self.always_allowed_errors = self.config.get('always_allowed_errors') or []
        self.exe_name = self.config.get('exe_name', 'user-sync')
        # self.exe_name = self.exe_name.rstrip(".exe")

    def load_test_env(self, name):
        directory = get_test_dir(name)
        with open(get_resource("test_defaults.yml")) as f:
            cfg = yaml.safe_load(f)
        with open(join(directory, 'test.yml'), 'r') as f:
            cfg.update(yaml.safe_load(f)), directory
        return cfg, directory

    def exec_shell(self, command, shell=False):
        p = Popen(command.split(" "), stdout=PIPE, stdin=PIPE, stderr=STDOUT, shell=shell)
        for line in iter(p.stdout.readline, b''):
            line = normalize_text(line)
            self.logger.info(line)
            self.sync_results.append(line)

    def run_test(self):
        self.log_start()
        self.setup()
        self.sync()
        if not self.check_results:
            self.logger.info("Sync complete (results not checked)")
            return
        try:
            self.validate_results()
            self.logger.info("Test assertions succesfully verified")
        except TestFailedException as e:
            self.logger.error("Test failed due to: {}".format(e))
            fail(str(e))

    def setup(self):

        # prepare test directory
        self.logger.info("Beginning sync setup")
        copy_tree(self.source_dir, self.test_dir)
        copy_tree(get_resource("shared_test_files"), self.test_dir)

        # Use CHDIR intentionally so the UST can resolve relative paths for CSV, etc
        # Absolute paths preferred, but this will not work in every case without updating config for test dir
        os.chdir(self.test_dir)

        # Arbitrary cli commands needed before sync
        for c in self.setup_commands:
            self.exec_shell(c, True)

    def sync(self):
        self.logger.info("Beginning sync")
        command = "./{0} {1}".format(self.exe_name, self.sync_args)
        self.exec_shell(command)

    def validate_results(self):
        """
        Check for for actual sync errors, and verify that our asserted lines are present in sync.
        :return:
        """

        for i, l in enumerate(self.sync_results):
            l = l.strip()
            for a in self.assertions:
                if a.startswith('REGEX:'):
                    if re.search(a[6:].strip(), l, flags=re.IGNORECASE):
                        self.assertions.remove(a)
                elif normalize_text(a) in l:
                    self.assertions.remove(a)

            if self.fail_on_error:
                if re.search('(ERROR)|(CRITICAL)|(EXCEPTION)|(WARNING)', l, flags=re.IGNORECASE):
                    if not True in {normalize_text(s) in normalize_text(l) for s in self.allowed_errors}:
                        raise TestFailedException("Encountered a non-ignored error: {}".format(l))

        if self.assertions:
            raise TestFailedException("Assertions not found in results: {}".format(self.assertions))

    def log_start(self):
        self.logger.info(
            "\n========================== Begin test: [{}] ==========================".format(self.test_name))
        self.logger.info("Using: " + os.path.abspath(self.root_config))
        self.logger.info("CLI args: " + self.sync_args)
        self.logger.info("Assertions: \n" + "\n".join(self.assertions))


class TestFailedException(Exception):
    pass
