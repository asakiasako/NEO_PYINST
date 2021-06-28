from ._BaseInstrument import BaseInstrument
from ..instrument_types import TypeSW
import subprocess
import os
import time
from ..libs.neo_usb_device import NeoUsbDevice


class ModelNSW(BaseInstrument, TypeSW):
    model = "Neo_SW"
    brand = "NeoPhotonics"
    params = [
        {
            "name": "slot_or_type",
            "type": "str",
            "options": ['1', '2', '3', '1*8', '1*16']
        }
    ]
    details = {
        "Note": "Valid slot depending on specific instrument."
    }

    def __init__(self, resource_name, slot_or_type):
        """
        slot_or_type: 1, 2, 3, '1*8', '1*16'
        """
        super(ModelNSW, self).__init__()
        self.__resource_name = resource_name
        if isinstance(slot_or_type, int):
            self.__index = slot_or_type - 1
        else:
            index_map = {
                '1': 0,
                '2': 1,
                '3': 2,
                '1*8': 3,
                '1*16': 4,
            }
            try:
                self.__index = index_map[slot_or_type]
            except KeyError:
                raise KeyError('Invalid value for slot_or_type: %r' % slot_or_type)
        self.__usb_dev = NeoUsbDevice(resource_name)
        self.__reg_ch_sel = 16*self.__index + 130
        if not self.check_connection():
            raise ConnectionError('Unable to connect Neo_SW.')

    @property
    def resource_name(self):
        return self.__resource_name

    @classmethod
    def get_usb_devices(cls):
        return [i["Serial Number"].upper() for i in NeoUsbDevice.get_devices_information()]

    def close(self):
        pass

    def check_connection(self):
        try:
            channel = self.get_channel()
            if channel > 0:
                connected = True
            else:
                connected = False
        except Exception:
            connected = False
        return connected

    def set_channel(self, channel:int):
        self.__usb_dev.write_registers(0xC2, self.__reg_ch_sel, channel.to_bytes(1, 'big'))
        time.sleep(0.4)
        if self.get_channel() != channel:
            raise ValueError('Set switch channel failed.')

    def get_channel(self):
        channel = int.from_bytes(self.__usb_dev.read_registers(0xC2, self.__reg_ch_sel, 1), 'big')
        print(f'GET->{channel}')
        return channel


