from dataclasses import dataclass, field

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gtk4LayerShell', '1.0')
from gi.repository import Gtk,Gio,Gdk
from gi.repository import Gtk4LayerShell as LayerShell

from modules.powerprofile import PowerProfileWidget
from modules.power import PowerWidget
from modules.battery import BatteryWidget
from modules.soundvolume import SoundVolumeWidget
from modules.soundmicrophone import SoundMicrophoneWidget
from modules.network import NetworkWidget
from modules.setting import SettingWidget
from modules.weather import WeatherWidget
from modules.clock import ClockWidget


#Групповой виджет - кнопка на панели
class GroupWidgetButton(Gtk.Button):
    def __init__(self, position:str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.add_css_class("group-widget-button")
        self.add_css_class("dock-button")

        self.position = position
        self._modul_list = []

        self.button_box = Gtk.Box()
        self.button_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.set_child(self.button_box)

        self.connect('clicked', self.on_button_clicked)

    def set_widget(self, modul:str):
        widget = None
        if modul == 'PowerProfile':
            widget = PowerProfileWidget()
        elif modul == 'Power':
            widget = PowerWidget()
        elif modul == 'Battery':
            widget = BatteryWidget()
        elif modul == 'SoundVolume':
            widget = SoundVolumeWidget()
        elif modul == 'SoundMicrophone':
            widget = SoundMicrophoneWidget()
        elif modul == 'Network':
            widget = NetworkWidget()
        elif modul == 'Setting':
            widget = SettingWidget()
        elif modul == 'Weather':
            widget = WeatherWidget()
        elif modul == 'Clock':
            widget = ClockWidget()

        if widget is not None:
            widget.build_button(button_box=self.button_box)
            self._modul_list.append(widget)

    def on_button_clicked(self, _button):
        if not hasattr(self, 'widget_window') or not self.widget_window.get_visible():
            window_box = Gtk.Box()
            window_box.props.halign = Gtk.Align.CENTER
            if self.position in ('begin','end'):
                window_box.set_orientation(Gtk.Orientation.VERTICAL)
            else:
                window_box.set_orientation(Gtk.Orientation.HORIZONTAL)

            for widget in self._modul_list:
                widget.build_window(window_box=window_box)

            self.widget_window = GroupWidgetWindow(window_box=window_box, position=self.position)
            self.widget_window.present()
        else:
            self.widget_window.close()

#Групповой виджет - окно виджета
class GroupWidgetWindow(Gtk.ApplicationWindow):
    def __init__(self, window_box:Gtk.Box, position:str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_css_class("group-widget-window")
        self.position = position

        self.set_child(window_box)
        self.initLayer()

    def initLayer(self):
        LayerShell.init_for_window(self)

        LayerShell.set_layer(self, LayerShell.Layer.OVERLAY)
        LayerShell.set_anchor(self, LayerShell.Edge.BOTTOM, self.position in ['bottom','begin','end'])
        LayerShell.set_anchor(self, LayerShell.Edge.TOP, self.position in ['top','begin','end'])
        LayerShell.set_anchor(self, LayerShell.Edge.LEFT, self.position in ['begin','bottom','top'])
        LayerShell.set_anchor(self, LayerShell.Edge.RIGHT, self.position in ['end','bottom','top'])

        if self.position == 'top':
            LayerShell.set_margin(self, LayerShell.Edge.TOP, 5)
            LayerShell.set_margin(self, LayerShell.Edge.LEFT, 5)
            LayerShell.set_margin(self, LayerShell.Edge.RIGHT, 5)
        elif self.position == 'bottom':
            LayerShell.set_margin(self, LayerShell.Edge.BOTTOM, 5)
            LayerShell.set_margin(self, LayerShell.Edge.LEFT, 5)
            LayerShell.set_margin(self, LayerShell.Edge.RIGHT, 5)
        elif self.position == 'begin':
            LayerShell.set_margin(self, LayerShell.Edge.BOTTOM, 5)
            LayerShell.set_margin(self, LayerShell.Edge.TOP, 5)
            LayerShell.set_margin(self, LayerShell.Edge.LEFT, 5)
        elif self.position == 'end':
            LayerShell.set_margin(self, LayerShell.Edge.BOTTOM, 5)
            LayerShell.set_margin(self, LayerShell.Edge.TOP, 5)
            LayerShell.set_margin(self, LayerShell.Edge.RIGHT, 5)

        LayerShell.auto_exclusive_zone_enable(self)

@dataclass
class GroupWidgetData:
    groupnum: int = 0
    position: str = ''
    dock_object: 'typing.Any' = None #DockWindow
    group_widget_object: GroupWidgetButton = None

#Основной класс сборки группового виджета
class GroupWidget:
    _group_widget_list = [GroupWidgetData]

    @staticmethod
    def is_exist(dock_object, position:str, groupnum:int) -> bool:
        for rec in GroupWidget._group_widget_list:
            if rec.dock_object == dock_object and rec.position == position and rec.groupnum == groupnum:
                return True

        return False

    @staticmethod
    def create(dock_object, position: str, groupnum: int):
        gw = GroupWidgetData()
        gw.dock_object = dock_object
        gw.position = position
        gw.groupnum = groupnum

        gwb = GroupWidgetButton(position=position)
        gw.group_widget_object = gwb

        GroupWidget._group_widget_list.append(gw)
        return gwb

    @staticmethod
    def set_widget(dock_object, position: str, groupnum: int, modul:str):
        for rec in GroupWidget._group_widget_list:
            if rec.dock_object == dock_object and rec.position == position and rec.groupnum == groupnum:
                rec.group_widget_object.set_widget(modul=modul)