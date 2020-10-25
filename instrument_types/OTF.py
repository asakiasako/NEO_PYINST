from ._BaseInstrumentType import BaseInstrumentType, InstrumentType
from time import sleep


class TypeOTF(BaseInstrumentType):
    """Optical Tunable Filter."""
    def __init__(self, *args, **kwargs):
        super(TypeOTF, self).__init__()
        self._append_ins_type(InstrumentType.OTF)
        # thresholds
        self._min_wl = None
        self._max_wl = None
        self._min_freq = None
        self._max_freq = None
        self._min_bw_in_nm = None
        self._max_bw_in_nm = None
        self._min_bw_in_ghz = None
        self._max_bw_in_ghz = None

    # -- properties --
    @ property
    def min_wavelength(self):
        if self._min_wl is None:
            self._raise_not_implemented()
        else:
            return self._min_wl

    @ property
    def max_wavelength(self):
        if self._max_wl is None:
            self._raise_not_implemented()
        else:
            return self._max_wl

    @ property
    def min_frequency(self):
        if self._min_freq is None:
            self._raise_not_implemented()
        else:
            return self._min_freq

    @ property
    def max_frequency(self):
        if self._max_freq is None:
            self._raise_not_implemented()
        else:
            return self._max_freq

    @ property
    def min_bandwidth_in_nm(self):
        if self._min_bw_in_nm is None:
            self._raise_not_implemented()
        else:
            return self._min_bw_in_nm

    @ property
    def max_bandwidth_in_nm(self):
        if self._max_bw_in_nm is None:
            self._raise_not_implemented()
        else:
            return self._max_bw_in_nm

    @ property
    def min_bandwidth_in_ghz(self):
        if self._min_bw_in_ghz is None:
            self._raise_not_implemented()
        else:
            return self._min_bw_in_ghz
    
    @ property
    def max_bandwidth_in_ghz(self):
        if self._max_bw_in_ghz is None:
            self._raise_not_implemented()
        else:
            return self._max_bw_in_ghz

    # -- methods --
    def get_wavelength(self):
        """
        Get the setting value of center wavelength in nm.
        
        :Returns: float, wavelength setting value in nm.
        """
        self._raise_not_implemented()

    def set_wavelength(self, value):
        """
        Set center wavelength in nm.
        
        :Parameters: **value** - float, center wavelength in nm.
        """
        self._raise_not_implemented()

    def get_frequency(self):
        """
        Get setting value of center frequency in THz.

        :Return Type: float
        """
        self._raise_not_implemented()

    def set_frequency(self, value):
        """
        Set center frequency in THz.

        :Parameters: **value** - float|int, optical frequency in THz
        """
        self._raise_not_implemented()

    def get_bandwidth_in_nm(self):
        """
        Get filter bandwidth in nm.

        :Return Type: float
        """
        self._raise_not_implemented()

    def set_bandwidth_in_nm(self, value):
        """
        Set filter bandwidth.

        :Parameters: **value** - float|int, bandwidth setting value in nm
        """
        self._raise_not_implemented()

    def peak_search(self, center, span):
        """
        Search peak near the given center wavelength.

        :Parameters:
            - **center** - int|float, center wavelength in nm.
            - **span** - int|float, span in nm.
        """
        self._raise_not_implemented()
