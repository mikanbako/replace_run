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

from replace_run import replace_run

import pytest


class TestCommandLineParser:
    def test_script_only(self):
        script = 'script.sh'
        arguments, script_arguments = replace_run.parse_command_line_arguments(
            ['-r', 'a/b', '--', script])

        assert arguments.script == script
        assert len(script_arguments) == 0

    def test_script_arguments(self):
        expected_script_arguments = ['-a', '--bc', 'def']
        _, script_arguments = replace_run.parse_command_line_arguments(
            ['-r', 'a/b', '--', 'scripts.sh'] + expected_script_arguments)

        assert expected_script_arguments == script_arguments

    def test_all_arguments(self):
        script = 'script.sh'
        expected_script_arguments = ['-a', '--bc', 'def']
        arguments, script_arguments = replace_run.parse_command_line_arguments(
            ['-r', 'a', 'b', '--output', script] + expected_script_arguments)

        assert arguments.output
        assert len(arguments.statements) == 2
        assert arguments.script == script
        assert expected_script_arguments == script_arguments

    def test_all_arguments_with_delimiter(self):
        script = 'script.sh'
        expected_script_arguments = ['-a', '--bc', 'def']
        arguments, script_arguments = replace_run.parse_command_line_arguments(
            ['-r', 'a', 'b', '--output', '--', script]
            + expected_script_arguments)

        assert arguments.output
        assert len(arguments.statements) == 2
        assert arguments.script == script
        assert expected_script_arguments == script_arguments


class TestReplacement:
    def test_create(self):
        replacement = replace_run.Replacement.create('a/b')

        assert 'bbb' == replacement.replace('aba')

    def test_create_with_escape_sequence(self):
        replacement = replace_run.Replacement.create('\\//\\\\')

        assert '\\' == replacement.replace('/')

    def test_create_with_wrong_statement(self):
        with pytest.raises(replace_run.StatementWrongException):
            replace_run.Replacement.create('a')

    def test_create_with_wrong_pattern(self):
        with pytest.raises(replace_run.StatementWrongException):
            replace_run.Replacement.create('[/a')

    def test_create_without_pattern(self):
        with pytest.raises(replace_run.StatementWrongException):
            replace_run.Replacement.create('/a')

    def test_replace(self):
        replacement = replace_run.Replacement.create(r'(\d+)/-\1')

        assert 'a-123' == replacement.replace('a123')

    def test_replace_with_wrong_replacement(self):
        replacement = replace_run.Replacement.create('abc/\\')

        with pytest.raises(replace_run.StatementWrongException):
            replacement.replace('abc')

    def test_replace_without_replacement(self):
        replacement = replace_run.Replacement.create('abc/a')

        assert replacement.replace('123') is None


class TestReplaceScript:
    def test_replace(self):
        replacements = [
            replace_run.Replacement.create('a/b'),
            replace_run.Replacement.create('1/2')]

        expected_text = '''
        bc
        23
        b
        '''

        text = '''
        ac
        13
        b
        '''

        assert expected_text == replace_run.replace_script(text, replacements)

    def test_no_replace(self):
        replacements = [
            replace_run.Replacement.create('5/6'),
            replace_run.Replacement.create('a/b'),
            replace_run.Replacement.create('1/2')]

        with pytest.raises(replace_run.NoReplacementException) as exc_info:
            replace_run.replace_script('5', replacements)

        assert exc_info.value.index == 1

    def test_replace_with_wrong_replacement(self):
        replacements = [replace_run.Replacement.create('a/\\')]

        with pytest.raises(replace_run.StatementWrongException):
            replace_run.replace_script('aaa', replacements)
