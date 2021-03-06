from ._VSA89600 import ModelVSA89600
from ..instrument_types import TypeOMA
from ..constants import LIGHT_SPEED


class ModelVsaOMA(ModelVSA89600, TypeOMA):

    def __init__(self, resource_name, **kwargs):
        super(ModelVsaOMA, self).__init__(resource_name, **kwargs)

    def set_frequency(self, frequency):
        self.smart_setup(freq=frequency, pre_set_layout=False)

    def set_wavelength(self, wavelength):
        freq = LIGHT_SPEED/wavelength
        self.set_frequency(freq)

    def smart_setup(self, execute=True, freq=None, symbol_rate=None, fine_tune_symbol_rate=None, demodulation_format=None, polarization=None, pre_set_layout=None, compensate_cd=None, compensate_pmd=None):
        """
        execute: if execute after setup. if false, settings will be set, but no execution will be done.
        """
        if freq is not None:
            self.command(':OMA:SMartSEtup:CarrierFrequency:FRErequency {value}'.format(value=freq*10**12))
        if symbol_rate is not None:
            self.command(':OMA:SMartSEtup:SYMBRate {value}'.format(value=symbol_rate*10**9))
        if fine_tune_symbol_rate is not None:
            if not isinstance(fine_tune_symbol_rate, bool):
                raise TypeError('fine_tune_symbol_rate should be bool.')
            self.command(':OMA:SMartSEtup:FINetuneSymbolRate {enable:d}'.format(enable=fine_tune_symbol_rate))
        if demodulation_format is not None:
            FORMATS = [
                "Qam16", "Qam32", "Qam64", "Qam256", "Qpsk", 
                "DifferentialQpsk", "Pi4DifferentialQpsk", 
                "OffsetQpsk", "Bpsk", "Psk8", "Msk", "Msk2", 
                "Fsk2", "Fsk4", "DvbQam16", "DvbQam32", 
                "DvbQam64", "Vsb8", "Vsb16", "Edge", "Fsk8", 
                "Fsk16", "Qam128", "DifferentialPsk8", 
                "Qam512", "Qam1024", "Apsk16", "Apsk16Dvb", 
                "Apsk32", "Apsk32Dvb", "DvbQam128", 
                "DvbQam256", "Pi8DifferentialPsk8", "CpmFM", 
                "Star16Qam", "Star32Qam", "CustomApsk", 
                "ShapedOffsetQpsk"
            ]
            if demodulation_format not in FORMATS:
                raise ValueError('Invalid modulation demodulation format: %r' % demodulation_format)
            self.command(':OMA:SMartSEtup:FORMat "{format}"'.format(format=demodulation_format))
        if polarization is not None:
            POLARIZATIONS = ["Single", "Dual", "Auto"]
            if not polarization in POLARIZATIONS:
                raise ValueError('Invalid polarization: %r' % polarization)
            self.command(':OMA:SMartSEtup:POLarization "{pol}"'.format(pol=polarization))
        if pre_set_layout is not None:
            if not isinstance(pre_set_layout, bool):
                raise TypeError('pre_set_layout should be bool.')
            self.command(':OMA:SMartSEtup:PREsetLAyout {enable:d}'.format(enable=pre_set_layout))
        if compensate_cd is not None:
            compensate_cd = bool(compensate_cd)
            self.command(':OMA:SMartSEtup:COmpensateCD {:d}'.format(compensate_cd))
        if compensate_pmd is not None:
            compensate_pmd = bool(compensate_pmd)
            self.command(':OMA:SMartSEtup:COmpensatePMD {:d}'.format(compensate_pmd))
        if execute:
            self.command(':OMA:SMartSEtup:PERformProposedActions')

