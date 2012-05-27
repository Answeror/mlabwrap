# mlabwrap

## Acknowledgement

This is a fork of <https://bitbucket.org/nikratio/mlabwrap> to fix some bugs.

I'm not familiar with hg. But I may checkout updates from <https://bitbucket.org/nikratio/mlabwrap>.

Thanks [this site](http://obasic.net/how-to-install-mlabwrap-on-windows), I made it run on Windows.

## Platform

The setup.py is configurated for Windows platform, with Python 2.7.2 **64 bit** and Matlab **64 bit**.

## Installation

Use `build.bat` to install.

## Fixed bugs

### Cannot delete temporary file

> [Error 32] The process cannot access the file because it is being used by another process:...

mentioned [here](http://obasic.net/how-to-install-mlabwrap-on-windows#comment-11549).

### Unable to extract MATLAB(TM) string

When function documentation contains multibyte encoded characters, like Chinese, this error will occur. Because `mxGetString` don't support multibyte encoded characters. I use `mxArrayToString` instead.
