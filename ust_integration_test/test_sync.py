import logging
import os
import re
import shutil
from distutils.dir_util import copy_tree
from os.path import join
from subprocess import Popen, PIPE, STDOUT

import yaml
from pytest import fail

from ust_integration_test.resources import get_ust_exe
from ust_integration_test.utils import load_test_defaults, get_test_config, normalize_text


class TestSync():
    test_defaults = load_test_defaults()

    def __init__(self, name, test_dir):
        test_defaults, self.source_dir = get_test_config(name)
        self.test_dir = test_dir
        self.test_name = name
        self.logger = logging.getLogger()
        self.sync_logger = logging.getLogger("test")
        self.sync_results = []

        self.config = self.test_defaults['parameters']
        self.config.update(test_defaults)
        self.check_results = self.config['check_results'] is True
        self.sync_args = self.config.get('sync_args', '')
        self.setup_commands = self.config.get('setup_commands', [])
        self.assertions = self.config.get('assertions', '').splitlines()
        self.root_config = self.config.get('root_config')
        self.fail_on_error = bool(self.config.get('fail_on_error', True))
        self.allowed_errors = self.config.get('allowed_errors') or []
        self.allowed_errors.extend(self.config.get('always_allowed_errors') or [])

    def exec_shell(self, command, shell=False):
        p = Popen(command.split(" "), stdout=PIPE, stdin=PIPE, stderr=STDOUT, shell=shell)
        for line in iter(p.stdout.readline, b''):
            line = normalize_text(line)
            self.sync_logger.info(line)
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

        self.logger.info("Beginning sync setup")
        # prepare test directory
        copy_tree(self.source_dir, self.test_dir)
        shutil.copy(get_ust_exe(), join(self.test_dir, 'ust'))

        # Use CHDIR intentionally so the UST can resolve relative paths for CSV, etc
        # Absolute paths preferred, but this will not work in every case without updating config for test dir
        os.chdir(self.test_dir)

        if os.path.exists('connector-umapi.yml'):
            with open('connector-umapi.yml', 'r') as f:
                umapi = yaml.safe_load(f)
                umapi.update(self.test_defaults['umapi_connection_data'])
            with open('connector-umapi.yml', 'w') as f:
                yaml.safe_dump(umapi, f)

        for c in self.setup_commands:
            self.exec_shell(c, True)

    def sync(self):
        self.logger.info("Beginning sync")
        command = "./ust -c {0} {1}".format(self.root_config, self.sync_args)
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
