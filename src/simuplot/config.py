# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

NBK_color_chart = 16 * ['#E36C09','#7F7F7F','#1F497D','#A5A5A5','#F79646','#FAC08F']

class Config(object):

    def __init__(self):

        self._params = {}

    # TODO: Read config
    def read(self):
        """Currently just a stub"""

        self._params['color_chart'] = NBK_color_chart

    # TODO: Write config
    def write(self):
        pass

    @property
    def params(self):
        return self._params

