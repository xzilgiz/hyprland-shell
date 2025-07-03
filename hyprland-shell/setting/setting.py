import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk,Gio,Gdk

from setting.setting_base import SettingBase
from setting.setting_launcher import SettingLauncher
from setting.setting_dock import SettingDock
from setting.setting_modules import SettingModules

class SettingWindow(Gtk.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._section_current = None

        #Основное окно делим лево(разделы) - центр(настройки) - право(...)
        self.section_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.section_box.add_css_class("setting")
        self.set_child(self.section_box)

        #Список разделов
        self.section_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.section_list_box.add_css_class("setting-section-list")
        self.section_box.append(self.section_list_box)

        #Добавляем разделы
        self.set_section(SettingBase())
        self.set_section(SettingLauncher())
        self.set_section(SettingDock())
        self.set_section(SettingModules())

    def set_section(self, section_obj):
        section_obj.props.vexpand = True
        section_obj.props.hexpand = True
        section_obj.add_css_class("setting-section-body")

        button = Gtk.Button(label=section_obj.name)
        button.section_obj = section_obj
        button.connect('clicked', self.on_section_clicked)
        self.section_list_box.append(button)

    def on_section_clicked(self, _button):
        if self._section_current is not None:
            self.section_box.remove(self._section_current)

        self._section_current = _button.section_obj
        self.section_box.append(_button.section_obj)