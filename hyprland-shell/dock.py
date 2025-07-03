import os

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gtk4LayerShell', '1.0')
from gi.repository import Gtk,Gdk
from gi.repository import Gtk4LayerShell as LayerShell

from data import DataConfig

from modules.groupwidget import GroupWidget
from modules.clock import Clock
from modules.apps import Apps
from modules.launcher import Launcher
from modules.power import Power
from modules.powerprofile import PowerProfile
from modules.soundvolume import SoundVolume
from modules.soundmicrophone import SoundMicrophone
from modules.workspaces import Workspaces
from modules.battery import Battery
from modules.network import Network
from modules.windowtitle import WindowTitle
from modules.language import Language
from modules.setting import Setting
from modules.weather import Weather

class DockBuild:
    _dock_list = []
    _application = None
    _search_path_default = None
    _style_provider_current = None

    @staticmethod
    def build():
        for rec in DockBuild._dock_list:
            rec.close()
        DockBuild._dock_list.clear()

        DockBuild.initUI()

        #Проходми по всем мониторам
        display = Gdk.Display.get_default()
        for i in range(0, display.get_monitors().get_n_items()):
            monitor = display.get_monitors().get_item(i)
            monitor_name = monitor.get_connector()
            for dock in DataConfig.getConfigDocks(monitor=monitor_name):
                dockWindow = DockWindow(application=DockBuild._application, monitor=monitor, config_dock_id=dock['config_dock_id'])
                dockWindow.present()
                DockBuild._dock_list.append(dockWindow)

    @staticmethod
    def initUI():
        _params = DataConfig.getConfigBaseParams()
        if _params['theme'] == 'dark':
            isDarkTheme = True
        else:
            isDarkTheme = False

        #Путь к иконкам
        if isDarkTheme:
            Gtk.Settings.get_default().set_property("gtk-application-prefer-dark-theme", True)
            # Подключаем библиотеку иконок приложения
            icoPath = os.path.basename(__file__)
            icoPath = os.path.abspath(__file__).replace(icoPath, 'ui/img-dark')
        else:
            Gtk.Settings.get_default().set_property("gtk-application-prefer-dark-theme", False)
            # Подключаем библиотеку иконок приложения
            icoPath = os.path.basename(__file__)
            icoPath = os.path.abspath(__file__).replace(icoPath, 'ui/img-light')

        icon_theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())

        if DockBuild._search_path_default is None:
            DockBuild._search_path_default = icon_theme.get_search_path()
        else:
            icon_theme.set_search_path(DockBuild._search_path_default)

        icon_theme.add_search_path(icoPath)

        #Подключение стилей CSS
        stylePath = os.path.basename(__file__)
        if isDarkTheme:
            stylePath = os.path.abspath(__file__).replace(stylePath, 'ui/style-dark.css')
        else:
            stylePath = os.path.abspath(__file__).replace(stylePath, 'ui/style-light.css')

        if os.path.isfile(stylePath):
            if DockBuild._style_provider_current is not None:
                Gtk.StyleContext.remove_provider_for_display(Gdk.Display().get_default(), DockBuild._style_provider_current)

            style_provider = Gtk.CssProvider()
            style_provider.load_from_path(stylePath)
            DockBuild._style_provider_current = style_provider

            Gtk.StyleContext.add_provider_for_display(Gdk.Display().get_default(),
                                                      style_provider,
                                                      Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

#Окно док панели
class DockWindow(Gtk.ApplicationWindow):
    def __init__(self, monitor, config_dock_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_css_class("dock")

        self.app_ = self.get_application()
        self.monitor = monitor
        self.config_dock_id = config_dock_id

        self.set_size_request(100, 32)

        self.boxWidget = Gtk.CenterBox()
        self.beginBoxWidget = Gtk.Box()
        self.centerBoxWidget = Gtk.Box()
        self.endBoxWidget = Gtk.Box()

        self.set_child(self.boxWidget)
        self.boxWidget.set_start_widget(self.beginBoxWidget)
        self.boxWidget.set_center_widget(self.centerBoxWidget)
        self.boxWidget.set_end_widget(self.endBoxWidget)

        self.initLayer()
        self.initModules()

    def initLayer(self):
        params = DataConfig.getConfigDock(self.config_dock_id)
        hmargin = params['hmargin']
        vmargin = params['vmargin']
        layer = params['layer']
        self.anchor = params['anchor']

        LayerShell.init_for_window(self)
        LayerShell.set_namespace(self, 'hyprland-shell-dock')

        if layer == 'overlay':
            LayerShell.set_layer(self, LayerShell.Layer.OVERLAY)
        elif layer == 'bottom':
            LayerShell.set_layer(self, LayerShell.Layer.BOTTOM)
        else:
            LayerShell.set_layer(self, LayerShell.Layer.TOP)

        if self.anchor == 'bottom':
            LayerShell.set_anchor(self, LayerShell.Edge.BOTTOM, True)
            LayerShell.set_margin(self, LayerShell.Edge.BOTTOM, vmargin)
        else:
            LayerShell.set_anchor(self, LayerShell.Edge.TOP, True)
            LayerShell.set_margin(self, LayerShell.Edge.TOP, vmargin)

        LayerShell.set_anchor(self, LayerShell.Edge.LEFT, True)
        LayerShell.set_margin(self, LayerShell.Edge.LEFT, hmargin)
        LayerShell.set_anchor(self, LayerShell.Edge.RIGHT, True)
        LayerShell.set_margin(self, LayerShell.Edge.RIGHT, hmargin)

        LayerShell.auto_exclusive_zone_enable(self)
        LayerShell.set_monitor(self, self.monitor)

    def initModules(self):
        for rec in DataConfig.getConfigDockModules(config_dock_id=self.config_dock_id):
            modul = rec['modul']
            position = rec['position']
            ordernum  = rec['ordernum']
            groupnum = rec['groupnum']

            _is_check = False
            _modul = None

            if modul == 'PowerProfile':
                _is_check = PowerProfile.is_check()
            elif modul == 'Power':
                _is_check = Power.is_check()
            elif modul == 'Battery':
                _is_check = Battery.is_check()
            elif modul == 'Network':
                _is_check = Network.is_check()
            elif modul == 'Weather':
                _is_check = Weather.is_check()
            else:
                _is_check = True

            if not _is_check:
                continue

            if groupnum > 0:
                if position == 'center':
                    position = self.anchor

                if GroupWidget.is_exist(dock_object=self, position=position, groupnum=groupnum):
                    GroupWidget.set_widget(dock_object=self, position=position, groupnum=groupnum, modul=modul)
                else:
                    _modul = GroupWidget.create(dock_object=self, position=position, groupnum=groupnum)
                    GroupWidget.set_widget(dock_object=self, position=position, groupnum=groupnum, modul=modul)
            elif modul == 'Workspaces':
                _modul = Workspaces(monitor=self.getMonitorName())
            elif modul == 'Apps':
                _modul = Apps()
            elif modul == 'Launcher':
                _modul = Launcher()
            elif modul == 'Clock':
                _modul = Clock()
            elif modul == 'SoundVolume':
                _modul = SoundVolume()
            elif modul == 'SoundMicrophone':
                _modul = SoundMicrophone()
            elif modul == 'PowerProfile':
                _modul = PowerProfile()
            elif modul == 'Power':
                _modul = Power()
            elif modul == 'Battery':
                _modul = Battery()
            elif modul == 'Network':
                _modul = Network()
            elif modul == 'WindowTitle':
                _modul = WindowTitle()
            elif modul == 'Language':
                _modul = Language()
            elif modul == 'Setting':
                _modul = Setting()
            elif modul == 'Weather':
                _modul = Weather()

            if _modul is not None:
                if position == 'begin':
                    self.setBeginWidget(_modul)
                elif position in ('center','top','bottom'):
                    self.setCenterWidget(_modul)
                elif position == 'end':
                    self.setEndWidget(_modul)


    def getMonitorName(self):
        return self.monitor.get_connector()

    def getMonitorWidth(self):
        return self.monitor.get_geometry().width

    def getMonitorHeight(self):
        return self.monitor.get_geometry().height

    def setBeginWidget(self, widget):
        self.beginBoxWidget.append(widget)

    def setCenterWidget(self, widget):
        self.centerBoxWidget.append(widget)

    def setEndWidget(self, widget):
        self.endBoxWidget.append(widget)