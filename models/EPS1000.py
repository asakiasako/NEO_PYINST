from ._BaseInstrument import BaseInstrument
from ..instrument_types import TypePOLC
from ..constants import LIGHT_SPEED
import math
import time
import ftd2xx as ftd
import ctypes


class ModelEPS1000(BaseInstrument, TypePOLC):
    model = "EPS1000"
    brand = "Novoptel"
    details = {
        "Wavelength Range": "1510.3-1639.1 nm",
        "Frequency Range": "182.9-198.5 THz",
        "Insertion loss": "1.5-3 dB",
        "Peaked Rate": "0-20,000,000 rad/s",
        "Rayleigh Rate": "0-10,000,000 rad/s"
    }

    def __init__(self, resource_name:str, timeout=3, **kwargs):
        super(ModelEPS1000, self).__init__(resource_name)
        self._min_wl = 1510.3
        self._max_wl = 1639.1
        self._min_freq = math.floor(LIGHT_SPEED*1000/self._max_wl)/1000 + 0.001
        self._max_freq = math.floor(LIGHT_SPEED*1000/self._min_wl)/1000
        self.__baudrate = 230400
        self.__resource_name = resource_name
        self.__device_num = None
        self.__device = None

        device_list = ftd.listDevices()

        for i in range(len(device_list)):
            desc = ftd.getDeviceInfoDetail(i)["description"].decode()
            if desc.startswith('EPS1000'):
                sn = desc.split()[-1]
            else:
                continue
            if resource_name.endswith(sn):
                self.__device_num = i
                break
        else:
            raise ValueError('Device not found: {model} | S/N:{sn}'.format(model=self.model, sn=resource_name))        

        self.__device = ftd.open(self.__device_num)
        self.__device.setBaudRate(self.__baudrate)
        self.__device.setDataCharacteristics(8, 0, 0)
        self.__device.setTimeouts(round(timeout*1000), round(timeout*1000))
        self.__connected = True
        
    @property
    def resource_name(self):
        return self.__resource_name

    def close(self):
        self.__device.close()
        self.__connected = False

    def check_connection(self):
        return self.__connected

    def write_register(self, addr, data):
        if not self.__connected:
            raise ValueError('Device is closed. Please connect first.')
        time.sleep(0.01)
        write_str = 'W' + '{:03X}'.format(addr) + '{:04X}'.format(data) + chr(13)
        write_str_c = ctypes.create_string_buffer(write_str.encode('utf-8'), 9)
        self.__device.write(write_str_c)

    def read_register(self, addr):
        if not self.__connected:
            raise ValueError('Device is closed. Please connect first.')
        self.__device.purge()  # clear buffer
        time.sleep(0.01)

        # send request
        read_request = 'R' + '{:03X}'.format(addr) + '0000' + chr(13)
        read_request_c = ctypes.create_string_buffer(read_request.encode('utf-8'), 9)
        self.__device.write(read_request_c)

        # wait response
        bytesavailable=0
        tries=0
        while bytesavailable<5 and tries<1000:
            bytesavailable=self.__device.getQueueStatus()
            tries += 1
            time.sleep(0.001)

        # get responce
        res = self.__device.read(bytesavailable)

        # return responce as integer
        if bytesavailable>4:
            value = int(res.decode("utf-8"),16)
        else:
            raise ValueError('Invalid response from ')

        return value

    def set_qwp(self, qwp_n , direction , speed):
        """
        qwp_n = 0, 1, 2, 3, 4, 5
        direction = 0(Disabled), 1(Forward), -1(Backward)
        speed = (rad/s)
        """
        control_reg_addr = qwp_n + 1
        speed_reg_addr0 = qwp_n*2+11
        speed_reg_addr1 = qwp_n*2+12
        
        if direction == 0:
            self.write_register(control_reg_addr, 0)
        elif direction == 1:
            self.write_register(control_reg_addr, 1)
        elif direction == -1:
            self.write_register(control_reg_addr, 3)
        else:
            raise ValueError('Invalid value for direction: {}. Options: 0(Disabled), 1(Forward), -1(Backward)'.format(direction))
        
        speed_msb = int((speed*100)/(2**16)) & 0xffff
        speed_lsb = int((speed*100)) & 0xffff
        
        self.write_register(speed_reg_addr0, speed_lsb)
        self.write_register(speed_reg_addr1, speed_msb)
        
    def set_hwp(self, direction , speed):
    
        """
        direction = 0(Disabled), 1(Forward), -1(Backward)
        speed = (krad/s)
        """
        
        control_reg_addr = 0
        speed_reg_addr0 = 9
        speed_reg_addr1 = 10

        if direction == 0:
            self.write_register(control_reg_addr, 0)
        elif direction == 1:
            self.write_register(control_reg_addr, 1)
        elif direction == -1:
            self.write_register(control_reg_addr, 3)
        else:
            raise ValueError('Invalid value for direction: {}. Options: 0(Disabled), 1(Forward), -1(Backward)'.format(direction))

        speed_msb = int((speed*100)/(2**16)) & 0xffff
        speed_lsb = int((speed*100)) & 0xffff
        
        self.write_register(speed_reg_addr0, speed_lsb)
        self.write_register(speed_reg_addr1, speed_msb)

    def get_frequency(self):
        value = int(self.read_register(addr=25))
        freq = (value + 1828)/10
        return freq

    def set_frequency(self, frequency):
        value = round(frequency*10 - 1828)
        self.write_register(addr=25, data=value)
        time.sleep(0.1)

    def get_wavelength(self):
        freq = self.get_frequency()
        wl = round(LIGHT_SPEED/freq, 6)
        return wl

    def set_wavelength(self, wavelength):
        freq = round(LIGHT_SPEED/wavelength, 6)
        self.set_frequency(freq)

    def start_scrambling(self, mode, speed):

        '''
        speed unit: rad/s
        when mode is 'Peaked', the max speed is 2000000rad/s
        when mode is  'Rayleigh', the max speed is 1000000rad/s
        when mode is 'Marvell', the unit is rad/s
        '''
        if mode == 'Peaked':
            if 0 <= speed <= 20000000:
                speed_10 = round(speed/10)
                lsb = speed_10&0xFFFF
                msb = (2<<14)|(speed_10>>16)
                self.write_register(addr=23, data=lsb)
                self.write_register(addr=24, data=msb)
            else:
                raise ValueError("Speed is out of range, the max speed of 'Peaked' mode is 2000000rad/s")

        elif mode == 'Rayleigh':
            if 0 <= speed <= 10000000:
                speed_10 = round(speed/10)
                lsb = speed_10&0xFFFF
                msb = (3<<14)|(speed_10>>16)
                self.write_register(addr=23, data=lsb)
                self.write_register(addr=24, data=msb)
            else:
                raise ValueError("Speed is out of range, the max speed of 'Rayleigh' mode is 1000000rad/s")

        elif mode == 'Marvell':
            self.stop_scrambling()
            self.write_register(addr=23, data=0)
            self.write_register(addr=24, data=0)
            time.sleep(0.1)

            qwp_speed = speed / 6
            offset = 0.02
            self.set_qwp(qwp_n=0, direction=1, speed=qwp_speed*(1.0+offset))
            self.set_qwp(qwp_n=1, direction=-1, speed=qwp_speed*(1.0-offset))
            self.set_qwp(qwp_n=2, direction=1, speed=qwp_speed*(1.0+offset))
            self.set_hwp(direction=-1, speed=0.01) # -1 is backward. 0.01 could be just rad/s
            self.set_qwp(qwp_n=3, direction=-1, speed=qwp_speed*(1.0-offset))
            self.set_qwp(qwp_n=4, direction=1, speed=qwp_speed*(1.0+offset))
            self.set_qwp(qwp_n=5, direction=-1, speed=qwp_speed*(1.0-offset))
            if qwp_speed < 10:
                self.set_hwp(direction=0, speed=0)

        else:
            raise ValueError("Invalid scrambling mode: {}".format(mode))

    def stop_scrambling(self):
        self.start_scrambling('Peaked', 0)

    def get_scrambling_params(self):
        value_reg24 = self.read_register(addr=24)
        value_reg23 = self.read_register(addr=23)
        mode_value = value_reg24 >> 14

        if mode_value == 3:
            mode = 'Rayleigh'
            speed = ((value_reg24 - int(0xC000))*2**16 + value_reg23)/100
        elif mode_value == 2:
            mode = 'Peaked'
            speed = ((value_reg24 - int(0x8000))*2**16 + value_reg23)/100
        else:
            mode = 'User'
            speed = None
        return mode, speed






            
    

