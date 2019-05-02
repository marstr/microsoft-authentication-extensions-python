## Setting up your Dev Environment

### Programs to Install

#### Required:
- [Python](https://www.python.org/downloads/)
- [Git](https://git-scm.com)
- Text Editor/IDE of your choice, capable of modifying Python source code. [VSCode](https://code.visualstudio.com)
 and [PyCharm](https://www.jetbrains.com/pycharm) are two popular options.

#### Optional:
- [Docker](https://www.docker.com/get-started)

### Acquiring Source:

From your command-line of choice, navigate to the directory you would like to contain this code. Then execute the
following:

``` bash
git clone https://github.com/marstr/microsoft-authentication-extensions-for-python.git
```

### Creating a Virtual Environment
Once you've cloned this source, you can create an isolated environment to debug and test this library using the module,
`virtualenv`. To do so, navigate to the root directory of this project on your local machine, in the command line
environment of your choice. Then execute:

``` bash
python -m virtualenv venv/
```

This will have created an isolated set of python modules that will be used to execute your tests, and do your debugging.
To finish initializing this environment, you'll need to activate it by running one of the following from the root of
this project:

_Unix-Like:_
``` bash
source ./venv/scripts/activate
pip install -e ".[dev]"
```

_PowerShell:_
``` PowerShell
.\venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```


## Running Tests
Once you have an activated and initialized virtual environment from the step above, testing is as simple as running the
command `pytest`.

#### Using Docker to Test

> NOTE: Docker cannot test the Windows or MacOS specific code in this library.

Creating multiple virtual environments to test Python2 and Python3 can be a pain. `Dockerfile.test` is provided to
simplify the process of testing against a version of Python you do not have installed locally.

To get started just run the following from the root directory of this project:
``` bash
docker build --build-arg base=python:3.4 -f Dockerfile.test -t msae-python-test:python3.4 .
docker run --rm msae-python-test:python3.4
```