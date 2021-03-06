from ._VisaInstrument import VisaInstrument
from ..instrument_types import TypeOSA
import time
from ..constants import LIGHT_SPEED


class ModelAQ6370(VisaInstrument, TypeOSA):
    model = "AQ6370"
    brand = "Yokogawa"
    details = {
        "Wavelength Range": "600 ~ 1700 nm",
        "Max. Resolution": "0.02 nm"
    }

    def __init__(self, resource_name, username="anonymous", password="empty", **kwargs):
        super(ModelAQ6370, self).__init__(resource_name, **kwargs)
        self._analysis_cat = ["WDM", "DFBLD", "FPLD", "SMSR"]
        self._analysis_setting_map = {
            "WDM": ["TH", "MDIFF", "DMASK", "NALGO", "NAREA", "MAREA", "FALGO", "NBW"],
            "DFBLD": {
                "SWIDTH": ["ALGO", "TH", "TH2", "K", "MFIT", "MDIFF"],
                "SMSR": ["SMODE", "SMASK", "MDIFF"],
                "RMS": ["ALGO", "TH", "K", "MDIFF"],
                "POWER": ["SPAN"],
                "OSNR": ["MDIFF", "NALGO", "NAREA", "MAREA", "FALGO", "NBW", "SPOWER", "IRANGE"],
            },
            "FPLD": {
                "SWIDTH": ["ALGO", "TH", "TH2", "K", "MFIT", "MDIFF"],
                "MWAVE": ["ALGO", "TH", "TH2", "K", "MFIT", "MDIFF"],
                "TPOWER": ["OFFSET"],
                "MNUMBER": ["ALGO", "TH", "TH2", "K", "MFIT", "MDIFF"],
            },
            "SMSR": ["MASK", "MODE"]
        }
        self._setup_map = ["BWIDTH:RES"]
        # init LAN if connection method is TCPIP
        if self.resource_name.upper().startswith('TCPIP'):
            self.open_lan_port(username, password)

    # param encapsulation
    # Method
    def open_lan_port(self, user="anonymous", password="empty"):
        usr_rsp = self.query('OPEN "%s"' % user)
        if usr_rsp.strip() == "AUTHENTICATE CRAM-MD5.":
            psw_rsp = self.query(password)
            if psw_rsp.strip() == "ready":
                return
        raise PermissionError("Uncorrect LAN username or password for %s" % self.model)

    def close(self):
        if self.resource_name.upper().startswith('TCPIP'):
            self.command('CLOSE')
        VisaInstrument.close(self)

    def sweep(self, mode="REPEAT"):
        """
        Set OSA sweep mode. mode = "AUTO"|"REPEAT"|"SINGLE"|"STOP"
        :param mode: (str) "AUTO"|"REPEAT"|"SINGLE"|"STOP"
        """
        selection = ["AUTO", "REPEAT", "SINGLE", "STOP"]
        if mode not in selection:
            raise ValueError('Invalid seeep mode: %r' % mode)
        if mode != "STOP":
            return self.command(':INIT:SMOD '+mode+';:INIT')
        else:
            return self.command(':ABOR')

    def set_auto_zero(self, is_on):
        """
        Enable or disable auto zero
        """
        if not isinstance(is_on, bool):
            raise TypeError('Param is_on should be bool')
        if is_on:
            flag = 'ON'
        else:
            flag = 'OFF'
        return self.command(":CAL:ZERO %s" % flag)

    def zero_once(self):
        """
        perform zeroing once
        """
        return self.command(":CAL:ZERO ONCE")

    def auto_analysis(self, enable):
        """
        enable/disable auto analysis
        :param enable: (bool) enable/disable auto analysis
        """
        return self.command(":CALC:AUTO "+str(int(enable)))

    def set_analysis_cat(self, item):
        """
        Set OSA analysis item. Available item depends on specific instrument.
        item = "WDM"|"DFBLD"|"FPLD"|"SMSR"
        :param item: (str) analysis item
        """
        if item not in self._analysis_cat:
            raise ValueError('Invalid analysis cat: %r' % item)
        return self.command(":CALC:CAT " + item)

    def get_analysis_cat(self):
        """
        Get the current analysis item.
        :return: (str) analysis item
        """
        cat_dict = {11: "WDM", 5: "DFBLD", 6: "FPLD"}
        cat_str = self.query(":CALC:CAT?")
        cat = cat_dict[int(cat_str)]
        return cat

    def analysis_setting(self, cat, param, value, subcat=None):
        """
        Analysis setting. param and value depends on specific instrument.
        :param cat: (str) setting category
        :param subcat: (str) setting sub category if there is one
        :param param: (str) setting item
        :param value: (str) setting value
        """
        if cat not in self._analysis_cat:
            raise ValueError('Invalid analysis category: %r' % cat)
        if subcat:
            if subcat not in tuple(self._analysis_setting_map[cat].keys()):
                raise ValueError('Invalid subcat: %r' % subcat)
            if param not in self._analysis_setting_map[cat][subcat]:
                raise ValueError('Invalid param name: %r' % param)
            route_str = " %s,%s," % (subcat, param)
        else:
            if param not in self._analysis_setting_map[cat]:
                raise ValueError('Invalid param name: %r' % param)
            route_str = ":%s " % param
        value = str(value)
        cmd_str = ":CALC:PAR:%s%s%s" % (cat, route_str, value)
        return self.command(cmd_str)

    def get_analysis_setting(self, cat, param, subcat=None):
        if cat not in self._analysis_cat:
            raise ValueError('Invalid analysis category: %r' % cat)
        if subcat:
            if subcat not in tuple(self._analysis_setting_map[cat].keys()):
                raise ValueError('Invalid subcat: %r' % subcat)
            if param not in self._analysis_setting_map[cat][subcat]:
                raise ValueError('Invalid param name: %r' % param)
            route_str = "? %s,%s" % (subcat, param)
        else:
            if param not in self._analysis_setting_map[cat]:
                raise ValueError('Invalid param name: %r' % param)
            route_str = ":%s?" % param
        cmd_str = ":CALC:PAR:%s%s" % (cat, route_str)
        return self.query(cmd_str)

    def get_analysis_setting_map(self):
        """
        Get setting map for all analysis categories.
        :return: (dict) analysis setting map
        """
        return self._analysis_setting_map

    def get_analysis_data(self):
        """
        Get data of current analysis item.
        :return: (str) data of current analysis item
        """
        return self.query(':CALC:DATA?')

    def set_center(self, value, unit):
        """
        Set center wavelength/frequency
        :param value: (float|int) center value
        :param unit: (str) unit
        """
        if not isinstance(value, (float, int)):
            raise TypeError('Center value should be number')
        if unit.upper() not in ['NM', 'THZ']:
            raise ValueError('Invalid center unit: %r. Should be NM or THZ' % unit)
        if unit.upper() == 'NM':
            return self.command(":SENS:WAV:CENT " + str(value) + 'NM')
        if unit.upper() == 'THZ':
            return self.command(":SENS:WAV:CENT " + str(value) + 'THZ')

    def set_wavelength(self, value):
        return self.set_center(value, 'NM')

    def set_frequency(self, value):
        return self.set_center(value, 'THZ')

    def get_center(self):
        """
        Get center wavelength setting
        :return: (float) center wavelength in nm
        """
        return float(self.query(":SENS:WAV:CENT?")) * 10**9
    
    def get_wavelength(self):
        return self.get_center()

    def get_frequency(self):
        return LIGHT_SPEED/self.get_wavelength()
    
    def set_marker_active_state(self, num, is_active):
        if not isinstance(num, int):
            raise TypeError('Marker index number should be int')
        if not 0 <= num <= 4:
            raise ValueError('Invalid marker index num: %r' % num)
        if not isinstance(is_active, bool):
            raise TypeError('Param is_active should be bool.')
        return self.command(':CALCULATE:MARKER:STATE %d,%d' % (num, int(is_active)))
# TODO
    def set_marker_x(self, num, value, unit):
        """
        set marker x
        unit: NM|THZ
        """
        if not isinstance(num, int):
            raise TypeError('Marker num should be int')
        if not 1 <= num <= 4:
            raise ValueError('Marker num sould be 1|2|3|4')
        if not isinstance(value, (int, float)):
            raise TypeError('Marker value should be number')
        if not unit in ['NM', 'THZ']:
            raise ValueError('Invalid unit: %r' % unit)
        return self.command(':CALCULATE:MARKER:X %d,%.3f%s' % (num, value, unit))

    def get_marker_x(self, num):
        """
        get marker x
        unit: Advanced marker position
        """
        if not isinstance(num, int):
            raise TypeError('Marker num should be int')
        if not 1 <= num <= 4:
            raise ValueError('Marker num sould be 1|2|3|4')
        return float(self.query(':CALCULATE:MARKER:X? %d') % num)

    def get_marker_y(self, num):
        """
        get marker y level
        """
        if not isinstance(num, int):
            raise TypeError('Marker num should be int')
        if not 1 <= num <= 4:
            raise ValueError('Marker num sould be 1|2|3|4')
        return float(self.query(':CALCULATE:MARKER:Y? %d' % num))

    def set_peak_to_center(self):
        """
        Set peak wavelength to center.
        """
        return self.command(':CALC:MARK:MAX:SCEN')

    def set_span(self, value, unit="NM"):
        """
        Set span wavelength/frequency
        :param value: (float|int) span value
        :param unit: (str) unit
        """
        if not isinstance(value, (float, int)):
            raise TypeError('Span value should be number')
        cmd = ':SENS:WAV:SPAN ' + str(value) + unit
        return self.command(cmd)

    def set_start_stop_wavelength(self, start, stop):
        """
        Set start-stop wavelength.
        :param start: (float|int) start wavelength in nm
        :param stop: (float|int) stop wavelength in nm
        """
        for i in start, stop:
            if not isinstance(i, (float, int)):
                raise TypeError('Param start and stop should be number')
        if not 0 < start < stop:
            raise ValueError('Invalid start and stop value. Start and stop should be positive number, and start < stop')
        return self.command(':SENS:WAV:STAR %.2fNM;:SENS:WAV:STOP %.2fNM' % (start, stop))

    def set_start_stop_frequency(self, start, stop):
        """
        Set start-stop frequency.
        :param start: (float|int) start frequency in THz
        :param stop: (float|int) stop frequency in THz
        """
        for i in start, stop:
            if not isinstance(i, (float, int)):
                raise TypeError('Param start and stop should be number')
        if not 0 < stop < start:
            raise ValueError('Invalid start and stop value. Start and stop should be positive number, and stop < start')
        return self.command(':SENS:WAV:STAR %fTHZ;:SENS:WAV:STOP %fTHZ' % (start, stop))

    def set_ref_level(self, value, unit):
        """
        Set reference level.
        :param value: (float|int) reference level value
        :param unit: (str) unit = "DBM"|"MW
        """
        if not isinstance(value, (float, int)):
            raise TypeError('Parameter value should be number')
        if unit not in ['DBM', 'MW', 'UM', 'NW']:
            raise ValueError('Invalid unit: %r' % unit)
        return self.command(":DISPLAY:TRACE:Y1:RLEVEL %f%s" % (value, unit))

    def set_peak_to_ref(self):
        """
        Set peak level to reference level
        """
        return self.command(':CALC:MARK:MAX:SRL')

    def set_auto_ref_level(self, is_on):
        """
        Enable/Disable auto peak -> ref level
        """
        
        return self.command(':CALC:MARK:MAX:SRL:AUTO %s' % 'ON' if is_on else 'OFF')

    def setup(self, param, value):
        """
        Set setup settings.
        :param param: (str) param
        :param value: (str) setting value
        """
        if not isinstance(param, str):
            raise TypeError('param should be str')
        if not isinstance(value, str):
            raise TypeError('value should be str')
        return self.command(':SENS:%s %s' % (param, value))

    def get_setup(self, param):
        return self.query(':SENS:%s?' % param)

    def format_data(self, cat, data):
        """
        Format data into dict, depends on calculate category (Anasis Category)
        :param cat: (str) "DFB"|"FP"|"WDM"
        :param data: (str) data retruned by method: get_analysis_data
        :return: (dict) a dict of test_item=>value
        """
        if cat not in self._analysis_cat:
            raise ValueError('Invalid cat: %r' % cat)
        data_list = data.split(',')
        r_data = None
        if cat == 'DFBLD':
            r_data = {
                "spec_wd": data_list[0],
                "peak_wl": data_list[1],
                "peak_lvl": data_list[2],
                "mode_ofst": data_list[3],
                "smsr": data_list[4]
            }
        elif cat == 'FPLD':
            r_data = {
                "spec_wd": data_list[0],
                "peak_wl": data_list[1],
                "peak_lvl": data_list[2],
                "center_wl": data_list[3],
                "total_pow": data_list[4],
                "mode_num": data_list[5]
            }
        elif cat == 'WDM':
            #  <display type> = ABSolute|0, RELative|1, MDRift|2, GDRift|3
            d_type = int(self.query(':CALC:PAR:WDM:DTYP?'))
            # 0 = OFFSET, 1 = SPACING
            relation = int(self.query(':CALC:PAR:WDM:REL?'))
            if d_type == 0:
                if relation == 0:
                    r_data = {
                        "ch_num": data_list[0],
                        "center_wl": data_list[1],
                        "peak_lvl": data_list[2],
                        "offset_wl": data_list[3],
                        "offset_lvl": data_list[4],
                        "noise": data_list[5],
                        "snr": data_list[6]
                    }
                elif relation == 1:
                    r_data = {
                        "ch_num": data_list[0],
                        "center_wl": data_list[1],
                        "peak_lvl": data_list[2],
                        "spacing": data_list[3],
                        "lvl_diff": data_list[4],
                        "noise": data_list[5],
                        "snr": data_list[6]
                    }
            elif d_type == 1:
                r_data = {
                    "ch_num": data_list[0],
                    "grid_wl": data_list[1],
                    "center_wl": data_list[2],
                    "rel_wl": data_list[3],
                    "peak_lvl": data_list[4],
                    "noise": data_list[5],
                    "snr": data_list[6]
                }
            elif d_type == 2:
                r_data = {
                    "ch_num": data_list[0],
                    "grid_wl": data_list[1],
                    "center_wl": data_list[2],
                    "wl_diff_max": data_list[3],
                    "wl_diff_min": data_list[4],
                    "ref_lvl": data_list[5],
                    "peak_lvl": data_list[6],
                    "lvl_diff_max": data_list[7],
                    "lvl_diff_min": data_list[8]
                }
            elif d_type == 3:
                r_data = {
                    "ch_num": data_list[0],
                    "ref_wl": data_list[1],
                    "center_wl": data_list[2],
                    "wl_diff_max": data_list[3],
                    "wl_diff_min": data_list[4],
                    "ref_lvl": data_list[5],
                    "peak_lvl": data_list[6],
                    "lvl_diff_max": data_list[7],
                    "lvl_diff_min": data_list[8]
                }
        return r_data

    def clear_all_markers(self):
        """
        """
        return self.command(':CALCULATE:MARKER:AOFF')

    def set_active_trace(self, trace_name):
        if trace_name not in ['TRA', 'TRB', 'TRC', 'TRD', 'TRE', 'TRF', 'TRG']:
            raise ValueError('Invalid trace_name: %r' % trace_name)
        return self.command(':TRAC:ACT %s' % trace_name)

    def set_trace_attribute(self, trace_name, attr):
        if trace_name not in ['TRA', 'TRB', 'TRC', 'TRD', 'TRE', 'TRF', 'TRG']:
            raise ValueError('Invalid trace_name: %r' % trace_name)
        if attr not in ['WRIT', 'FIX', 'MAX', 'MIN', 'RAVG', 'CALC']:
            raise ValueError('Invalid attr: %r' % attr)
        return self.command(':TRAC:ATTR:%s %s' % (trace_name, attr))

    def set_trace_display(self, trace_name, state):
        if trace_name not in ['TRA', 'TRB', 'TRC', 'TRD', 'TRE', 'TRF', 'TRG']:
            raise ValueError('Invalid trace_name: %r' % trace_name)
        if not isinstance(state, bool):
            raise TypeError('Parameter state should be bool')
        state_str = 'ON' if state else 'OFF'
        return self.command(':TRAC:STAT:%s %s' % (trace_name, state_str))

    def clear_trace(self, trace_name):
        if trace_name not in ['TRA', 'TRB', 'TRC', 'TRD', 'TRE', 'TRF', 'TRG']:
            raise ValueError('Invalid trace_name: %r' % trace_name)
        return self.command(':TRAC:DEL %s' % trace_name)

    def clear_all_traces(self):
        return self.command(':TRAC:DEL:ALL')

    def get_trace_data_x(self, trace_name):
        if trace_name not in ['TRA', 'TRB', 'TRC', 'TRD', 'TRE', 'TRF', 'TRG']:
            raise ValueError('Invalid trace_name: %r' % trace_name)
        result_str = self.query(':TRACE:X? %s' % trace_name)
        result_list = [float(i) for i in result_str.split(',')]
        return result_list

    def get_trace_data_y(self, trace_name):
        if trace_name not in ['TRA', 'TRB', 'TRC', 'TRD', 'TRE', 'TRF', 'TRG']:
            raise ValueError('Invalid trace_name: %r' % trace_name)
        result_str = self.query(':TRACE:Y? %s' % trace_name)
        result_list = [float(i) for i in result_str.split(',')]
        return result_list

    def capture_screen(self):
        """
        return: bytes
        """
        # create a unique name with nearly no chance to conflict
        temp_filename = 'tmp-{timestamp:X}'.format(timestamp=int(time.time()*10**6))
        # save image to internal memory
        self.command(':MMEMORY:STORE:GRAPHICS COLOR,BMP,"{filename}",INTERNAL'.format(filename=temp_filename))
        self.opc
        # save data to PC
        bin_data = self.query(':MMEMORY:DATA? "{filename}.BMP",internal'.format(filename=temp_filename), bin=True)
        bytes_data = bytes(bin_data)
        # delete temp file from internal memory
        self.command(':MMEMORY:DELETE "{filename}.BMP",internal'.format(filename=temp_filename))
        return bytes_data

    def save_screen(self, filepath):
        data = self.capture_screen()
        with open(filepath, 'wb') as f:
            f.write(data)