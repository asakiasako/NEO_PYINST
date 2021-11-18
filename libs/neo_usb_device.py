import ctypes
import time

def _dec_open_close(function):
    def wrapper(self, *args, **kwargs):
        try:
            self.open()
            return function(self, *args, **kwargs)
        finally:
            self.close()
    return wrapper

class NeoUsbDevice:

    dll_si_usb = ctypes.cdll.LoadLibrary('SiUSBXp.dll')

    @classmethod
    def check_si_status(cls, si_status):
        if si_status:
            raise ValueError('SI_STATUS Error: 0x{ec:X}'.format(ec=si_status))

    @classmethod
    def count_devices(cls):
        count = ctypes.c_ulong()
        si_status = cls.dll_si_usb.SI_GetNumDevices(ctypes.byref(count))
        cls.check_si_status(si_status)
        return count.value

    @classmethod
    def get_product_string(cls, devnum, flag):
        buff = ctypes.create_string_buffer(1024)
        si_status = cls.dll_si_usb.SI_GetProductString(devnum, ctypes.byref(buff), ctypes.c_ulong(flag))
        cls.check_si_status(si_status)
        return buff.value.decode()

    @classmethod
    def get_devices_information(cls):
        num = cls.count_devices()
        info = [
            {
                "Device Number": i,
                "Serial Number": cls.get_product_string(i, 0),
                "Description": cls.get_product_string(i, 1),
                "Link Name": cls.get_product_string(i, 2),
                "VID": cls.get_product_string(i, 3),
                "PID": cls.get_product_string(i, 4),
            } for i in range(num)
        ]
        return info

    def __init__(self, sn_or_devnum):
        if isinstance(sn_or_devnum, int):
            self.__devnum = sn_or_devnum
        elif isinstance(sn_or_devnum, str):
            self.__devnum = self.__get_devnum_by_sn(sn_or_devnum)
        else:
            raise TypeError("sn_or_devnum should be int or str")
        if not 0 <= self.__devnum < self.count_devices():
            raise ValueError('SI DevNum out of range.')
        self.__handle = ctypes.c_ulong()
        self.__is_open = False

    @property
    def is_open(self):
        return self.__is_open

    @property
    def devnum(self):
        return self.__devnum

    @property
    def sn(self):
        return self.get_product_string(self.__devnum, 0).strip()

    @property
    def link_name(self):
        return self.get_product_string(self.__devnum, 2).strip()

    @property
    def vid(self):
        return self.get_product_string(self.__devnum, 3).strip()

    @property
    def pid(self):
        return self.get_product_string(self.__devnum, 4).strip()

    def __get_devnum_by_sn(self, sn:str):
        info = self.get_devices_information()
        sn = sn.strip()
        for idx, i_info in enumerate(info):
            if sn.lower() == i_info["Serial Number"].strip().lower():
                devnum = idx
                break
        else:
            raise ValueError('No device with SN={sn}'.format(sn=sn))
        return devnum

    def _action_open(self):
        handle = ctypes.c_ulong()
        si_status = self.dll_si_usb.SI_Open(ctypes.c_int(self.__devnum), ctypes.byref(handle))
        self.check_si_status(si_status)
        self.__handle = handle  # save handle only when opened successfully

    def _action_close(self):
        si_status = self.dll_si_usb.SI_Close(self.__handle)
        self.check_si_status(si_status)

    def set_timeouts(self, r, w):
        si_status = self.dll_si_usb.SI_SetTimeouts(r, w)
        self.check_si_status(si_status)

    def open(self):
        if not self.__is_open:
            self.set_timeouts(500, 1000)
            self._action_open()
            self.__is_open = True

    def close(self):
        if self.__is_open:
            try:
                self._action_open()
            except ValueError:
                pass
            finally:
                self._action_close()
            self.__is_open = False

    def clear_buffer(self):
        c_1 = ctypes.c_uint(1)
        si_status = self.dll_si_usb.SI_FlushBuffers(self.__handle, c_1, c_1)
        self.check_si_status(si_status)

    @_dec_open_close
    def read_registers(self, dev_addr, reg_addr, reg_size):
        cmd = [0xEF, 0xEF, 0x00, 0x06, 0xF1, dev_addr, reg_addr, reg_size>>8, reg_size & 0xFF, 0x00]
        cmd[-1] = sum(cmd[:-1]) & 0xFF
        tx_buff = (ctypes.c_char * 10)(*cmd)
        rx_buff = (ctypes.c_char * (9+reg_size))()

        self.clear_buffer()

        n_to_write = ctypes.c_long(10)
        n_written = ctypes.c_long()
        si_status = self.dll_si_usb.SI_Write(self.__handle, ctypes.byref(tx_buff), n_to_write, ctypes.byref(n_written), 0)
        self.check_si_status(si_status)
        if n_to_write.value != n_written.value:
            raise ValueError('Error SI_Write: mismatch of bytes to write and bytes written.')

        n_bytes_in_queue = ctypes.c_ulong()
        queue_status = ctypes.c_ulong()
        for _ in range(100):
            si_status = self.dll_si_usb.SI_CheckRXQueue(self.__handle, ctypes.byref(n_bytes_in_queue), ctypes.byref(queue_status))
            self.check_si_status(si_status)
            #define SI_RX_NO_OVERRUN 0x00
            #define SI_RX_EMPTY 0x00
            #define SI_RX_OVERRUN 0x01
            #define SI_RX_READY 0x02
            if queue_status.value == 2:
                break
            else:
                time.sleep(0.001)
        else:
            raise ValueError('Wait for SI_RX_READY timeout.')

        n_to_read = ctypes.c_ulong(len(rx_buff))
        n_read = ctypes.c_ulong()
        si_status = self.dll_si_usb.SI_Read(self.__handle, rx_buff, n_to_read, ctypes.byref(n_read), 0)
        self.check_si_status(si_status)
        if n_to_read.value != n_read.value:
            raise ValueError('Error SI_Read: mismatch of bytes to read and bytes read.')
        if rx_buff[7][0] != 0xE0:
            raise ValueError('Error device response: check ACK failed.')

        return bytes(rx_buff[8:-1])

    @_dec_open_close
    def write_registers(self, dev_addr, reg_addr, data):
        """
        data: bytes or other iterable consists of int (0~255)
        return: number of bytes written to register
        """
        len_cmd = (len(data) + 4).to_bytes(2, 'big')
        
        cmd = [0xEF, 0xEF, len_cmd[0], len_cmd[1], 0xF0, dev_addr, reg_addr]
        cmd.extend(data)
        cmd.append(sum(cmd) & 0xFF)
        tx_buff = (ctypes.c_char * len(cmd))(*cmd)
        rx_buff = (ctypes.c_char * 9)()

        self.clear_buffer()

        n_to_write = ctypes.c_long(len(cmd))
        n_written = ctypes.c_long()
        si_status = self.dll_si_usb.SI_Write(self.__handle, ctypes.byref(tx_buff), n_to_write, ctypes.byref(n_written), 0)
        self.check_si_status(si_status)
        if n_to_write.value != n_written.value:
            raise ValueError('Error SI_Write: mismatch of bytes to write and bytes written.')

        n_bytes_in_queue = ctypes.c_ulong()
        queue_status = ctypes.c_ulong()
        for _ in range(100):
            si_status = self.dll_si_usb.SI_CheckRXQueue(self.__handle, ctypes.byref(n_bytes_in_queue), ctypes.byref(queue_status))
            self.check_si_status(si_status)
            #define SI_RX_NO_OVERRUN 0x00
            #define SI_RX_EMPTY 0x00
            #define SI_RX_OVERRUN 0x01
            #define SI_RX_READY 0x02
            if queue_status.value == 2:
                break
            else:
                time.sleep(0.001)
        else:
            raise ValueError('Wait for SI_RX_READY timeout.')

        n_to_read = ctypes.c_ulong(len(rx_buff))
        n_read = ctypes.c_long()
        si_status = self.dll_si_usb.SI_Read(self.__handle, rx_buff, n_to_read, ctypes.byref(n_read), 0)
        self.check_si_status(si_status)
        if n_to_read.value != n_read.value:
            raise ValueError('Error SI_Read: mismatch of bytes to read and bytes read.')
        if rx_buff[7][0] != 0xE0:
            raise ValueError('Error device response: check ACK failed.')

        return n_written