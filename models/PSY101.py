from ._VisaInstrument import VisaInstrument
from ..instrument_types import TypePOLC
from ..constants import LIGHT_SPEED
import math


class ModelPSY101(VisaInstrument, TypePOLC):
    model = "PSY-101"
    brand = "General Photonics"
    details = {
        "Wavelength Range": "1500-1600 nm",
        "Operating power range": "-15 to 10 dBm"
    }

    def __init__(self, resource_name, write_termination='', read_termination='#', **kwargs):
        super(ModelPSY101, self).__init__(
            resource_name, write_termination=write_termination, read_termination=read_termination, **kwargs
        )
        # thresholds
        self._min_wl = 1500
        self._max_wl = 1600
        self._min_freq = math.floor(LIGHT_SPEED*1000/self._max_wl)/1000 + 0.001
        self._max_freq = math.floor(LIGHT_SPEED*1000/self._min_wl)/1000

    def get_wavelength(self):
        """
        Get current wavelength setting (nm)
        :return: (float) wavelength
        """
        rpl = self.query('*WAV?')
        return float(rpl.strip('*WAV'))

    def get_frequency(self):
        return LIGHT_SPEED/self.get_wavelength()

    def set_wavelength(self, wavelength):
        """
        Set wavelength setting (nm)
        :param wavelength: (float, int) wavelength in nm
        """
        if not isinstance(wavelength, (float, int)):
            raise TypeError('wavelength should be number')
        if not self.min_wavelength <= wavelength <= self.max_wavelength:
            raise ValueError('wavelength out of range')
        wavelength = round(wavelength)
        rpl = self.query('*WAV %04d#' % wavelength)
        if not rpl.strip() == '*E00':
            raise ValueError('Set wavelength failed. ErrCode={}'.format(rpl))

    def set_frequency(self, freq):
        return self.set_wavelength(LIGHT_SPEED/freq)
    
    def _set_scrambling_param(self, mode, speed):
        """
        Set scrambling params.
        :param mode: (str) Scrambling mode: RANDOM | SAW
        :param params: (any, any, ...) Scrambling params.
        """
        if mode == 'RANDOM':
            if not 1 <= speed <= 6000:
                raise ValueError('Invalid scrambling speed: mode=RANDOM, speed={speed}'.format(speed=speed))
            speed = round(speed)
            rpl = self.query('*RAN:FRQ {speed:04d}#'.format(speed=speed))
        elif mode == 'SAW':
            if not 0.1 <= speed <= 500:
                raise ValueError('Invalid scrambling speed: mode=RANDOM, speed={speed}'.format(speed=speed))
            speed = round(speed, 1)
            rpl = self.query('*SAW:FRQ {speed:.1f}#'.format(speed=speed))
        else:
            raise ValueError('Invalid scrambling mode: {mode}'.format(mode=mode))
        if not rpl.strip() == '*E00':
            raise ValueError('Set scrambling param failed. ErrCode={}'.format(rpl))
    
    def _set_scrambling_state(self, mode, is_on):
        """
        Start or pause scrambling.
        :param mode: (str) Scrambling mode: RANDOM | SAW
        :param ison: (bool) True->start  False->stop
        """
        if mode == 'RANDOM':
            rpl = self.query('*RAN:ENA {state}#'.format(state = 'ON' if is_on else 'OFF'))
        elif mode == 'SAW':
            rpl = self.query('*SAW:ENA {state}#'.format(state = 'ON' if is_on else 'OFF'))
        else:
            raise ValueError('Invalid scrambling mode: {mode}'.format(mode=mode))
        if not rpl.strip() == '*E00':
            raise ValueError('Set scrambling state failed. ErrCode={}'.format(rpl))

    def start_scrambling(self, mode, speed, *params):
        self._set_scrambling_param(mode, speed, *params)
        self._set_scrambling_state(mode, True)

    def stop_scrambling(self):
        self._set_scrambling_state('TORN', False)