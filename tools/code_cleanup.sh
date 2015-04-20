#!/bin/bash

# Remove whitespaces at end of lines
for f in `find $(dirname $BASH_SOURCE)/../src/ -name "*.py"`; do sed -i 's/[ ]*$//' $f; done

# Change 'Alt-Gr + space' into 'space' (common typo)
for f in `find $(dirname $BASH_SOURCE)/../src/ -name "*.py"`; do sed -i 's/ / /' $f; done

