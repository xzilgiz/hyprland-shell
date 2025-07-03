import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from ctl import CtlPower
from lang import Lang

class PowerWidget:
    def lang_init(self):
        self.text = Lang()
        self.text.set_text('ru','title','Завершение работы')
        self.text.set_text('ru', 'shutdown', 'Выключить')
        self.text.set_text('ru', 'reboot', 'Перезагрузить')
        self.text.set_text('ru', 'logout', 'Выход')

        self.text.set_text('en','title','Shutdown')
        self.text.set_text('en', 'shutdown', 'Turn off')
        self.text.set_text('en', 'reboot', 'Reboot')
        self.text.set_text('en', 'logout', 'Logout')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lang_init()
        self.title = self.text.get_text('title')

    def build_button(self, button_box:Gtk.Box):
        icon = Gtk.Image.new_from_icon_name('hs-system-shutdown')
        icon.set_icon_size(Gtk.IconSize.NORMAL)
        button_box.append(icon)

    def build_window(self, window_box:Gtk.Box):
        group_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        group_box.add_css_class("group-widget-box")

        title = Gtk.Label(label=self.title)
        title.add_css_class("group-widget-title")
        group_box.append(title)

        group_box.append(PowerButton(icon='hs-system-shutdown', label=self.text.get_text('shutdown'), action='shutdown'))
        group_box.append(PowerButton(icon='hs-system-reboot', label=self.text.get_text('reboot'), action='reboot'))
        group_box.append(PowerButton(icon='hs-system-log-out', label=self.text.get_text('logout'), action='logout'))
        window_box.append(group_box)

class Power(Gtk.Button):
    @staticmethod
    def is_check():
        return True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_css_class("dock-button")

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        self.widget = PowerWidget()
        self.widget.build_button(button_box)
        self.set_child(button_box)

        self.connect('clicked', self.on_button_clicked)

    def on_button_clicked(self, _button):
        window_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.widget.build_window(window_box)

        popover = Gtk.Popover()
        popover.set_child(window_box)
        popover.set_parent(self)
        popover.popup()

class PowerButton(Gtk.Button):
    def __init__(self, icon, label, action, **kwargs):
        super().__init__(**kwargs)
        self.action = action

        self.connect('clicked', self.on_power_button_clicked)

        self.buttonBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.icon = Gtk.Image.new_from_icon_name(icon)
        self.icon.set_icon_size(Gtk.IconSize.NORMAL)
        self.buttonBox.append(self.icon)

        self.label = Gtk.Label(label=label)
        self.buttonBox.append(self.label)

        self.set_child(self.buttonBox)

    def on_power_button_clicked(self, _button):
        if self.action == 'shutdown':
            CtlPower.exec_shutdown()
        elif self.action == 'reboot':
            CtlPower.exec_reboot()
        elif self.action == 'logout':
            CtlPower.exec_logout()