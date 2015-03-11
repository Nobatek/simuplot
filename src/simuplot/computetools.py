# -*- coding: utf-8 -*-

import datetime

def create_inter (begin=None, end=None):

    # Set simulation first day (if Energyplus simulation it s a Sunday)
    # CAUTION : For now Simuplot works for full year only
    day0 = datetime.datetime(today.year,1,1,0,0,0)

    # Determine whether to create one or two interval
    # And compute interval boundaries
    if end > begin :   
        # Create only one interval
        b1 = begin - day0
        b2 = end - day0
        print b2
        return [[b1.days * 24 + b1.seconds / 3600,
                 b2.days * 24 + b2.seconds / 3600]]
    else :
        # Create two intervals
        b21 = end - day0
        b12 = begin - day0
        return [[0 , b21.days * 24 + b21.seconds / 3600],
                [b12.days * 24 + b12.seconds / 3600 , 8760]]