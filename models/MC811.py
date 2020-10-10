from ._BaseInstrument import BaseInstrument
from ..instrument_types import TypeTS
from ..constants import TemperatureUnit
import serial

class ModelMC811(BaseInstrument, TypeTS):
    model = "MC-811"
    brand = "GWS"

    def __init__(self, resource_name, dev_id=0, baud_rate=19200, **kwargs):
        super(ModelMC811, self).__init__()
        self._ts_type = 'Chamber'
        self.__serial = serial.Serial(port=resource_name, baudrate=baud_rate, timeout=0.5)
        self.__serial.reset_input_buffer()
        self.__resource_name = resource_name
        self.__termination = '\r\n'

    @property
    def resource_name(self):
        return self.__resource_name

    def write_cmd(self, cmd):
        full_cmd = '{cmd}{termination}'.format(cmd=cmd, termination=self.__termination)
        self.__serial.reset_input_buffer()
        self.__serial.write(full_cmd.encode())

    def read_reply(self):
        r = ''
        while True:
            append = self.__serial.read(1).decode()
            if not append:
                raise TimeoutError
            r += append
            if r.endswith('\r\n'):
                break
        r = r[:-2]
        return r

    def close(self):
        self.__serial.close()

    def check_connection(self):
        try:
            self.get_target_temp()
            return True
        except Exception:
            return False

    def set_target_temp(self, value):
        """
        Set the target Temperature.
        :param value: <float|int> target temperature value
        """
        value = round(value, 1)  # this chamber supports 1 decimal place
        cmd = 'TEMP, S{value:.1f}'.format(value=value)
        self.write_cmd(cmd)

    def get_target_temp(self):
        """
        Get the target Temperature
        :return: <float> target temperature value
        """
        cmd = 'TEMP?'
        self.write_cmd(cmd)
        r = self.read_reply()
        value = float(r.split(',')[1])
        return value

    def get_current_temp(self):
        """
        Get the current measured temperature
        :return: <float> current measured temperature
        """
        cmd = 'TEMP?'
        self.write_cmd(cmd)
        r = self.read_reply()
        value = float(r.split(',')[0])
        return value

    def set_unit(self, unit):
        """
        Set temperature unit
        :param unit: int, value of <TemperatureUnit> unit
        """
        TemperatureUnit(unit)
        if unit == TemperatureUnit.C.value:
            return
        else:
            raise ValueError('Chamber temperature unit is fixed as "C".')

    def get_unit(self):
        """
        Get temperature unit
        :return: int, value of <TemperatureUnit> unit
        """
        return TemperatureUnit.C.value