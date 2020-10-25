from ..instrument_types import TypeOTF
from ._BaseInstrument import BaseInstrument
import requests
import json
from ..constants import LIGHT_SPEED


class ModelWaveShaper4000A(BaseInstrument, TypeOTF):
    model = "WaveShaper 4000A"
    brand = "Finisar"
    details = {
        "Frequency Range": "191.1 ~ 196.46 THz"
    }
    params = [
        {
            "name": "port",
            "type": "int",
            "options": [1, 2, 3, 4]
        },
        {
            "name": "profile",
            "type": "str",
            "options": [
                "bandpass",
                "bandstop",
                "gaussian",
            ]
        }
    ]

    def __init__(self, resource_name, port, profile, timeout=5, **kwargs):
        super(ModelWaveShaper4000A, self).__init__()
        self.__resource_name = resource_name
        self.__timeout = timeout
        self.__port = port
        self.__profile = profile
        self._min_freq = 191.1
        self._max_freq = 196.46
        self._min_wl = LIGHT_SPEED/self._max_freq
        self._max_wl = LIGHT_SPEED/self._min_freq
        self.__curr_freq = None
        self.__curr_bw = None

    @property
    def resource_name(self):
        return self.__resource_name

    def close(self):
        pass
    
    def check_connection(self):
        try:
            requests.get('http://{ip}/waveshaper/devinfo'.format(ip=self.resource_name))
            return True
        except Exception:
            return False

    def __upload_profile(self, center, bw_in_ghz):
        """
        center: THz
        bandwidth: ghz
        """
        bw_in_thz = bw_in_ghz/1000
        data = {
            'type': self.__profile,
            'port': self.__port,
            'center': center,
            'bandwidth': bw_in_thz,
            'attn': 0
        }
        r = requests.post('http://{ip}/waveshaper/loadprofile'.format(ip=self.resource_name), json.dumps(data), timeout=self.__timeout)
        if not r.status_code == 200:
            raise ValueError('Error code: %d' % r.status_code)

    def get_wavelength(self):
        return LIGHT_SPEED/self.get_frequency()

    def get_frequency(self):
        if self.__curr_freq is None:
            return 0
        else:
            return self.__curr_freq

    def set_wavelength(self, wl):
        self.set_frequency(LIGHT_SPEED/wl)

    def set_frequency(self, freq):
        bw = self.__curr_bw
        if bw is None:
            self.__curr_bw = bw = 100
        self.__upload_profile(freq, bw)
        self.__curr_freq = freq

    def get_bandwidth_in_ghz(self):
        if self.__curr_bw is None:
            return 0
        else:
            return self.__curr_bw

    def set_bandwidth_in_ghz(self, bw):
        if self.__curr_freq is None:
            self.__curr_freq = 193.1
        self.__upload_profile(self.__curr_freq, bw)
        self.__curr_bw = bw
