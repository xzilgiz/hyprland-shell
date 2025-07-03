import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk,GObject

from hyprevent import HyprEvent, HyprEventType
from hyprdata import HyprData

#Заголовок активного окна
class WindowTitle(Gtk.Box):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_css_class("window-title")

        self.title = Gtk.Label(label='')
        self.append(self.title)

        HyprEvent.add_handle(self, HyprEventType.ON_WINDOW_TITLE, self.on_active_window_title)

    def on_active_window_title(self):
        self.title.set_label(HyprData.get_active_window_title())