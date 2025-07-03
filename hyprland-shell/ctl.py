import os
import subprocess

def isCommand(cmd):
    cmd = cmd.split()[0]
    cmd = "command -v {}".format(cmd)
    try:
        is_cmd = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        if is_cmd:
            return True
    except subprocess.CalledProcessError:
        pass

    return False

class CtlNetwork:
    @staticmethod
    def exec_get_devices():
        result = []
        #enp2s0:ethernet:connected:Проводное подключение 1
        process = os.popen('nmcli -t device status')
        resStr = process.read().strip()
        process.close()

        for row in list(resStr.split("\n")):
            rowList = list(row.split(':'))
            device = rowList[0]
            type = rowList[1]
            state = rowList[2]
            connection = rowList[3]

            if type in ('ethernet','wifi'):
                result.append(dict(device=device, type=type, state=state, connection=connection))
            else:
                continue
        return result

    @staticmethod
    def exec_get_connections(atype):
        result = []
        process = os.popen('nmcli -t connection show')
        resStr = process.read().strip()
        process.close()

        for row in list(resStr.split("\n")):
            rowList = list(row.split(':'))

            name = rowList[0]
            uuid = rowList[1]
            type = rowList[2]
            device = rowList[3]

            if 'ethernet' in type:
                type = 'ethernet'
            elif 'wireless' in type:
                type = 'wifi'
            else:
                continue

            if type != atype:
                continue

            if device == '':
                state = 'disconnected'
            else:
                state = 'connected'

            result.append(dict(name=name, uuid=uuid, type=type, device=device, state=state))
        return result

    @staticmethod
    def exec_set_connection(aname, astate:bool):
        if astate:
            os.system('nmcli connection up "{}"'.format(aname))
        else:
            os.system('nmcli connection down "{}"'.format(aname))

    @staticmethod
    def exec_set_wifi_enable(aenable: bool):
        if aenable:
            os.system('nmcli radio wifi on')
        else:
            os.system('nmcli radio wifi off')

class CtlPower:
    @staticmethod
    def exec_shutdown():
        os.popen('systemctl poweroff')

    @staticmethod
    def exec_reboot():
        os.popen('systemctl reboot')

    @staticmethod
    def exec_logout():
        os.popen('killall Hyprland')

class CtlPowerProfile:
    p_is_performance = False
    p_is_balanced = False
    p_is_saver = False

    @staticmethod
    def is_check():
        if isCommand('powerprofilesctl') or isCommand('tuned-adm'):
            return True
        else:
            return False

    @staticmethod
    def exec_get():
        preprocessed = ''
        if isCommand('powerprofilesctl'):
            process = os.popen('powerprofilesctl get')
            preprocessed = process.read().strip()
            process.close()
        elif isCommand('tuned-adm'):
            process = os.popen('tuned-adm active')
            preprocessed = process.read().strip()
            preprocessed = preprocessed.split(':', 1)[1].strip()
            process.close()

        CtlPowerProfile.p_is_performance = False
        CtlPowerProfile.p_is_balanced = False
        CtlPowerProfile.p_is_saver = False

        if preprocessed == 'performance' or preprocessed == 'accelerator-performance':
            CtlPowerProfile.p_is_performance = True
        elif preprocessed == 'balanced' or preprocessed == 'balanced-battery':
            CtlPowerProfile.p_is_balanced = True
        else:
            CtlPowerProfile.p_is_saver = True

    @staticmethod
    def is_performance():
        return CtlPowerProfile.p_is_performance

    @staticmethod
    def is_balanced():
        return CtlPowerProfile.p_is_balanced

    @staticmethod
    def is_saver():
        return CtlPowerProfile.p_is_saver

    @staticmethod
    def exec_set_performance():
        if isCommand('powerprofilesctl'):
            os.system('powerprofilesctl set performance')
        elif isCommand('tuned-adm'):
            os.system('tuned-adm profile accelerator-performance')

    @staticmethod
    def exec_set_balanced():
        if isCommand('powerprofilesctl'):
            os.system('powerprofilesctl set balanced')
        elif isCommand('tuned-adm'):
            os.system('tuned-adm profile balanced-battery')

    @staticmethod
    def exec_set_saver():
        if isCommand('powerprofilesctl'):
            os.system('powerprofilesctl set power-saver')
        elif isCommand('tuned-adm'):
            os.system('tuned-adm profile powersave')

class CtlSoundVolume:
    p_value = 0
    p_mute = False

    @staticmethod
    def exec_get():
        process = os.popen('wpctl get-volume @DEFAULT_AUDIO_SINK@')
        preprocessed = process.read().strip()

        if "[MUTED]" in preprocessed:
            CtlSoundVolume.p_mute = True
        else:
            CtlSoundVolume.p_mute = False

        try:
            CtlSoundVolume.p_value = int(float(preprocessed.split()[1]) * 100)
        except:
            CtlSoundVolume.p_value = 0

        process.close()

    @staticmethod
    def is_mute():
        return CtlSoundVolume.p_mute

    @staticmethod
    def get_value():
        return CtlSoundVolume.p_value

    @staticmethod
    def exec_set_value(value):
        os.system('wpctl set-volume @DEFAULT_AUDIO_SINK@ ' + value + '%')

    @staticmethod
    def exec_toggle_mute():
        os.system('wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle')

    @staticmethod
    def exec_setting(exec:str):
        if isCommand(exec):
            os.popen(exec)

class CtlSoundMicrophone:
    p_value = 0
    p_mute = False

    @staticmethod
    def exec_get():
        process = os.popen('wpctl get-volume @DEFAULT_AUDIO_SOURCE@')
        preprocessed = process.read().strip()

        if "[MUTED]" in preprocessed:
            CtlSoundMicrophone.p_mute = True
        else:
            CtlSoundMicrophone.p_mute = False

        try:
            CtlSoundMicrophone.p_value = int(float(preprocessed.split()[1]) * 100)
        except:
            CtlSoundMicrophone.p_value = 0

        process.close()

    @staticmethod
    def is_mute():
        return CtlSoundMicrophone.p_mute

    @staticmethod
    def get_value():
        return CtlSoundMicrophone.p_value

    @staticmethod
    def exec_set_value(value):
        os.system('wpctl set-volume @DEFAULT_AUDIO_SOURCE@ ' + value + '%')

    @staticmethod
    def exec_toggle_mute():
        os.system('wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle')

    @staticmethod
    def exec_setting(exec:str):
        if isCommand(exec):
            os.popen(exec)

class CtlHypr:
    @staticmethod
    def exec_next_language(device):
        os.system("hyprctl switchxkblayout {} next".format(device))

    @staticmethod
    def exec_set_workspace(id):
        os.system('hyprctl dispatch workspace name:' + id)

    @staticmethod
    def exec_set_focus_window(address):
        addr = address
        if not addr.startswith('0x'):
            addr = '0x' + addr
        os.system('hyprctl dispatch focuswindow address:' + addr)

    @staticmethod
    def exec_movetoworkspace_window(workspace, address):
        addr = address
        if not addr.startswith('0x'):
            addr = '0x' + addr
        os.system("hyprctl dispatch movetoworkspace {},address:{}".format(workspace, addr))

    @staticmethod
    def exec_closed_window(address):
        addr = address
        if not addr.startswith('0x'):
            addr = '0x' + addr
        os.system('hyprctl dispatch closewindow address:' + addr)
