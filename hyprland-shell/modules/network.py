import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk,GObject

from ctl import CtlNetwork
from lang import Lang

def getDeviceTypeIconName(atype:str):
    iconName = 'hs-network'
    if atype == 'ethernet':
        iconName = iconName + '-wired-enabled'
    elif atype == 'wifi':
        iconName = iconName + '-wireless-enabled'
    return iconName

def getDeviceStateIconName(atype:str, astate:str):
    iconName = 'hs-network'
    if atype == 'ethernet':
        iconName = iconName + '-wired'
    elif atype == 'wifi':
        iconName = iconName + '-wireless'

    if astate == 'connected':
        iconName = iconName + '-enabled'
    elif astate == 'disconnected':
        iconName = iconName + '-disabled'
    elif astate == 'unavailable':
        iconName = iconName + '-unavailable'
    else:
        iconName = iconName + '-unavailable'
    return iconName

def getConnectActionIconName(astate:str):
    iconName = 'hs-network'
    if astate == 'connected':
        iconName = iconName + '-connected'
    elif astate == 'disconnected':
        iconName = iconName + '-connect'
    return iconName

class NetworkWidget:
    def lang_init(self):
        self.text = Lang()
        self.text.set_text('ru','title','Сеть')
        self.text.set_text('en','title','Network')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.lang_init()
        self.title = self.text.get_text('title')

        self.devices = []

    def build_button(self, button_box:Gtk.Box):
        self.fillDevices(button_box)
        self.refreshDevices()
        self.startDevicesMonitorTimer()

    def build_window(self, window_box:Gtk.Box):
        group_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        group_box.add_css_class("group-widget-box")

        title = Gtk.Label(label=self.title)
        title.add_css_class("group-widget-title")
        group_box.append(title)

        for device in CtlNetwork.exec_get_devices():
            group_box.append(NetworkDevice(
                dockbutton = self,
                device = device['device'],
                type = device['type'],
                state = device['state'],
                connection = device['connection']
            ))

        window_box.append(group_box)

    # Кнопки на панели
    def fillDevices(self, button_box:Gtk.Box):
        self.devices = CtlNetwork.exec_get_devices()
        for device in self.devices:
            icon = Gtk.Image()
            device['icon'] = icon
            button_box.append(device['icon'])

    def refreshDevices(self):
        for device in CtlNetwork.exec_get_devices():
            for rec in self.devices:
                if rec['device'] == device['device']:
                    rec['icon'].set_from_icon_name(getDeviceStateIconName(atype=device['type'], astate=device['state']))

        return True

    def startDevicesMonitorTimer(self):
        GObject.timeout_add(10000, self.refreshDevices)

class Network(Gtk.Button):
    @staticmethod
    def is_check():
        try:
            test = CtlNetwork.exec_get_devices()
            return True
        except:
            return False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_css_class("dock-button")

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.widget = NetworkWidget()
        self.widget.build_button(button_box)
        self.set_child(button_box)

        self.connect('clicked', self.on_button_clicked)

    # Выпадающее меню
    def on_button_clicked(self, _button):
        self.popover = Gtk.Popover()
        window_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.widget.build_window(window_box)
        self.popover.set_child(window_box)
        self.popover.set_parent(self)
        self.popover.popup()

class NetworkDevice(Gtk.Box):
    def lang_init(self):
        self.text = Lang()
        self.text.set_text('ru','ethernet','Проводная сеть')
        self.text.set_text('ru', 'wifi', 'Беспроводная сеть')
        self.text.set_text('ru', 'enable', 'Включить')
        self.text.set_text('ru', 'disable', 'Выключить')

        self.text.set_text('en','ethernet','Ethernet')
        self.text.set_text('en', 'wifi', 'Wireless')
        self.text.set_text('en', 'enable', 'Enable')
        self.text.set_text('en', 'disable', 'Disable')

    def __init__(self, dockbutton, device, type, state, connection, **kwargs):
        super().__init__(**kwargs)

        self.lang_init()

        self.add_css_class("network-device")
        self.set_orientation(Gtk.Orientation.VERTICAL)

        self.dockbutton = dockbutton
        self.device = device
        self.type = type
        self.state = state
        self.connection = connection

        #Заголовок девайса
        titleBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        titleBox.add_css_class("network-device-title")
        titleBox.set_parent(self)
        titleBox.append(Gtk.Image().new_from_icon_name(getDeviceTypeIconName(atype=self.type)))
        if self.type == 'ethernet':
            titleBox.append(Gtk.Label(label=self.text.get_text('ethernet')))
        elif self.type == 'wifi':
            titleBox.append(Gtk.Label(label=self.text.get_text('wifi')))

        # Включение\отключение (Только для wifi)
        if self.type == 'wifi':
            enableBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            enableBox.add_css_class("network-device-connect")
            enableBox.set_parent(self)

            enableBt = Gtk.Button()
            enableBt.set_icon_name(getDeviceStateIconName(atype=self.type, astate=self.state))
            enableBt.state = self.state
            enableBt.type = self.type
            enableBt.connect('clicked', self.on_enable_button_clicked)
            enableBox.append(enableBt)
            if self.state == 'unavailable':
                enableBox.append(Gtk.Label(label=self.text.get_text('enable')))
            else:
                enableBox.append(Gtk.Label(label=self.text.get_text('disable')))

        # Соединения
        if self.state != 'unavailable':
            for connection in CtlNetwork.exec_get_connections(self.type):
                connectBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                connectBox.add_css_class("network-device-connect")
                connectBox.set_parent(self)

                connectBt = Gtk.Button()
                connectBt.set_icon_name(getConnectActionIconName(astate=connection['state']))
                connectBt.state = connection['state']
                connectBt.name = connection['name']
                connectBt.connect('clicked', self.on_connect_button_clicked)
                connectBox.append(connectBt)
                connectBox.append(Gtk.Label(label=connection['name']))

    def on_enable_button_clicked(self, _button):
        if _button.type == 'wifi':
            if _button.state == 'unavailable':
                CtlNetwork.exec_set_wifi_enable(aenable=True)
            else:
                CtlNetwork.exec_set_wifi_enable(aenable=False)

        self.dockbutton.refreshDevices()
        self.dockbutton.popover.hide()

    def on_connect_button_clicked(self, _button):
        if _button.state == 'connected':
            CtlNetwork.exec_set_connection(aname=_button.name, astate=False)
        elif _button.state == 'disconnected':
            CtlNetwork.exec_set_connection(aname=_button.name, astate=True)

        self.dockbutton.refreshDevices()
        self.dockbutton.popover.hide()