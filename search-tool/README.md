# Search tool

## Install dependencies

Python 2.7 required! Not working with Python 3.

```Bash
$ python --version
Python 2.7.11
$ virtualenv venv
$ source venv/bin/activate
$ python --version
Python 2.7.11
$ pip install -r requirements.txt
```

You may need to upgrade setuptools==18.5 before installing planemo.

## Install Galaxy

Galaxy requires Python 2.7, to check your python version, run:

```Bash
$ python -V
Python 2.7.3
```

Install Galaxy release_16.04 (not working with 16.07):

```Bash
$ sh get-galaxy.sh
```

But do not run it.

## Test planemo

```Bash
$ planemo tool_init --id 'hello_world' --name 'Hello World from Planemo'
$ planemo lint
$ planemo test --galaxy_root=/Users/pajon01/workspace/git-galaxy-kickstart/galaxy-dist
Testing complete. HTML report is in "/Users/pajon01/workspace/git-galaxy-kickstart/search-tool/tool_test_output.html".
There were problems with 1 test(s) - out of 1 test(s) executed. See /Users/pajon01/workspace/git-galaxy-kickstart/search-tool/tool_test_output.html for detailed breakdown.
hello_world[0]: failed
$ planemo serve --galaxy_root=/Users/pajon01/workspace/git-galaxy-kickstart/galaxy-dist
```

Check at http://127.0.0.1:9090
