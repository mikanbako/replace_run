#!/usr/bin/env python3

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

import argparse
import os
import os.path
import re
import stat
import subprocess
import sys
import tempfile


class StatementWrongException(Exception):
    def __init__(self, reason):
        self.reason = reason


class NoReplacementException(Exception):
    def __init__(self, index):
        self.index = index


class Replacement:
    def __init__(self, pattern, replacement):
        self.pattern = pattern
        self.replacement = replacement

    @staticmethod
    def _split_statement(statement):
        start_index = statement.rfind('\\/')

        start_index = start_index + 2 if 0 <= start_index else 0

        index = statement.find('/', start_index)

        if index == -1:
            raise StatementWrongException('The delimiter "/" is not found.')

        pattern = statement[:index].replace('\\/', '/')
        replacement = statement[index + 1:]

        return pattern, replacement

    @staticmethod
    def create(statement):
        '''
        Creates a replacement object.

        Parameters:
            statement: The statement that contains a pattern and a replacement.
        Returns:
            A replacement object.
        Raises:
            StatementWrongException: The statement is wrong.
        '''
        pattern_string, replacement_string = Replacement._split_statement(
            statement)

        if len(pattern_string) == 0:
            raise StatementWrongException('The pattern is not found.')

        try:
            pattern = re.compile(pattern_string)
        except re.error as e:
            raise StatementWrongException('The pattern is wrong: ' + e.msg)

        return Replacement(pattern, replacement_string)

    def replace(self, text):
        '''
        Replaces a text.

        Parameters:
            text: The text.
        Returns:
            The replaced text.
        Raises:
            StatementWrongException: The replacement is wrong.
        '''
        try:
            replaced_text, count = self.pattern.subn(self.replacement, text)
        except re.error as e:
            raise StatementWrongException(e.msg)

        return replaced_text if 0 < count else None


def _split_command_line_arguments(argv=None):
    source_arguments = argv if argv is not None else sys.argv[1:]

    script_index = len(source_arguments)

    is_in_replace_option = False

    for index, argument in enumerate(source_arguments):
        if argument == '-r' or argument == '--replace':
            is_in_replace_option = True
        elif argument.startswith('-'):
            is_in_replace_option = False
        elif not is_in_replace_option:
            script_index = index
            break

    return (source_arguments[:script_index + 1],
            source_arguments[script_index + 1:])


def parse_command_line_arguments(argv=None):
    '''
    Parses command line arguments.

    Parameters:
        argv: The command line arguments. None is sys.argv.
    Returns:
        argparse.Namespace with command line argument for this script and
        list with command line arguments for running scripts.
    '''
    parser = argparse.ArgumentParser(
        description='Run a script that replaced by '
        'specified regular expressions.')
    parser.add_argument(
        '-r',
        '--replace',
        nargs='+',
        metavar='STATEMENT',
        dest='statements',
        required=True,
        help='The statements for replacing script. '
        'The format is "<regular expression>/<replacement>". '
        'The escape sequence is "\\" in <regular expression>.')
    parser.add_argument(
        '-o',
        '--output',
        action='store_true',
        help='Oputput the replaced script instead of running it.')
    parser.add_argument('script', help='The path of a script file.')

    script_arguments, running_script_arguments = _split_command_line_arguments(
        argv)

    return parser.parse_args(script_arguments), running_script_arguments


def _create_replacements(all_statements):
    return [Replacement.create(statement) for statement in all_statements]


def _read_text(path):
    with open(path) as file:
        return file.read()


def replace_script(source_text, all_replacements):
    '''
    Replaces a script by replacements.

    Parameters:
        source_text: The text for replacement.
        all_replacements: The iterable object for replacement.
    Returns:
        The replaced text. None when a reprecement does not replace the text.
    Raises:
        StatementWrongException: The replacement is wrong.
        NoReplacementException: A replacement has not replaced the text.
    '''
    text = source_text

    for index, replacement in enumerate(all_replacements):
        text = replacement.replace(text)

        if text is None:
            raise NoReplacementException(index)

    return text


def _create_temporary_script_file(script_source, source_script_path):
    script_directory = os.path.dirname(os.path.abspath(source_script_path))
    script_extension = os.path.splitext(source_script_path)[1]

    try:
        script_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix=script_extension,
            dir=script_directory)
        script_file.write(script_source)
        script_file.flush()

        os.chmod(script_file.name, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        return script_file
    except Exception:
        if script_file:
            script_file.close()

        raise
    finally:
        os.sync()


def _execute(script_source, arguments, source_script_path):
    with _create_temporary_script_file(
            script_source, source_script_path) as script_file:

        result = subprocess.run([script_file.name] + arguments)

        return result.returncode


def main():
    arguments, script_arguments = parse_command_line_arguments()

    try:
        replacements = _create_replacements(arguments.statements)
    except StatementWrongException as e:
        print('{}'.format(e.reason), file=sys.stderr)
        sys.exit(1)

    try:
        script_source = _read_text(arguments.script)
    except IOError as e:
        print('{}'.format(e), file=sys.stderr)
        sys.exit(1)

    try:
        replaced_source = replace_script(script_source, replacements)
    except StatementWrongException as e:
        print('{}'.format(e.reason), file=sys.stderr)
        sys.exit(1)
    except NoReplacementException as e:
        print(
            'Statement "{}" has not replaced the script.'.format(
                arguments.statements[e.index]),
            file=sys.stderr)
        sys.exit(1)

    if arguments.output:
        print(replaced_source)

        sys.exit(0)
    else:
        return_code = _execute(
            replaced_source, script_arguments, arguments.script)

        sys.exit(return_code)


if __name__ == '__main__':
    main()
