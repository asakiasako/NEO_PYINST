from ._BaseInstrumentType import BaseInstrumentType, InstrumentType
from ..utils import dbm_to_w, w_to_dbm


class TypeWM(BaseInstrumentType):
    def __init__(self, *args, **kwargs):
        super(TypeWM, self).__init__()
        self._append_ins_type(InstrumentType.WM)

    def run(self):
        """
        Start repeat measurement.
        """
        self._raise_not_implemented()

    def stop(self):
        """
        Stop repeat measurement.
        """
        self._raise_not_implemented()

    def is_running(self):
        """
        Get measurement state of WM.

        :Returns: bool, if repeat measurement is started.
        """
        self._raise_not_implemented()

    def get_frequency(self):
        """
        Get frequency of single peak in THz.

        :Returns: float, frequency in THz
        """
        self._raise_not_implemented()

    def get_wavelength(self):
        """
        Get wavelength of single peak in nm

        :Returns: float, wavelength in nm
        """
        self._raise_not_implemented()
