# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 14:53:39 2022

@author: jimen
"""

import numpy as np

tab=np.random.normal(0,1,(5,5))
grad=np.gradient(tab,2,2)