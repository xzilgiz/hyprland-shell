import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk,GObject

from ctl import CtlHypr
from hyprevent import HyprEvent, HyprEventType
from hyprdata import HyprData

#Отображение и переключение раскладки клавиатуры
class Language(Gtk.Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_css_class("dock-button")

        self.refreshInfo()
        self.connect('clicked', self.on_exec_clicked)
        HyprEvent.add_handle(self, HyprEventType.ON_LANGUAGE, self.on_language)

    def refreshInfo(self):
        value = HyprData.get_language()
        self.set_property("tooltip-text", value['name'])
        self.set_label(value['code'])

    def on_language(self):
        self.refreshInfo()

    def on_exec_clicked(self, _button):
        CtlHypr.exec_next_language(HyprData.get_language()['device'])