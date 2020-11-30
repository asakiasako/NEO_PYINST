from ._VisaInstrument import VisaInstrument


class ModelVSA89600(VisaInstrument):
    """
    This is the base model of Keysight VSA89600 software
    """

    def __init__(self, resource_name, encoding='latin1', **kwargs):
        super(ModelVSA89600, self).__init__(resource_name, encoding=encoding, **kwargs)
        self.__resource_name = resource_name

    # param encapsulation
    @property
    def resource_name(self):
        return self.__resource_name

    # Methods
    def run(self):
        """
        Run OMA
        """
        self.command(':INIT:RES')
        
    def stop(self):
        """
        Pause OMA
        """
        self.command(':INIT:ABOR')
    
    def get_trace_item_names(self, trace):
        """
        Get all the test item names for the specified trace.
        :param trace: (int) index of trace, 1 based from A. For example: A->1, E->5
        :return: (list of str) trace item names.
        """
        if not isinstance(trace, int):
            raise TypeError('trace should be int')
        if not trace >= 1:
            raise ValueError('trace starts from 1')
        item_str = self.query(':TRACe%d:DATA:TABLe:NAME?' % trace)
        item_list = item_str.split(',')
        item_list = list(map(lambda x: x.strip('"'), item_list))
        return item_list

    def get_trace_values(self, trace):
        """
        Get all the test values for the specified trace.
        :param trace: (int) index of trace, 1 based from A. For example: A->1, E->5
        :return: (list of float) trace item values.
        """
        if not isinstance(trace, int):
            raise TypeError('trace should be int')
        if not trace >= 1:
            raise ValueError('trace starts from 1')
        value_str = self.query(':TRACe%d:DATA:TABLe?' % trace)
        value_list = value_str.split(',')
        for i in range(len(value_list)):
            try:
                value_list[i] = float(value_list[i])
            except Exception:
                pass
        return value_list

    def get_trace_units(self, trace):
        """
        Get all the units for the specified trace.
        :param trace: (int) index of trace, 1 based from A. For example: A->1, E->5
        :return: (list of str) units of item values.
        """
        if not isinstance(trace, int):
            raise TypeError('trace should be int')
        if not trace >= 1:
            raise ValueError('trace starts from 1')
        unit_str = self.query(':TRACe%d:DATA:TABLe:UNIT?' % trace)
        unit_list = unit_str.split(',')        
        unit_list = list(map(lambda x: x.strip('"'), unit_list))
        return unit_list

    def get_trace_data(self, trace):
        """
        Get a formatted data include test item_names, values, and units.
        :param trace: (int) index of trace, 1 based from A. For example: A->1, E->5
        :return: (dict) { str:item1: (float:value, str:unit), ...}
        """
        names = self.get_trace_item_names(trace)
        values = self.get_trace_values(trace)
        units = self.get_trace_units(trace)
        ilen = len(names)
        if not ilen == len(values) == len(units):
            raise IndexError('Mismatch numbers for names, values and units')
        res = {}
        try:
            for i in range(ilen):
                res[names[i]] = (values[i], units[i])
        except Exception:
            raise
        return res

    def get_custom_demod_measurement_filter(self):
        cmd = ':CDEMod:FILTer?'
        rpl = self.query(cmd)
        return rpl.strip().strip('"')

    def set_custom_demod_measurement_filter(self, _filter):
        FILTERS = { 'None', 'Rectangular', 'RootRaisedCosine', 'Gaussian', 'LowPass' }
        if _filter not in FILTERS:
            raise ValueError('Invalid filter type for Custom Demod Measurement Filter: {filter}'.format(filter=_filter))
        cmd = ':CDEM:FILT "{filter}"'.format(filter=_filter)
        self.command(cmd)

    def get_custom_demod_reference_filter(self):
        cmd = ':CDEM:FILT:REF?'
        rpl = self.query(cmd)
        return rpl.strip().strip('"')

    def set_custom_demod_reference_filter(self, _filter):
        FILTERS = { "Rectangular", "RaisedCosine", "RootRaisedCosine", "Gaussian", "HalfSine" }
        if _filter not in FILTERS:
            raise ValueError('Invalid filter type for Custom Demod Measurement Filter: {filter}'.format(filter=_filter))
        cmd = ':CDEM:FILT:REF "{filter}"'.format(filter=_filter)
        self.command(cmd)

    def get_custom_demod_filter_abt(self):
        """
        Gets the α (alpha) or BT (bandwidth time product) parameter for measurement and reference filters
        """
        cmd = ':CDEMod:FILTer:ABT?'
        rpl = self.query(cmd)
        return float(rpl)

    def set_custom_demod_filter_abt(self, abt):
        """
        Sets the α (alpha) or BT (bandwidth time product) parameter for measurement and reference filters
        """
        if not isinstance(abt, (int, float)):
            raise TypeError('Invalid type for abt (alpha or BT parameter), should be a number.')
        cmd = ':CDEMod:FILTer:ABT {value:f}'.format(value=round(abt, 6))
        self.command(cmd)

    def get_custom_demod_equalization_state(self):
        """
        Gets a value indicating whether the equalization filter is enabled. 
        """
        cmd = ':CDEMod:COMPensate:EQUalize?'
        rpl = self.query(cmd)
        return bool(int(rpl))

    def set_custom_demod_equalization_state(self, enable):
        """
        Sets a value indicating whether the equalization filter is enabled. 
        """
        if not isinstance(enable, bool):
            raise TypeError('Parameter enable should be bool.')
        state = int(enable)
        cmd = ':CDEMod:COMPensate:EQUalize {state:d}'.format(state=state)
        self.command(cmd)

    def get_custom_demod_equalization_length(self):
        cmd = ':CDEMod:COMPensate:EQUalize:LENGth?'
        rpl = self.query(cmd)
        return int(rpl)

    def set_custom_demod_equalization_length(self, value):
        if not isinstance(value, int):
            raise TypeError('Custom Demod EQ length value should be int.')
        if not value >= 3:
            raise ValueError('Invalid EQ length: should >= 3')
        cmd = ':CDEMod:COMPensate:EQUalize:LENGth {value:d}'.format(value=value)
        self.command(cmd)
        
    def get_custom_demod_equalization_convergence(self):
        cmd = ':CDEMod:COMPensate:EQUalize:CONVergence?'
        rpl = self.query(cmd)
        return float(rpl)

    def set_custom_demod_equalization_convergence(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError('Custom Demod EQ Convergence value should be number.')
        if not 1E-8 <= value <= 1e-6:
            raise ValueError('Invalid value of EQ convergence: should between 1E-6 and 1E-8.')
        cmd = ':CDEMod:COMPensate:EQUalize:CONVergence {value:.4E}'.format(value=value)
        self.command(cmd)

    def get_custom_demod_equalizer_run_mode(self):
        """
        Gets the run mode of the Adaptive Equalizer.
        """
        cmd = ':CDEMod:COMPensate:EQUalize:MODE?'
        rpl = self.query(cmd)
        return rpl.strip().strip('"')

    def set_custom_demod_equalizer_run_mode(self, value):
        """
        Sets the run mode of the Adaptive Equalizer.
        """
        MODES = { "Run", "Hold" }
        if value not in MODES:
            raise ValueError('Invalid value for Custom Demod EQ run mode: {vlaue!r}'.format(value))
        cmd = ':CDEMod:COMPensate:EQUalize:MODE {value}'.format(value=value)
        self.command(cmd)

    def reset_custom_demod_equalizer(self):
        cmd = ':CDEMod:COMPensate:EQUalize:RESet'
        self.command(cmd)