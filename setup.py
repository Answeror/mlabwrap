#!/usr/bin/env python

##############################################################################
########################### setup.py for mlabwrap ############################
##############################################################################
## o author: Alexander Schmolck (a.schmolck@gmx.net)
## o created: 2003-08-07 17:15:22+00:40

import os
import os.path
from setuptools import setup, Extension
import sys
import re
import tempfile
import subprocess as sp
from textwrap import dedent
from utils import has_option
from utils import option_value


# find executable in PATH
def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def find_matlab():
    """Try to find matlab home by MATLAB_HOME and exe in PATH."""
    # e.g: '/usr/local/matlab'; 'c:/matlab6'
    home = os.environ['MATLAB_HOME']
    if home:
        return home
    exe = which('matlab.exe')
    if exe:
        return os.path.dirname(os.path.dirname(exe))
    return None


def find_visual_studio(exe=None):
    """Try to find VC directory by devenv.exe in PATH."""
    if exe is None:
        exe = which('devenv.exe')
    if exe:
        dirname = os.path.dirname
        return os.path.join(dirname(dirname(dirname(exe))), 'VC')
    return None


def find_vc_include_dirs():
    return os.environ['INCLUDE'].split(';')


def find_vc_library_dirs():
    return os.environ['LIB'].split(';')


def main():
    __version__ = '1.1.3'

    OPTION_MATLAB = option_value('matlab')
    OPTION_DEVENV = option_value('devenv')


    # global variables begin

    MATLAB_COMMAND = 'matlab'   # specify a full path if not in PATH
    MATLAB_VERSION = 7.3       # e.g: 6 (one of (6, 6.5, 7, 7.3))
                                #      7.3 includes later versions as well
    #MATLAB_DIR = find_matlab()
    MATLAB_DIR = os.path.dirname(os.path.dirname(OPTION_MATLAB))
    if not MATLAB_DIR:
        print('You must set environment variable MATLAB_HOME first.')
        return 1

    PLATFORM_DIR = None           # e.g: 'glnx86'; r'win32/microsoft/msvc60'
    EXTRA_COMPILE_ARGS = None     # e.g: ['-G']

    # hopefully these 3 won't need modification
    MATLAB_LIBRARIES = None       # e.g: ['eng', 'mx', 'mat', 'mi', 'ut']
    USE_NUMERIC = None            # use obsolete Numeric instead of numpy?
    PYTHON_INCLUDE_DIR = None     # where to find numpy/*.h

    SUPPORT_MODULES = ["awmstools"]  # set to [] if already
                                    # installed
    ########################### WINDOWS ONLY ###########################
    #  Option 1: Visual Studio
    #  -----------------------
    #  only needed for Windows Visual Studio (tm) build
    #  (adjust if necessary if you use a different version/path of VC)
    #VC_DIR='C:/Program Files (x86)/Microsoft Visual Studio 9.0/VC'
    # NOTE: You'll also need to adjust PLATFORM_DIR accordingly
    #
    #  Option 2: Borland C++
    #  ---------------------
    #  uncomment (and adjust if necessary) the following lines to use Borland C++
    #  instead of VC:
    #
    #VC_DIR=None
    VC_DIR = find_visual_studio(OPTION_DEVENV)
    #PLATFORM_DIR="win32/borland/bc54"
    PLATFORM = '32'

    # global variables end

    ####################################################################
    ### NO MODIFICATIONS SHOULD BE NECESSARY BEYOND THIS POINT       ###
    ####################################################################
    # *******************************************************************

    if sys.version_info < (2, 2):
        print >> sys.stderr, "You need at least python 2.2"
        return 1

    if PYTHON_INCLUDE_DIR is None and not USE_NUMERIC:
        try:
            import numpy
            PYTHON_INCLUDE_DIR = numpy.get_include()
        except ImportError:
            print("Warning: numpy not found. Still using Numeric?")
            try:
                import Numeric
                if USE_NUMERIC is None:
                    USE_NUMERIC = True
            except ImportError:
                print("CANNOT FIND EITHER NUMPY *OR* NUMERIC")

    def matlab_params(cmd, is_windows, extra_args):
        fh = tempfile.NamedTemporaryFile(delete=False)
        param_fname = fh.name
        # XXX I have no idea why '\n' instead of the ``%c...,10`` hack fails - bug
        # in matlab's cmdline parsing? (``call`` doesn't do shell mangling, so that's not it...)
        code = ("fid = fopen('%s', 'wt');" % param_fname +
                r"fprintf(fid, '%s%c%s%c%s%c', version, 10, matlabroot, 10, computer, 10);" +
                "fclose(fid); quit")
        if is_windows:
            code = '"' + code + '"'
        cmd += ['-r', code]
        fh = None
        try:
            error = sp.call(cmd, **extra_args)
            if error:
                print('''INSTALL ABORT: %r RETURNED ERROR CODE %d
    PLEASE MAKE SURE matlab IS IN YOUR PATH!
    ''' % (" ".join(cmd), error))
                return 1
            with open(param_fname, 'r') as fh:
                ver, pth, platform = iter(fh)
                return (float(re.match(r'\d+.\d+', ver).group()), \
                        pth.rstrip(), platform.rstrip().lower())
        finally:
            try:
                os.unlink(fh.name)
            except OSError as msg:  # FIXME
                print(dedent('''\
                        windows SPECIFIC ISSUE? Unable to remove %s;
                        please delete it manually
                        %s''' % (param_fname, msg)))

    # windows
    windows = sys.platform.startswith('win')
    if None in (MATLAB_VERSION, MATLAB_DIR, PLATFORM_DIR):
        cmd = [MATLAB_COMMAND, "-nodesktop",  "-nosplash"]
        if windows:
            extra_args = {}
            cmd += ["-wait"]
        else:
            extra_args = dict(stdout=open('/dev/null', 'wb'))
        ## FIXME: it is necessary to call matlab to figure out unspecified install
        ## parameters but only if the user actually intends to build something
        ## (e.g. not for making a sdist or running a clean or --author-email etc.).
        ## Unfortunately I can't see a clean way to do that, so this nasty kludge
        ## attempts to avoid calling matlab unless required.
        #if len(sys.argv) > 1 and not (
            #re.search("sdist|clean", sys.argv[1]) or
            #len(sys.argv) == 2 and sys.argv[1].startswith('--') or
            #sys.argv[-1].startswith('--help')):
            #queried_version, queried_dir, queried_platform_dir = matlab_params(cmd, windows, extra_args)
        #else:
            #queried_version, queried_dir, queried_platform_dir = ["WHATEVER"] * 3
        #MATLAB_VERSION = MATLAB_VERSION or queried_version
        #MATLAB_DIR = MATLAB_DIR or queried_dir
        PLATFORM_DIR = 'win{}/microsoft'.format(PLATFORM)

    if windows:
        EXTENSION_NAME = 'mlabraw'
        MATLAB_LIBRARIES = MATLAB_LIBRARIES or 'libeng libmx'.split()
        CPP_LIBRARIES = []  # XXX shouldn't need CPP libs for windoze

    # unices
    else:
        EXTENSION_NAME = 'mlabrawmodule'
        if not MATLAB_LIBRARIES:
            if MATLAB_VERSION >= 6.5:
                MATLAB_LIBRARIES = 'eng mx mat ut'.split()
            else:
                MATLAB_LIBRARIES = 'eng mx mat mi ut'.split()
        CPP_LIBRARIES = ['stdc++']  # XXX strangely  only needed on some linuxes
        if sys.platform.startswith('sunos'):
            EXTRA_COMPILE_ARGS = EXTRA_COMPILE_ARGS or ['-G']

    if MATLAB_VERSION >= 7 and not windows:
        MATLAB_LIBRARY_DIRS = [MATLAB_DIR + "/bin/" + PLATFORM_DIR]
    else:
        MATLAB_LIBRARY_DIRS = [MATLAB_DIR + "/extern/lib/" + PLATFORM_DIR]
    MATLAB_INCLUDE_DIRS = [MATLAB_DIR + "/extern/include"]  # "/usr/include"
    if windows:
        if VC_DIR:
            MATLAB_INCLUDE_DIRS += find_vc_include_dirs()
            MATLAB_LIBRARY_DIRS += find_vc_library_dirs()
        else:
            print("Not using Visual C++; fiddling paths for Borland C++ compatibility")
            MATLAB_LIBRARY_DIRS = [mld.replace('/', '\\') for mld in  MATLAB_LIBRARY_DIRS]
    DEFINE_MACROS = []
    if MATLAB_VERSION >= 6.5:
        DEFINE_MACROS.append(('_V6_5_OR_LATER', 1))
    if MATLAB_VERSION >= 7.3:
        DEFINE_MACROS.append(('_V7_3_OR_LATER', 1))
    if USE_NUMERIC:
        DEFINE_MACROS.append(('MLABRAW_USE_NUMERIC', 1))

    MATLAB_INCLUDE_DIRS = [d for d in MATLAB_INCLUDE_DIRS if d]
    MATLAB_LIBRARY_DIRS = [d for d in MATLAB_LIBRARY_DIRS if d]

    setup(  # Distribution meta-data
            name="mlabwrap",
            version=__version__,
            description="A high-level bridge to matlab",
            author="Alexander Schmolck",
            author_email="A.Schmolck@gmx.net",
            py_modules=["mlabwrap"] + SUPPORT_MODULES,
            url='http://mlabwrap.sourceforge.net',
            ext_modules=[
                Extension(EXTENSION_NAME, ['mlabraw.cpp'],
                        define_macros=DEFINE_MACROS,
                        library_dirs=MATLAB_LIBRARY_DIRS,
                        #runtime_library_dirs=MATLAB_LIBRARY_DIRS,
                        libraries=MATLAB_LIBRARIES + CPP_LIBRARIES,
                        include_dirs=MATLAB_INCLUDE_DIRS + [PYTHON_INCLUDE_DIR],
                        extra_compile_args=EXTRA_COMPILE_ARGS,
                        ),
            ],
            use_2to3=True
        )

    return 0

main()
