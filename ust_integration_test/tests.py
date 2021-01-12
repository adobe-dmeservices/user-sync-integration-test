import logging
import os
import re
import sys

from ust_integration_test import init_logger
from ust_integration_test.test_sync import TestSync

init_logger(logging.DEBUG)
logger = logging.getLogger()
root_dir = os.getcwd()


def run_test(test_name, test_dir):
    try:
        test = TestSync(test_name, str(test_dir))
        test.run_test()
    finally:
        os.chdir(root_dir)


def delete_users(tmpdir):
    run_test('setup.delete_all_users', tmpdir)


def reset_sign_users(tmpdir):
    logger.info("Reset sign users")
    run_test('setup.reset_sign_users', tmpdir)


def test_manual(tmpdir):
    # delete_users(tmpdir)
    reset_sign_users(tmpdir)


class TestUST(object):

    def test_create_all_users(self, tmpdir):
        run_test(get_test_name(), tmpdir)

    def test_sign_case_1(self, tmpdir):
        reset_sign_users(tmpdir)
        run_test(get_test_name(), tmpdir)


# noinspection PyProtectedMember,PyUnresolvedReferences
def get_test_name():
    return re.sub('^test_', '', sys._getframe(1).f_code.co_name)
