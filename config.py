# -*- coding: utf-8 -*-

NBK_color_chart = 16 * ['#E36C09','#7F7F7F','#1F497D','#A5A5A5','#F79646','#FAC08F']

rt_zone_climatique={'H1a - H1b - H2a - H2b':0.02,
                    'H1c - H2c':0.025,
                    'H2d - H3':0.03}
                    
hqe_selec_tmax={'bureau - enseignement':28,
            'hotel':26,
            'commun/circulation commerce et beignade':30,
            'entrpôts':35}

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

