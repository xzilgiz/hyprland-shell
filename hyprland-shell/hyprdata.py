from hyprctl import HyprCtl

### Класс данных
class HyprData:
    _active_window_title = ''
    _workspaces = []
    _workspace_current = None
    _language = {}
    _active_apps = []
    _urgent_address = ''
    _urgent_allowed = False
    _monitors = []

    @staticmethod
    def get_active_window_title():
        return HyprData._active_window_title

    @staticmethod
    def upd_active_window_title(value):
        HyprData._active_window_title = value

    @staticmethod
    def upd_language(adevice, avalue):
        HyprData._language = dict(device=adevice, name=avalue, code=avalue[0:2].upper())

    @staticmethod
    def get_language():
        if HyprData._language == {}:
            value = HyprCtl.get_language()
            HyprData.upd_language(value['device'], value['value'])
        return HyprData._language

    @staticmethod
    def get_workspaces():
        if HyprData._workspaces == []:
            HyprData.upd_workspaces()
        return HyprData._workspaces

    @staticmethod
    def upd_workspaces():
        HyprData._workspaces = HyprCtl.get_workspaces()

    @staticmethod
    def get_workspace_current():
        return HyprData._workspace_current

    @staticmethod
    def upd_workspace_current(value):
        HyprData._workspace_current = value

    @staticmethod
    def get_active_apps():
        if HyprData._active_apps == []:
            HyprData.upd_active_apps()
        return HyprData._active_apps

    @staticmethod
    def upd_active_apps():
        HyprData._active_apps = HyprCtl.get_active_apps()

    @staticmethod
    def get_urgent_address():
        return HyprData._urgent_address

    @staticmethod
    def upd_urgent_address(address):
        HyprData._urgent_address = address

    @staticmethod
    def get_urgent_allowed():
        return HyprData._urgent_allowed

    @staticmethod
    def set_urgent_allowed(value:bool):
        HyprData._urgent_allowed = value

    @staticmethod
    def get_monitors():
        if HyprData._monitors == []:
            HyprData.upd_monitors()
        return HyprData._monitors

    @staticmethod
    def upd_monitors():
        HyprData._monitors = HyprCtl.get_monitors()