# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os

# Define paths
BASE_PATH = os.path.dirname(os.path.dirname(__file__))
UI_PATH = os.path.join(BASE_PATH, 'resources/ui')
I18N_PATH = os.path.join(BASE_PATH, 'i18n/ts')

# Base Exception class for all Exceptions in the project
# This is a workaround to raise exceptions with Unicode messages,
# which is needed for internationalization
# http://stackoverflow.com/questions/29096702/

class SimuplotError(Exception):

    def __init__(self, message):

        if isinstance(message, unicode):

            super(SimuplotError, self).__init__(message.encode('utf-8'))

            self.message = message

        elif isinstance(message, str):

            super(SimuplotError, self).__init__(message)

            self.message = message.decode('utf-8')

        # This shouldn't happen...
        else:
            raise TypeError

    def __unicode__(self):

        return self.message

