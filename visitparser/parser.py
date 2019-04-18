"""Module to inspect JWST visit files.

Authors
-------
    Johannes Sahlmann
    Marshall Perrin


"""

from collections import OrderedDict
import copy
import re

from astropy.table import Table, join
import numpy as np


iswhitespace = lambda x: re.fullmatch("\s+", x) is not None


# set up regular expressions for parsing
rx_dict = {
    'template': re.compile(r'# (?P<apt_templates>.*)'),
}


def _parse_line(line, rx_dict):
    """Do a regex search against all defined regexes.

    Return the key and match result of the first matching regex.

    See https://www.vipinajayakumar.com/parsing-text-with-python/
    """
    for key, rx in rx_dict.items():
        match = rx.search(line)
        if match:
            return key, match

    # if there are no matches
    return None, None


# Some lightweight classes for parsed information
class Statement(object):
    """Capture visit file statement delimited by a semicolon."""
    def __init__(self, cmdstring, verbose=False):
        cmdparts = cmdstring.split(' ,')
        self.name = cmdparts[0]
        self.args = cmdparts[1:]
        try:
            self.scriptname = cmdparts[2]
        except IndexError:
            self.scriptname = 'NONE'

        if verbose:
            for part in cmdparts:
                print("   " + part)

    def __repr__(self):
        return ("<Statement {} >".format(self.name))


class Aux(Statement):
    """Capture statement identified by AUX keyword."""
    def __init__(self, cmdstring, verbose=False):
        super().__init__(cmdstring, verbose=verbose)
        for param in self.args:
            if '=' in param:
                key, value = param.split('=')
                try:
                    value = float(value)
                except:
                    pass
            self.__dict__[key] = value



class Dither(Statement):
    """Capture statement identified by DITHER keyword."""
    def __init__(self, cmdstring, verbose=False):
        super().__init__(cmdstring, verbose=verbose)
        self.id = self.args[0].split('=')[1]
        for param in self.args:
            if '=' in param:
                key, value = param.split('=')
                try:
                    value = float(value)
                except:
                    pass
            self.__dict__[key] = value


class Momentum(Statement):
    """Capture statement identified by MOMENTUM keyword."""
    def __init__(self, cmdstring, verbose=False):
        super().__init__(cmdstring, verbose=verbose)
        for param in self.args:
            if '=' in param:
                key, value = param.split('=')
                try:
                    value = float(value)
                except:
                    pass
            self.__dict__[key] = value


class SlewOrAct(Statement):
    """Capture statement identified by SLEW or ACT keyword."""
    def __init__(self, cmdstring, group=None, sequence=None, verbose=False):
        super().__init__(cmdstring, verbose=verbose)
        self.group = group
        self.sequence = sequence
        try:
            self.activity = int(self.args[0], base=16)  # note, these are base 16 hex numbers
        except ValueError as e:
            print('Activity number parsing raises ValueError:\n{}\nSetting to 99'.format(e))
            self.activity = 99

        for param in self.args[2:]:
            if '=' in param:
                key, value = param.split('=')
                try:
                    value = float(value)
                except:
                    pass
            self.__dict__[key] = value

    @property
    def gsa(self):
        "Group, sequence, activity"
        return "{:02d}{:1d}{:02d}".format(self.group, self.sequence, self.activity)


class VisitDescription(Statement):
    """Capture statement identified by VISIT keyword."""
    def __init__(self, cmdstring, verbose=False):
        super().__init__(cmdstring, verbose=verbose)
        self.id = self.args[0]
        for param in self.args[1:]:
            if '=' in param:
                key, value = param.split('=')
                try:
                    value = float(value)
                except:
                    pass
            self.__dict__[key] = value


class Activity(SlewOrAct):
    """Capture information related to activity."""
    def __init__(self, cmdstring, *args, **kwargs):
        super().__init__(cmdstring, *args, **kwargs)
        # self.scriptname = self.args[1]

    def __repr__(self):
        return ("Activity {}:  {}".format(self.gsa, self.describe()))

    def describe(self):
        if self.scriptname == 'NRCWFSCMAIN':
            description = """{s.scriptname}  {s.CONFIG} WFCGROUP={s.WFCGROUP}
        Readout={s.NGROUPS:.0f} groups, {s.NINTS:.0f} ints
        SW={s.FILTSHORTA}, LW={s.FILTLONGA}"""
        elif self.scriptname == 'NRCMAIN':
            description = """{s.scriptname}  {s.CONFIG}
        Readout={s.NGROUPS:.0f} groups, {s.NINTS:.0f} ints
        SW={s.FILTSHORTA}, LW={s.FILTLONGA}"""
        elif self.scriptname == 'NRCWFCPMAIN':
            mod = self.CONFIG[3]  # a or B
            description = "{s.scriptname}  {s.FILTSHORT" + mod + "}+{s.PUPILSHORT" + mod + \
                          "} Readout={s.NGROUPS:.0f} groups, {s.NINTS:.0f} ints"
        elif self.scriptname == 'SCSAMMAIN':
            description = """SCSAMMAIN  dx={s.DELTAX}, dy={s.DELTAY}, dpa={s.DELTAPA}"""
        elif self.scriptname == 'NRCSUBMAIN':
            description = """NRCSUBMAIN   subarray={s.SUBARRAY}"""
        else:
            description = """{s.scriptname}"""
        try:
            return description.format(s=self)
        except AttributeError as e:
            print('Activity {} raised AttributeError:\n{}'.format(self.scriptname, e))


class Guide(SlewOrAct):
    """Expand Guide statement."""
    def describe(self):
        if self.args[1] == 'FGSVERMAIN':
            return ("Verification")
        else:
            detnum = self.DETECTOR[-1]
            return """FGS{detnum}""".format(detnum=detnum, s=self)

    def __repr__(self):
        return ("Guide {}:  {}".format(self.gsa, self.describe()))


class Slew(SlewOrAct):
    """Expand statement identified by SLEW keyword."""
    def __repr__(self):
        return (
        "Slew  {}: for {} on GS at ({}, {}) with PA={}".format(self.gsa, 'N/A', self.GSRA,
                                                               self.GSDEC, self.GSPA))
        # "Slew  {}: for {} on GS at ({}, {}) with PA={}".format(self.gsa, self.GUIDEMODE, self.GSRA,
        #                                                        self.GSDEC, self.GSPA))


class Visit():
    """Class for JWST visit file information"""
    def __init__(self, templates, statements, groups):
        self.templates = templates
        self.groups = groups
        self.statements = statements

        # store non-exposure related information in class asstributes
        dithers = OrderedDict()
        for statement in self.statements:
            if statement.name == 'VISIT':
                self.id = statement.id
                self.visit_parameters = statement
            elif statement.name == 'MOMENTUM':
                self.momentum = statement
            elif statement.name == 'AUX':
                self.aux = statement
            elif statement.name == 'DITHER':
                dithers['{}'.format(statement.id)] = statement

        self.dithers = dithers

        # construct astropy table with basic content
        script_statements = []
        self.table = Table(names=('GROUP_ID', 'SEQ_ID', 'ACT_ID', 'GSA', 'TYPE', 'SCRIPT'),
                           dtype=(int, int, int, object, object, object))
        for group_id, group in self.groups.items():
            for seq_id, seq in group.items():
                for statement in seq:
                    self.table.add_row((np.int(group_id.split('_')[1]), np.int(seq_id.split('_')[1]),
                                        statement.activity, statement.gsa, statement.name, statement.scriptname))
                    script_statements.append(statement)
        for colname in 'TYPE SCRIPT GSA'.split():
            self.table[colname] = np.array(self.table[colname]).astype(str)
        self.table.meta['comments']=['{}'.format(self.id)]
        self.number_of_statements = len(self.table)
        self.script_statements = np.array(script_statements)

    def __repr__(self):
        return (
        "Visit  {}: {:>2} dithers, {:>2} groups, {:>3} observation statements. Uses {}".format(self.id, len(self.dithers),
                                                                                               len(self.groups), self.number_of_statements, self.templates))


    def overview_table(self, instrument=None):
        """Return an astropy table with specific information, one row per exposure/activity.

        Parameters
        ----------
        instrument : str
            JWST instrument name, case insensitive

        Returns
        -------
        table : astropy.table
            Table with additional information extracted from the statements.

        """

        table = copy.deepcopy(self.table)
        if instrument.lower() == 'niriss':
            remove_index = np.array([i for i, script in enumerate(self.table['SCRIPT']) if script[0:3] not in ['NIS', 'NRC']])
            table.remove_rows(remove_index)

            column_names = 'GSA OPMODE TARGTYPE DITHERID PATTERN NINTS NGROUPS PUPIL FILTER SUBARRAY'.split()
            instrument_table = Table(names=tuple(column_names), dtype=tuple([object]*10))
            for statement in self.script_statements:
                if statement.gsa in table['GSA']:
                    row = [statement.gsa]
                    for colname in instrument_table.colnames[1:]:
                        try:
                            value = str(getattr(statement, colname))
                        except AttributeError:
                            value = 'NONE'
                        row.append(value)
                    instrument_table.add_row(vals=row)
            for colname in instrument_table.colnames:
                instrument_table[colname] = np.array(instrument_table[colname]).astype(str)

            table = join(table, instrument_table, keys='GSA')

        return table




def parse_visit_file(filename, verbose=False):
    """Read and parse the visit file line-by-line.

    Parameters
    ----------
    filename : str
        Name fo file to parse
    verbose : bool
        verbosity

    Returns
    -------
    visit : Visit object
        Object containing all information extracted from the file.

    """
    with open(filename) as file:
        lines = file.readlines()
        key, match = _parse_line(lines[0], rx_dict)
        if key == 'template':
            apt_templates = match.group('apt_templates').split(',')

        # Simple parsing that ignores commands and newlines, but respects the fact that
        # OSS parameters are separated by the exact string " ," with the comma necessarily after whitespace.
        nocomments = [l.strip() for l in lines if not (l.startswith("#") or iswhitespace(l))]
        for i in range(len(nocomments)):
            if nocomments[i].startswith(','):
                nocomments[i] = ' ' + nocomments[i]

        merged = ''.join(nocomments)
        commands = merged.split(';')
        if verbose:
            print(commands)

        # Now iterate through the statements
        groups = OrderedDict()
        commands = np.array(commands)

        # process initial statements
        statements = []
        for index,cmd in enumerate(commands):
            if cmd == '':
                continue
            if verbose:
                print(cmd)
                print('*'*50)
            parsedcmd = Statement(cmd)
            if parsedcmd.name == 'GROUP':
                break
            elif parsedcmd.name == 'VISIT':
                parsedcmd = VisitDescription(cmd)
            elif parsedcmd.name == 'MOMENTUM':
                parsedcmd = Momentum(cmd)
            elif parsedcmd.name == 'AUX':
                parsedcmd = Aux(cmd)
            elif parsedcmd.name == 'DITHER':
                parsedcmd = Dither(cmd)
            statements.append(parsedcmd)

        # process groups and sequences
        for ii, cmd in enumerate(commands[index:]):
            if cmd == '':
                continue
            parsedcmd = Statement(cmd)
            if parsedcmd.name == 'GROUP':
                ct_group = int(parsedcmd.args[0].split()[0])
                groups['GROUP_{:02d}'.format(ct_group)] = OrderedDict()
                continue
            elif parsedcmd.name == 'SEQ':
                ct_seq = int(parsedcmd.args[0].split()[0])
                seq_statements = []
                groups['GROUP_{:02d}'.format(ct_group)]['SEQ_{:02d}'.format(ct_seq)] = seq_statements
                continue

            elif parsedcmd.name == 'SLEW':
                parsedcmd = Slew(cmd, group=ct_group, sequence=ct_seq)

            elif parsedcmd.name == 'ACT':
                if parsedcmd.args[1] == 'FGSMAIN' or parsedcmd.args[1] == 'FGSVERMAIN':
                    parsedcmd = Guide(cmd, group=ct_group, sequence=ct_seq)
                else:
                    parsedcmd = Activity(cmd, group=ct_group, sequence=ct_seq)

            seq_statements.append(parsedcmd)

    return Visit(apt_templates, statements, groups)


def crosscheck_wfsc_visit_file(filename):
    """

    TODO
    ----
        update Perrin's function to updated code.

    Parameters
    ----------
    filename

    Returns
    -------

    """
    statements, apt_template = parse_visit_file(filename)
    print("==WFSC crosscheck for file {}==".format(filename))
    print("From APT template: {}".format(apt_template))
    # Check slew statements
    slews = [s for s in statements if (isinstance(s, Slew) or isinstance(s, Guide))]
    # Check activity statements
    acts = [s for s in statements if isinstance(s, Activity)]
    is_wfsc_visit = any(['WFSC' in a.scriptname for a in acts])

    print("\nContains {} slew or guide statement(s):".format(len(slews)))
    for s in slews:
        print("   " + repr(s))
    print("\nContains {} activity statement(s):".format(len(acts)))
    act_by_num = dict()
    for s in acts:
        print("   " + repr(s))
        act_by_num[s.gsa] = s
    if is_wfsc_visit:
        aux = [s for s in statements if s.name == 'AUX']
        if len(aux) is 0:
            raise RuntimeError("WFSC VISIT BUT NO AUX STATEMENT FOUND!")
            # Check for presence of AUX statement
