from ._VisaInstrument import VisaInstrument
from ..instrument_types import TypeOTF
from ..constants import OpticalUnit, LIGHT_SPEED
from time import sleep
import math

class ModelOTF930(VisaInstrument, TypeOTF):
    model = "OTF-930"
    brand = "Santec"
    details = {
        "Wavelength Range": "1520 ~ 1610 nm",
        "Frequency Range": "186.2 ~ 197.2 THz",
        "Bandwidth @-3dB": "Fixed, different across type",
        "Max Input Power": "+20 dBm"
    }

    def __init__(self, resource_name, read_termination='\r\n', write_termination='\r\n', **kwargs):
        super(ModelOTF930, self).__init__(resource_name, read_termination=read_termination,
                                          write_termination=write_termination, **kwargs)
        self._min_wl = 1520
        self._max_wl = 1610
        self._min_freq = math.floor(LIGHT_SPEED/self._max_wl*1000+1)/1000
        self._max_freq = math.floor(LIGHT_SPEED/self._min_wl*1000)/1000
        self.__unit = OpticalUnit.DBM

    # Methods
    def get_wavelength(self):
        """
        Reads out the setting value of the filter center wavelength.
        :return: (float) wavelength in nm.
        """
        wl_str = self.query('WA')
        wl = float(wl_str)
        return wl

    def set_wavelength(self, value):
        """
        Sets the filter center wavelength.
        :param value: (float|int) wavelength in nm
        """
        if not isinstance(value, (int, float)):
            raise TypeError('Wavelength value should be number')
        if not self.min_wavelength <= value <= self.max_wavelength:
            raise ValueError('Wavelength value out of range')
        return self.command('WA '+str(value))

    def get_frequency(self):
        """
        Reads out the filter center wavelength in optical frequency.
        :return: (float) optical frequency in THz
        """
        return round(LIGHT_SPEED/self.get_wavelength(), 3)

    def set_frequency(self, value):
        """
        Sets the filter center wavelength in frequency(THz).
        :param value: (float|int) optical frequency in THz
        """
        wl_value = round(LIGHT_SPEED/value, 3)
        return self.set_wavelength(wl_value)

    def get_wavelength_offset(self):
        """
        Reads out the offset wavelength of the filter center wavelength.
        :return: (float) wavelength offset in nm
        """
        offset_str = self.query('CW')
        offset = float(offset_str)
        return offset

    def set_wavelength_offset(self, value):
        """
        Sets the offset to the filter center wavelength.
        :param value: (float|int) wavelength
        """
        if not isinstance(value, (float, int)):
            raise TypeError('Wavelength offset value should be number')
        return self.command('CW %s' % str(round(value, 3)))

    def get_power_unit(self):
        """
        Get optical power unit of power monitor.
        :return: int, value of enum (OpticalUnit) optical power unit of power monitor
        """
        return self.__unit.value

    def set_power_unit(self, unit):
        """
        Set optical power unit of power monitor.
        :param unit: int, value of (OpticalUnit) optical power unit of power monitor
        """
        unit_enum = OpticalUnit(unit)
        self.__unit = unit_enum

    def get_power_value(self):
        """
        Get optical power value in selected unit. Range: -40dBm ~ 10dBm
        :return: (float) optical power in selected unit.
        """
        if self.__unit == OpticalUnit.DBM:
            return float(self.query('OP'))
        elif self.__unit == OpticalUnit.W:
            return float(self.query('LP')) / 1000
