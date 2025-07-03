import random
import sys

from ctypes import CDLL
CDLL('libgtk4-layer-shell.so.0')

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk,Gio,Gdk,GLib

from dock import DockBuild
from data import DataApps, DataConfig

class App(Gtk.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        GLib.set_application_name("Hyprland Shell")
        GLib.set_prgname("hyprland-shell")

        DataConfig.createDataBase()
        DataApps.createDataBase()

    def do_activate(self):
        DockBuild._application = self
        DockBuild.build()

def main():
    ver = str(random.randint(10 ,99))
    app = App(application_id="hyprland.shell"+ver, flags=Gio.ApplicationFlags.FLAGS_NONE)
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)

if __name__ == "__main__":
    main()