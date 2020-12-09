from ._VisaInstrument import VisaInstrument
from ..instrument_types import TypeWM
from ..constants import OpticalUnit


class ModelAQ6150(VisaInstrument, TypeWM):
    model = ["AQ6150", "AQ6151"]
    brand = "Yokogawa"
    details = {
        "Wavelength Range": "1270 ~ 1650 nm",
        "Power Accuracy": "+/-0.5 dB",
        "Input Power Range": "-40 ~ 10 dBm",
        "Safe Power": "+18 dBm"
    }

    def __init__(self, resource_name, **kwargs):
        super(ModelAQ6150, self).__init__(resource_name, **kwargs)

    def run(self):
        """
        Start repeat measurement.
        """
        return self.command(":INIT:CONT ON")

    def stop(self):
        """
        Stop repeat measurement.
        """
        return self.command(":ABOR")

    def is_running(self):
        """
        Get measurement state of WM.
        :return: (bool) if repeat measurement is started.
        """
        status_str = self.query(":INIT:CONT?")
        status = bool(int(status_str))
        return status

    def get_frequency(self):
        """
        Get frequency of single peak in THz.

        :Returns: float, frequency in THz
        """
        freq_str = self.query(":MEASure:POWer:FREQuency?")
        freq = round(float(freq_str)/10**12, 6)
        if freq == 0:
            raise ValueError('AQ6150 input no signal.')
        return freq

    def get_wavelength(self):
        """
        Get wavelength of single peak in nm

        :Returns: float, wavelength in nm
        """
        wl_str = self.query(":MEASure:POWer:WAVelength?")
        wl = round(float(wl_str)*10**9, 6)
        if wl == 0:
            raise ValueError('AQ6150 input no signal.')
        return wl
