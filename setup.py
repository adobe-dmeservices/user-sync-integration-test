# Copyright (c) 2020 Adobe Inc.  All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import os

from setuptools import setup, find_packages

version_namespace = {}
with open('ust_integration_test/version.py') as f:
    exec(f.read(), version_namespace)

with open("README.md", "r") as fh:
    long_description = fh.read()


def package_files(*dirs):
    paths = []
    for d in dirs:
        for (path, directories, filenames) in os.walk(d):
            for filename in filenames:
                paths.append(os.path.join('..', path, filename))
    return paths


extra_files = package_files('spypi/resources')

test_deps = ['mock', 'pytest']
setup_deps = ['wheel']

setup(name='ust-integration-test',
      version=version_namespace['__version__'],
      long_description=long_description,
      long_description_content_type="text/markdown",
      classifiers=[],
      description='Integration testing against live console',
      url='https://github.com/adobe-dmeservices/user-sync-integration-test',
      maintainer='Danimae Vossen',
      maintainer_email='per38285@adobe.com',
      license='MIT',
      packages=find_packages(),
      package_data={
          'ust_integration_test': extra_files,
      },
      install_requires=[
          'PyYAML',
          'Click',
          'click_default_group'
      ],
      extras_require={
          'test': test_deps,
          'setup': setup_deps,
      },
      setup_requires=setup_deps,
      tests_require=test_deps,
      entry_points={
          'console_scripts': [
              'ust_integration_test = ust_integration_test.app:main'
          ]
      },
      )
