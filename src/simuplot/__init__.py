# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os

# Define paths
base_path = os.path.dirname(os.path.dirname(__file__))
ui_path = os.path.join(base_path, 'resources/ui')
i18n_path = os.path.join(base_path, 'i18n/ts')

# Base Exception class for all Exceptions in the project
# This is a workaround to raise exceptions with Unicode messages,
# which is needed for internationalization
# http://stackoverflow.com/questions/29096702/how-can-i-raise-an-exception-that-includes-a-unicode-string

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

