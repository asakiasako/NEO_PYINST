from ._BaseInstrument import BaseInstrument
from ..instrument_types import TypeSW
import subprocess
import os
import time
import usb
import win32com.client


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

    try:
        _ops = win32com.client.Dispatch('Neo_SmartOpticalSwitch.SmartOpticalSwitch')
    except Exception:
        _ops = None

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
        if not self._ops:
            raise ModuleNotFoundError('Neo_SmartOpticalSwitch.SmartOpticalSwitch')

    @property
    def resource_name(self):
        return self.__resource_name

    @classmethod
    def get_usb_devices(cls, num=9):
        if not cls._ops:
            raise ModuleNotFoundError('Neo_SmartOpticalSwitch.SmartOpticalSwitch')
        cls._ops.InitIntefaceType = 3
        dev_list = [cls._ops.GetMultiUSBDeviceName(i) for i in range(num) if cls._ops.GetMultiUSBDeviceName(i) != 'NoDevice']
        return dev_list

    def close(self):
        pass

    def check_connection(self):
        channel = self.get_channel()
        if channel > 0:
            return True
        return False

    def _select_device(self):
        dev_list = self.get_usb_devices()
        if self.resource_name not in dev_list:
            raise ValueError('Invalid device name: %s' % self.resource_name)
        self._ops.USBDeviceName = self.resource_name
        self._ops.InitIntefaceType = 2

    def __set_channel_single(self, channel):
        index = self.__index
        self._select_device()
        self._ops.SetSelectChannel(index, channel)

    def __get_channel_single(self):
        index = self.__index
        self._select_device()
        channel = self._ops.GetSelectChannel(index)
        return channel

    def __check_channel(self, expected, max_try=5):
        tried = 0
        while True:
            tried += 1
            time.sleep(0.4)
            ch = self.__get_channel_single()
            if ch == expected:
                break
            else:
                if tried >= max_try:
                    raise ValueError('Check Neo_Opswitch channel failed. DeviceName: %s' % self.resource_name)

    def set_channel(self, channel, max_try=3):
        """
        Set channel.
        :param channel: (int) channel number (1 based)
        """
        tried = 0
        while True:
            tried += 1
            try:
                self.__set_channel_single(channel)
                self.__check_channel(channel)
                break
            except Exception as e:
                try:
                    self.reset()
                    time.sleep(1)
                except Exception:
                    pass
                if tried >= max_try:
                    raise ValueError('Unable to set Neo_Opswitch channel. DeviceName: %s' % self.resource_name)

    def get_channel(self, max_try=3):
        """
        Get selected channel.
        :return: (int) selected channel (1 based)
        """
        tried = 0
        while True:
            tried += 1
            try:
                return self.__get_channel_single()
            except Exception as e:
                if tried >= max_try:
                    raise RuntimeError('Unable to get Neo_Opswitch channel. DeviceName: %s' % self.resource_name)

    def reset(self):
        """
        Neo Optical Switch may lose USB control during auto test.
        This method reset the USB port to solve the connection issue.
        """
        serial_number = self.resource_name
        dev = usb.core.find(serial_number=serial_number)
        if not dev:
            raise AttributeError('Error on Reset: USB Device not found. SN = %s' % serial_number)
        dev.reset()
