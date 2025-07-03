import os

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk,Gdk

from data import DataApps, DataConfig
from ctl import CtlHypr
from hyprevent import HyprEvent, HyprEventType
from hyprdata import HyprData
from lang import Lang

#Панелька с кнопками приложений для док панели
class Apps(Gtk.Box):
    objectList = []
    _terminal_exec = ''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_css_class("apps")

        _params = DataConfig.getConfigBaseParams()
        Apps._terminal_exec = _params['terminal_exec']

        _params = DataConfig.getConfigDockModulParams(modul='Apps')
        self.is_active = _params['is_active']
        self.fill()

        HyprEvent.add_handle(self, HyprEventType.ON_APP, self.on_app)
        HyprEvent.add_handle(self, HyprEventType.ON_APP_URGENT, self.on_urgent)
        HyprEvent.add_handle(self, HyprEventType.ON_WORKSPACE_CURRENT, self.on_workspace_current)
        Apps.objectList.append(self)

    def __del__(self):
        Apps.objectList.remove(self)

    @staticmethod
    def refill():
        for obj in Apps.objectList:
            obj.fill()

    def fill(self):
        # Чистим панель
        cnt = 0
        for rec in self:
            cnt = cnt + 1

        try:
            for i in range(0, cnt):
               self.remove(self.get_last_child())
        except:
            pass

        # Выводим результаты
        for app in DataApps.get_apps_favorite(is_and_active=self.is_active):
            self.append(App(app=app))

    def on_app(self):
        self.fill()

    def on_urgent(self):
        if HyprData.get_urgent_allowed():
            CtlHypr.exec_set_focus_window(HyprData.get_urgent_address())
            HyprData.set_urgent_allowed(False)

    def on_workspace_current(self):
        pass

#Кнопки с приложениями
class App(Gtk.Button):
    def lang_init(self):
        self.text = Lang()
        self.text.set_text('ru','app_focus','Перейти к приложению')
        self.text.set_text('ru', 'app_move', 'Преместить на текущий рабочий стол')
        self.text.set_text('ru', 'app_closed', 'Закрыть приложение')

        self.text.set_text('en','app_focus','Go to application')
        self.text.set_text('en', 'app_move', 'Move to current desktop')
        self.text.set_text('en', 'app_closed', 'Close application')

    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)

        self.lang_init()

        self.add_css_class("app")

        self.app = app

        self.setIcon()
        self.setLabel()

        # Клик левой кнопки мыши
        self.connect('clicked', self.on_exec_clicked)

        # Клик правой кнопки мыши
        gs = Gtk.GestureClick()
        gs.set_button(Gdk.BUTTON_SECONDARY)
        gs.connect('pressed', self.on_exec_secondary_clicked)
        self.add_controller(gs)

        if self.app.is_active():
            self.add_css_class("app-active")
        if not self.app.is_favorite():
            self.add_css_class("app-nofavorite")

    def setIcon(self):
        if os.path.isfile(self.app.icon):
            icon = Gtk.Image.new_from_file(self.app.icon)
        else:
            icon = Gtk.Image.new_from_icon_name(self.app.icon)

        icon.set_icon_size(Gtk.IconSize.LARGE)
        self.set_child(icon)

    def setLabel(self):
        self.set_property("tooltip-text", self.app.name)

    def on_exec_clicked(self, _button):
        #Если приложение неизвестное то перемещаем фокус на него
        if self.app.exec == '':
            for rec in self.app.actives:
                if rec.address != '':
                    CtlHypr.exec_set_focus_window(rec.address)
        else: #Иначе штатно запускаем
            HyprData.set_urgent_allowed(True)
            if self.app.terminal:
                os.popen(Apps._terminal_exec + " " + self.app.exec + " &")
            else:
                os.popen(self.app.exec + " &")

    #Выпадающее меню с запущенными экземплярами, для перехода
    def on_exec_secondary_clicked(self, *args, **kwargs):
        self.showAppMenu()

    def showAppMenu(self):
        exists = False
        popoverBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        #Кнопки:
        popover = Gtk.Popover()
        for active_apps in DataApps.get_apps_active():
            if self.app.id == active_apps.id:
                for active_app in active_apps.actives:
                    box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                    box.props.halign = Gtk.Align.END

                    #Заголовок
                    box.append(Gtk.Label(label=active_app.title))

                    #Кнопка форкуса
                    btSetFocus = Gtk.Button()
                    btSetFocus.set_icon_name('hs-app-focus')
                    btSetFocus.set_property("tooltip-text", self.text.get_text('app_focus'))
                    btSetFocus.popover = popover
                    btSetFocus.address = active_app.address
                    btSetFocus.connect('clicked', self.on_exec_set_focus_clicked)
                    box.append(btSetFocus)

                    # Кнопка перемещения на текущий воркспейс
                    btMove = Gtk.Button()
                    btMove.set_icon_name('hs-app-move')
                    btMove.set_property("tooltip-text", self.text.get_text('app_move'))
                    btMove.popover = popover
                    btMove.address = active_app.address
                    btMove.connect('clicked', self.on_exec_movetoworkspace_clicked)
                    box.append(btMove)

                    # Кнопка закрытия приложения
                    btClosed = Gtk.Button()
                    btClosed.set_icon_name('hs-app-closed')
                    btClosed.set_property("tooltip-text", self.text.get_text('app_closed'))
                    btClosed.popover = popover
                    btClosed.address = active_app.address
                    btClosed.connect('clicked', self.on_exec_closedwindow_clicked)
                    box.append(btClosed)

                    popoverBox.append(box)
                    exists = True

        if exists:
            popover.set_child(popoverBox)
            popover.set_parent(self)
            popover.popup()

    def on_exec_set_focus_clicked(self, _button):
        CtlHypr.exec_set_focus_window(_button.address)
        _button.popover.hide()

    def on_exec_movetoworkspace_clicked(self, _button):
        CtlHypr.exec_movetoworkspace_window(HyprData.get_workspace_current(), _button.address)
        _button.popover.hide()

    def on_exec_closedwindow_clicked(self, _button):
        CtlHypr.exec_closed_window(_button.address)
        _button.popover.hide()
