''' A file to store general basic functionality needed in different modules.'''
import numpy as np


def round_num(num, decimal_places=4):
    """Rounds a number to the selected num of decimal places
    This allows consistency throughout the method and avoids
    numerical artifacts"""
    return np.round(num, decimal_places)
