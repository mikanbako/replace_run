# Copyright (c) 2022 Keita Kita
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

import os.path
import subprocess

SCRIPT_DIRECTORY = os.path.dirname(__file__)
TOP_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, '..')
REPLACE_RUN_SCRIPT = os.path.join(TOP_DIRECTORY, 'replace_run/replace_run.py')
RESOURCES_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, 'resources')
ECHO_SCRIPT_PATH = os.path.join(RESOURCES_DIRECTORY, 'echo_script.sh')
ECHO_SCRIPT_WITH_ARGUMENT_PATH = os.path.join(
    RESOURCES_DIRECTORY, 'echo_script_with_argument.sh')


def run(arguments, script_path, script_arguments=[]):
    return subprocess.run(
        [REPLACE_RUN_SCRIPT]
        + arguments
        + ['--', script_path]
        + script_arguments,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True)


def test_replace():
    result = run(['-r', 'replaced line/test'], ECHO_SCRIPT_PATH)

    assert result.returncode == 0
    assert result.stdout == '''\
test
test
test
test
'''


def test_replace_with_group():
    result = run(['-r', r'(\S+ ).+/\1out'], ECHO_SCRIPT_PATH)

    assert result.returncode == 0
    assert result.stdout == '''\
out
out
out
out
'''


def test_no_replace():
    result = run(
        ['-r', 'no_replace/no_replace', 'replaced line/test'],
        ECHO_SCRIPT_PATH)

    assert result.returncode != 0


def test_script_argument():
    echoed_test = 'output'

    result = run(
        ['-r', 'true/echo'], ECHO_SCRIPT_WITH_ARGUMENT_PATH, [echoed_test])

    assert result.returncode == 0
    assert result.stdout == echoed_test + '\n'
