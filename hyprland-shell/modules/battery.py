import psutil

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk,GObject

from lang import Lang

#Батарея
class BatteryWidget:
    def lang_init(self):
        self.text = Lang()
        self.text.set_text('ru','title','Батарея')
        self.text.set_text('ru', 'charge_level', 'Уровень заряда')
        self.text.set_text('ru', 'status_charging', 'Состояние: заряжается')
        self.text.set_text('ru', 'charge_left_on', 'Осталось заряда на')

        self.text.set_text('en','title','Battery')
        self.text.set_text('en', 'charge_level', 'Charge level')
        self.text.set_text('en', 'status_charging', 'Status: charging')
        self.text.set_text('en', 'charge_left_on', 'There is charge left on')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lang_init()
        self.title = self.text.get_text('title')

        self.isBattery = False
        self.percent = 0
        self.left = ''
        self.plugged = False

    def build_button(self, button_box:Gtk.Box):
        self.icon = Gtk.Image.new_from_icon_name('hs-battery-no')
        button_box.append(self.icon)
        self.label = Gtk.Label(label='')
        button_box.append(self.label)

        self.refreshInfo()
        self.startTimer()

    def build_window(self, window_box:Gtk.Box):
        group_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        group_box.add_css_class("group-widget-box")

        title = Gtk.Label(label=self.title)
        title.add_css_class("group-widget-title")
        group_box.append(title)

        self.LabelPercent = Gtk.Label(label='')
        self.labelState = Gtk.Label(label='')

        group_box.append(self.LabelPercent)
        group_box.append(self.labelState)
        window_box.append(group_box)

        self.LabelPercent.set_label(self.text.get_text('charge_level') + ': ' + str(self.percent) + '%')
        if self.plugged:
            self.labelState.set_label(self.text.get_text('status_charging'))
        else:
            self.labelState.set_label(self.text.get_text('charge_left_on') + ': ' + self.left)

    def secs2hours(self, secs):
        mm, ss = divmod(secs, 60)
        hh, mm = divmod(mm, 60)
        return "%d:%02d:%02d" % (hh, mm, ss)

    def refreshInfo(self):
        battery = psutil.sensors_battery()
        if battery is not None:
            self.isBattery = True
            self.percent = battery.percent
            self.percent = round(self.percent)
            self.plugged = battery.power_plugged
            if not self.plugged:
                self.left = self.secs2hours(battery.secsleft)
            else:
                self.left = ''
        else:
            self.isBattery = False

        if self.isBattery:
            self.label.set_label(' '+str(self.percent)+'%')

            level = round(self.percent/10) * 10
            iconName = 'hs-battery-level-' + str(round(level))
            if self.plugged:
                iconName = iconName + '-charging'

            self.icon.set_from_icon_name(iconName)
        else:
            self.label.set_label('')
            self.label.set_visible(False)
            self.icon.set_from_icon_name('hs-battery-no')

            return False
        return True

    def startTimer(self):
        GObject.timeout_add(5000, self.refreshInfo)

class Battery(Gtk.Button):
    @staticmethod
    def is_check():
        try:
            battery = psutil.sensors_battery()
            return battery is not None
        except:
            return False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_css_class("dock-button")

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.widget = BatteryWidget()
        self.widget.build_button(button_box)
        self.set_child(button_box)

        if self.widget.isBattery:
            self.connect('clicked', self.on_info_clicked)

    def on_info_clicked(self, _button):
        window_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.widget.build_window(window_box)
        self.widget.refreshInfo()

        popover = Gtk.Popover()
        popover.set_child(window_box)
        popover.set_parent(self)
        popover.popup()