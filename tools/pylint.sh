#!/bin/bash
pylint $(dirname $BASH_SOURCE)/../src/simuplot --extension-pkg-whitelist=numpy,PyQt4,matplotlib
