# mlabwrap

## Acknowledgement

This is a fork of <https://bitbucket.org/nikratio/mlabwrap> to fix some bugs.

I'm not familiar with hg. But I may checkout updates from <https://bitbucket.org/nikratio/mlabwrap>.

Thanks [this site](http://obasic.net/how-to-install-mlabwrap-on-windows), I made it run on Windows.

## Platform

The setup.py is configurated for Windows platform, with Python3 **32 bit** and Matlab **32 bit**.

## Installation

In VS2008 Command Prompt:

```
python setup.py bdist_egg --matlab=PATH_TO_YOUR_MATLAB_DOT_EXE
easy_install dist\xxx.egg
```

## Changlog

### 1.1.3 (2012-11-21)

* using system encoding scheme to decode string in `mlabraw.eval`
* fix memory leak in `mlabraw.put` caused by chained `char2mx` and `PyUnicode_AsUTF8String`

### 1.1.2

#### Cannot delete temporary file

> [Error 32] The process cannot access the file because it is being used by another process:...

mentioned [here](http://obasic.net/how-to-install-mlabwrap-on-windows#comment-11549).

#### Unable to extract MATLAB(TM) string

When function documentation contains multibyte encoded characters, like Chinese, this error will occur. Because `mxGetString` don't support multibyte encoded characters. I use `mxArrayToString` instead.
