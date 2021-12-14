from ._BaseInstrument import BaseInstrument
from ._VisaInstrument import VisaInstrument
from ..instrument_types import TypeSW
from ..constants import LIGHT_SPEED
import time


class ModelAT5524(VisaInstrument, TypeSW):

    '''
    AT5524 is 2*4 optical switch, INPUT/OUTPUT is always A/B, 4 option channels: [1, 2, 3, 4] 
    '''
    
    model = "AT5524"
    brand = "Applent"

    def __init__(self, resource_name, write_termination="\n", read_termination="\n", **kwargs):
        super(ModelAT5524, self).__init__(resource_name, write_termination=write_termination, read_termination=read_termination, **kwargs)

    
    def get_channel(self):
        
        return int(self.query('SW?'))

    def set_channel(self, channel):
        if channel in range(1, 5):
            self.command('SW {ch}'.format(ch=channel))
            time.sleep(0.5)
        else:
            raise ValueError('Please choose channel 1~4!')

        if self.get_channel() != channel:
            raise ValueError('Set switch channel failed.')