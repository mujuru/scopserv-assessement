import sys, pprint
from types import ListType
import signal
import datetime
import requests


class AGI:
    def __init__(self, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self._got_sighup = False
        signal.signal(signal.SIGHUP, self._handle_sighup)  # handle SIGHUP
        self.stderr.write('ARGS: ')
        self.stderr.write(str(sys.argv))
        self.stderr.write('\n')
        self.env = {}
        self._get_agi_env()

    def _get_agi_env(self):
        while 1:
            line = self.stdin.readline().strip()
            self.stderr.write('ENV LINE: ')
            self.stderr.write(line)
            self.stderr.write('\n')
            if line == '':
                # blank line signals end
                break
            key, data = line.split(':')[0], ':'.join(line.split(':')[1:])
            key = key.strip()
            data = data.strip()
            if key != '':
                self.env[key] = data
        self.stderr.write('class AGI: self.env = ')
        self.stderr.write(pprint.pformat(self.env))
        self.stderr.write('\n')

    def execute(self, command, *args):
        try:
            self.send_command(command, *args)
            return self.get_result()
        except IOError as e:
            if e.errno == 32:
                # Broken Pipe
                raise AGISIGPIPEHangup("Received SIGPIPE")
            else:
                raise

    def send_command(self, command, *args):
        """Send a command to Asterisk"""
        command = command.strip()
        command = '%s %s' % (command, ' '.join(map(str, args)))
        command = command.strip()
        if command[-1] != '\n':
            command += '\n'
        self.stderr.write('    COMMAND: %s' % command)
        self.stdout.write(command)
        self.stdout.flush()

    def get_result(self):
        """Read the result of a command from Asterisk"""
        code = 0
        result = {'result': ('', '')}
        line = self.stdin.readline().strip()
        self.stderr.write('    RESULT_LINE: %s\n' % line)
        m = re_code.search(line)
        if m:
            code, response = m.groups()
            code = int(code)

        if code == 200:
            for key, value, data in re_kv.findall(response):
                result[key] = (value, data)

                # If user hangs up... we get 'hangup' in the data
                if data == 'hangup':
                    raise AGIResultHangup("User hungup during execution")

                if key == 'result' and value == '-1':
                    raise AGIAppError("Error executing application, or hangup")

            self.stderr.write('    RESULT_DICT: %s\n' % pprint.pformat(result))
            return result
        elif code == 510:
            raise AGIInvalidCommand(response)
        elif code == 520:
            usage = [line]
            line = self.stdin.readline().strip()
            while line[:3] != '520':
                usage.append(line)
                line = self.stdin.readline().strip()
            usage.append(line)
            usage = '%s\n' % '\n'.join(usage)
            raise AGIUsageError(usage)
        else:
            raise AGIUnknownError(code, 'Unhandled code or undefined response')

    def _process_digit_list(self, digits):
        if type(digits) == ListType:
            digits = ''.join(map(str, digits))
        return self._quote(digits)

    def appexec(self, application, options=''):
        result = self.execute('EXEC', application, self._quote(options))
        res = result['result'][0]
        if res == '-2':
            raise AGIAppError('Unable to find application: %s' % application)
        return res

    def hangup(self, channel=''):
        self.execute('HANGUP', channel)

    def get_data(self, caller, timeout=-1, max_digits=255):
        result = self.execute('GET DATA', caller, timeout, max_digits)
        res, value = result['result']
        return res

    def set_variable(self, name, value):
        self.execute('SET VARIABLE', self._quote(name), self._quote(value))

    def record_file(self, caller, format='gsm', escape_digits='#', timeout=-1, offset=0, beep='beep'):
        escape_digits = self._process_digit_list(escape_digits)
        res = \
        self.execute('RECORD FILE', self._quote(filename), format, escape_digits, timeout, offset, beep)['result'][0]
        # try:
        #     return chr(int(res))
        # except:
        #     raise AGIError('Unable to convert result to digit: %s' % res)

    def stream_file(self, filename, escape_digits='', sample_offset=0):
        escape_digits = self._process_digit_list(escape_digits)
        response = self.execute('STREAM FILE', filename, escape_digits, sample_offset)
        res = response['result'][0]
        if res == '0':
            return ''
        else:
            try:
                return chr(int(res))
            except:
                raise AGIError('Unable to convert result to char: %s' % res)


def program(self, agi):
    # Prompt date of birth
    agi.appexec('hcaller', 'Thank you for calling.')
    agi.appexec('hcaller', 'Please enter date of birth and press hash when done.')
    # Escape on hash enforced on the default function defination
    agi.record_file('dob')
    dob = agi.get_data('dob')
    agi.set_variable('dob', dob)

    # Date of birth validation
    try:
        # Expected format: DD MM YYYY
        datetime.datetime.strptime(date_text, '%d %m %Y')
    except ValueError:
        agi.appexec('hcaller', 'The date you entered seems to be invalid')

    # Prompt Postal code
    agi.appexec('hcaller', 'Thank you for entering your date of birth.')
    agi.appexec('hcaller', 'Please enter postal code and press hash when done.')
    # Escape on hash enforced on the default function defination
    agi.record_file('postal_code')
    postal_code = agi.get_data('postal_code')
    agi.set_variable('postal_code', postal_code)

    # Send data to backend to save in database
    payload = {"dob": agi.get_variable('dob'), "pc": agi.get_variable('postal_code')}
    r = requests.post("https://localhost/tel/add", data=payload)

    agi.appexec('festival', 'You entered ' + agi.get_variable('dob') + ' for date of birth and ' + agi.get_variable(
        'postal_code') + ' for postal code')

    return agi.stream_file('press-one-msg', ['1'])


if __name__ == '__main__':
    agi = AGI()

return_code = program(agi)
while return_code == '1':
    return_code = program(agi)

agi.hangup()