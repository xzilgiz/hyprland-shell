import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk,GObject
from ctl import CtlPowerProfile
from lang import Lang

class PowerProfileWidget:
    def lang_init(self):
        self.text = Lang()
        self.text.set_text('ru','title','Профиль питания')
        self.text.set_text('ru', 'performance', 'Производительный')
        self.text.set_text('ru', 'balanced', 'Сбалансированный')
        self.text.set_text('ru', 'saver', 'Экономичный')

        self.text.set_text('en','title','Power profile')
        self.text.set_text('en', 'performance', 'Performance')
        self.text.set_text('en', 'balanced', 'Balanced')
        self.text.set_text('en', 'saver', 'Saver')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lang_init()
        self.title = self.text.get_text('title')

    def build_button(self, button_box:Gtk.Box):
        self.icon = Gtk.Image.new_from_icon_name('hs-power-profile-saver')
        self.icon.set_icon_size(Gtk.IconSize.NORMAL)
        button_box.append(self.icon)

    def build_window(self, window_box:Gtk.Box):
        group_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        group_box.add_css_class("group-widget-box")

        title = Gtk.Label(label=self.title)
        title.add_css_class("group-widget-title")
        group_box.append(title)

        self.btPerformance = PowerProfileButton(
            parent=self,
            icon='hs-power-profile-performance',
            label=self.text.get_text('performance'),
            action='performance')
        self.btBalanced = PowerProfileButton(
            parent=self,
            icon='hs-power-profile-balanced',
            label=self.text.get_text('balanced'),
            action='balanced')
        self.btSaver = PowerProfileButton(
            parent=self,
            icon='hs-power-profile-saver',
            label=self.text.get_text('saver'),
            action='saver')

        group_box.append(self.btPerformance)
        group_box.append(self.btBalanced)
        group_box.append(self.btSaver)

        window_box.append(group_box)

        self.refreshInfo()
        self.startMonitorTimer()

    def refreshInfo(self):
        CtlPowerProfile.exec_get()
        self.btPerformance.set_sensitive(not CtlPowerProfile.is_performance())
        self.btBalanced.set_sensitive(not CtlPowerProfile.is_balanced())
        self.btSaver.set_sensitive(not CtlPowerProfile.is_saver())

        if CtlPowerProfile.is_performance():
            self.icon.set_from_icon_name('hs-power-profile-performance')
        elif CtlPowerProfile.is_balanced():
            self.icon.set_from_icon_name('hs-power-profile-balanced')
        elif CtlPowerProfile.is_saver():
            self.icon.set_from_icon_name('hs-power-profile-saver')

        return True

    def startMonitorTimer(self):
        GObject.timeout_add(10000, self.refreshInfo)

class PowerProfile(Gtk.Button):
    @staticmethod
    def is_check():
        try:
            return CtlPowerProfile.is_check()
        except:
            return False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_css_class("dock-button")

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.widget = PowerProfileWidget()
        self.widget.build_button(button_box)
        self.set_child(button_box)

        self.connect('clicked', self.on_button_clicked)

    def on_button_clicked(self, _button):
        window_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.widget.build_window(window_box)
        self.widget.refreshInfo()

        popover = Gtk.Popover()
        popover.set_child(window_box)
        popover.set_parent(self)
        popover.popup()

class PowerProfileButton(Gtk.Button):
    def __init__(self, parent, icon, label, action, **kwargs):
        super().__init__(**kwargs)
        self.parent = parent
        self.action = action

        self.connect('clicked', self.on_power_button_clicked)

        buttonBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        icon_img = Gtk.Image.new_from_icon_name(icon)
        icon_img.set_icon_size(Gtk.IconSize.NORMAL)
        buttonBox.append(icon_img)
        buttonBox.append(Gtk.Label(label=label))

        self.set_child(buttonBox)

    def on_power_button_clicked(self, _button):
        if self.action == 'performance':
            CtlPowerProfile.exec_set_performance()
        elif self.action == 'balanced':
            CtlPowerProfile.exec_set_balanced()
        elif self.action == 'saver':
            CtlPowerProfile.exec_set_saver()

        PowerProfileWidget.refreshInfo(self.parent)
