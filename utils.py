import math
from .constants import LIGHT_SPEED


def w_to_dbm(value):
    """
    Convert optical power in watt to optical power in dbm
    :param value: (float|int) optical power in watt.
    :return: (float) optical power in dbm
    """
    if not isinstance(value, (float, int)):
        raise TypeError('value of optical power in watt should be a number (int or float).')
    if value < 0:
        raise ValueError('value of optical power in watt should >= 0')
    dbm_value = 10*math.log(value*1000, 10)
    dbm_value = float(dbm_value)
    return dbm_value


def dbm_to_w(value):
    """
    Convert optical power in dbm to power in watt
    :param value: (float|int) optical power in dbm
    :return: (float) optical power in watt
    """
    if not isinstance(value, (float, int)):
        raise TypeError('value of optical power in watt should be a number (int or float).')
    w_value = (10**(value/10))/1000
    w_value = float(w_value)
    return w_value


def bw_in_nm_to_ghz(bw_in_nm, center_wl):
    """
    bw_in_nm: nm
    center_wl: nm
    """
    C = LIGHT_SPEED
    bw_in_ghz = 1000 * (C/(center_wl-bw_in_nm/2) - C/(center_wl+bw_in_nm/2))
    return bw_in_ghz


def bw_in_ghz_to_nm(bw_in_ghz, center_freq):
    """
    bw_in_ghz: GHz
    center_freq: THz
    """
    C = LIGHT_SPEED
    bw_in_nm = C/(center_freq-bw_in_ghz/2000) - C/(center_freq+bw_in_ghz/2000)
    return bw_in_nm


def format_unit(value, precision):
    """
    Format base unit to readable styles, suchas: 0.034 -> (34, 'm'), 2.3e-10 -> (230, 'p')
    m: 1E-3; u: 1E-6; n: 1E-9; p: 1E-12
    :param value: (float|int) initial value in base unit
    :param precision: (int) decimal digits
    :return: (tuple) (float:value, str:prefix)
    """
    if not isinstance(value, (float, int)):
        raise TypeError('value should be a number (int or float).')
    if not isinstance(precision, int):
        raise TypeError('precision should be a int')
    abs_value = abs(value)
    if abs_value < 1e-9:
        value = value*10**12
        value = round(value, precision)
        return value, 'p'
    elif 1e-9 <= abs_value < 1e-6:
        value = value*10**9
        value = round(value, precision)
        return value, 'n'
    elif 1e-6 <= abs_value < 1e-3:
        value = value*10**6
        value = round(value, precision)
        return value, 'u'
    elif 1e-3 <= abs_value < 1:
        value = value*10**3
        value = round(value, precision)
        return value, 'm'
    else:
        return value, ''


def complement_to_int(comp, bytes_num):
    range_str = '0x%s' % ('FF'*bytes_num)
    range_val = int(range_str, 16)
    if comp < (range_val+1)/2:
        return comp
    else:
        return comp - range_val - 1


def int_to_complement(value, bytes_num):
    """
    :return: (str) a str of Hex caractors with fixed length such as: '0048', 'FF3A'
    """
    if not isinstance(value, int):
        raise TypeError('value to convert should be int')
    range_str = '0x%s' % ('FF' * bytes_num)
    range_val = int(range_str, 16)
    if not -(range_val+1)/2 <= value <= (range_val+1)/2 - 1:
        raise ValueError('value to convert is out of valid range')
    if value >= 0:
        return '%0*X' % (bytes_num*2, value)
    else:
        return '%0*X' % (bytes_num*2, value+range_val+1)


def calc_check_sum(str0):
    return sum([ord(i) for i in str0])
