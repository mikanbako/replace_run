# replace_run
A script to execute another script that replaced parts of it.

## Requires

Python >= 3.5

## Install

Copy replace_run/replace_run.py to a directory that contained PATH.

## Example

Replaces "abc" with "def" in echo.sh.

```
$ printf '#!/bin/bash\necho abc\n' > echo.sh
$ replace_run.py -r 'abc/def' -- echo.sh
```

Output:

```
def
```

## Usage

Specify replacements with "X/Y" format. X is a replaced text and Y is a replacement. X and Y can use [regular expression](https://docs.python.org/3.5/library/re.html).

Run replace_run.py with --help option to show the help message.

## License

The MIT License. See LICENSE.txt.

## For developers

Using [asdf](https://asdf-vm.com/) is recommended to use tools for this project.

Install clikit after tools are installed (See "[Poetry does not work on Python 3.5.2](https://github.com/python-poetry/poetry/issues/1744)"):

```
$ python3 -m pip install clikit
```

Install dependencies:

```
$ poetry install
```

Runs unit tests:

```
$ poetry run pytest
```