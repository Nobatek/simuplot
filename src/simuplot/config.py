# Define color charts
NBK_COLOR_CHART = 16 * ['#E36C09', '#7F7F7F', '#1F497D',
                        '#A5A5A5', '#F79646', '#FAC08F']
INEF4_COLOR_CHART = 16 * ['#8EC02F', '#E47823', '#FEA022',
                          '#6A4300', '#868786', '#1B461E',
                          '#000000']

class Config(object):

    def __init__(self):

        self._params = {}

    # TODO: Read config
    def read(self):
        """Currently just a stub"""

        self._params['color_chart'] = INEF4_COLOR_CHART

    # TODO: Write config
    def write(self):
        pass

    @property
    def params(self):
        return self._params

