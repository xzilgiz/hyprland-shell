import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk,GObject
from datetime import datetime

from data import DataConfig
from lang import Lang

#Дата время для док панели
class ClockWidget:
    def lang_init(self):
        self.text = Lang()
        self.text.set_text('ru','title','Календарь')
        self.text.set_text('en','title','Calendar')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lang_init()
        self.title = self.text.get_text('title')

        _params = DataConfig.getConfigDockModulParams(modul='Clock')
        self.maskData = _params['mask_date']
        self.maskTime = _params['mask_time']

    def build_button(self, button_box:Gtk.Box):
        self.iconData = Gtk.Image.new_from_icon_name('hs-calendar')
        button_box.append(self.iconData)
        self.labelData = Gtk.Label(label='')
        button_box.append(self.labelData)

        self.iconTime = Gtk.Image.new_from_icon_name('hs-clock')
        button_box.append(self.iconTime)
        self.labelTime = Gtk.Label(label='')
        button_box.append(self.labelTime)

        self.refreshInfo()
        self.startClockTimer()

    def build_window(self, window_box:Gtk.Box):
        group_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        group_box.add_css_class("group-widget-box")

        title = Gtk.Label(label=self.title)
        title.add_css_class("group-widget-title")
        group_box.append(title)

        group_box.append(Gtk.Calendar())
        window_box.append(group_box)

    def refreshInfo(self):
        datetimenow = datetime.now()
        date_str = datetimenow.strftime(self.maskData)
        time_str = datetimenow.strftime(self.maskTime)

        self.labelData.set_label(date_str)
        self.labelTime.set_label(time_str)
        return True

    def startClockTimer(self):
        GObject.timeout_add(1000, self.refreshInfo)

class Clock(Gtk.Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_css_class("dock-button")

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        window_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.widget = ClockWidget()
        self.widget.build_button(button_box)
        self.widget.build_window(window_box)

        self.set_child(button_box)
        self.popover = Gtk.Popover()
        self.popover.set_child(window_box)
        self.popover.set_parent(self)

        self.connect('clicked', self.on_calendar_clicked)

    def on_calendar_clicked(self, _button):
        self.widget.refreshInfo()
        self.popover.popup()

