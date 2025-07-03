import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GObject

from ctl import CtlHypr
from hyprevent import HyprEvent, HyprEventType
from hyprdata import HyprData
from data import DataApps, DataConfig
from lang import Lang

class Workspaces(Gtk.Box):
    apps = []
    _is_active = True
    _style = 'circle' #number

    def __init__(self, monitor, **kwargs):
        super().__init__(**kwargs)
        self.add_css_class("workspaces")

        self.monitor = monitor
        self.workspace_list = []

        _params = DataConfig.getConfigDockModulParams(modul='Workspaces')
        Workspaces._is_active = _params['is_active']
        Workspaces._style = _params['style']

        #Кнопка слайдер
        self.slaider_value = 1 #0-активные и не пустые 1- +персистентные 2- +дефолтные
        self.slaider = Gtk.Button()
        self.slaider.add_css_class("workspace-slaider")
        self.slaider.connect('clicked', self.on_slider_clicked)

        self.refreshInfo()

        HyprEvent.add_handle(self, HyprEventType.ON_WORKSPACE, self.on_workspace)

    def start_slider_timer(self):
        GObject.timeout_add(5000, self.slider_default_state)

    def on_slider_clicked(self, _button):
        if self.slaider_value == 0:
            self.slaider_value = 1
            self.start_slider_timer()
        elif self.slaider_value == 1:
            self.slaider_value = 2
            self.start_slider_timer()
        elif self.slaider_value == 2:
            self.slaider_value = 1 #0

        self.set_workspaces_visible()

    def slider_default_state(self):
        self.slaider_value = 1
        self.set_workspaces_visible()

    def set_workspaces_visible(self):
        if self.slaider_value == 0:
            self.slaider.set_icon_name('hs-position-right')
            for rec in self.workspace_list:
                rec.set_visible(rec.empty == 'False' or rec.active == 'True')
        elif self.slaider_value == 1:
            self.slaider.set_icon_name('hs-position-right')
            for rec in self.workspace_list:
                rec.set_visible(rec.empty == 'False' or rec.active == 'True' or rec.persistent == 'True')
        else:
            self.slaider.set_icon_name('hs-position-left')
            for rec in self.workspace_list:
                rec.set_visible(True)

    def refreshInfo(self):
        Workspaces.apps = DataApps.get_apps_active()
        #Чистим панель
        cnt = 0
        for rec in self.workspace_list:
            cnt = cnt + 1

        try:
            for i in range(0, cnt):
               self.remove(self.workspace_list[i])
            self.workspace_list.clear()
        except:
            pass

        #Берём данные по текущему монитору
        wsn = []
        for rec in HyprData.get_workspaces():
            if rec['name'] == self.monitor:
                wsn = rec['ws']

        #Проходим по данным воккспейсов и создаём их
        for ws in wsn:
            t = Workspace(id=ws['id'])
            t.set_params(ws['persistent'], ws['empty'], ws['active'])
            self.append(t)
            self.workspace_list.append(t)

        #Перемещаем кнопку слайдера в конец
        if self.slaider in self:
            self.remove(self.slaider)
        self.append(self.slaider)

        #Простовляем видимость
        self.set_workspaces_visible()

    def on_workspace(self):
        self.refreshInfo()

class Workspace(Gtk.Box):
    def lang_init(self):
        self.text = Lang()
        self.text.set_text('ru','app_focus','Перейти к приложению')
        self.text.set_text('ru', 'app_move', 'Преместить на текущий рабочий стол')
        self.text.set_text('ru', 'app_closed', 'Закрыть приложение')

        self.text.set_text('en','app_focus','Go to application')
        self.text.set_text('en', 'app_move', 'Move to current desktop')
        self.text.set_text('en', 'app_closed', 'Close application')

    def __init__(self, id, **kwargs):
        super().__init__(**kwargs)

        self.lang_init()

        self.add_css_class("workspace")

        self.id = id
        self.persistent = ''
        self.empty = ''
        self.active = ''

        #Кнопка воркспейса
        self.button_main = Gtk.Button()
        self.button_main.add_css_class("workspace-main")
        self.button_main.set_label(self.id)
        self.button_main.connect('clicked', self.on_exec_clicked)
        self.append(self.button_main)

        #Кнопки запущенных приложений
        if Workspaces._is_active:
            for app in Workspaces.apps:
                for activ_app in app.actives:
                    if activ_app.workspace == self.id:
                        button_app = Gtk.Button()
                        button_app.add_css_class("workspace-app")
                        button_app.address = activ_app.address
                        button_app.title = app.name + ': ' + activ_app.title
                        button_app.set_icon_name(app.icon)
                        # Клик левой кнопкой мыши
                        button_app.connect('clicked', self.on_exec_set_focus_clicked)
                        # Клик правой кнопкой мыши
                        gs = Gtk.GestureClick()
                        gs.set_button(Gdk.BUTTON_SECONDARY)
                        gs.connect('pressed', self.on_exec_secondary_clicked, button_app)
                        button_app.add_controller(gs)

                        self.append(button_app)

    def set_params(self, persistent, empty, active):
        self.persistent = persistent
        self.empty = empty
        self.active = active

        if self.active == 'True':
            self.add_css_class("workspace-active")
        else:
            self.remove_css_class("workspace-active")

        if self.persistent == 'True':
            self.add_css_class("workspace-persistent")
        else:
            self.remove_css_class("workspace-persistent")

        if self.empty == 'False':
            self.remove_css_class("workspace-empty")
        else:
            self.add_css_class("workspace-empty")

        if Workspaces._style == 'circle':
            if self.active == 'True':
                self.button_main.set_icon_name('hs-workspace-active')
            elif self.empty == 'False':
                self.button_main.set_icon_name('hs-workspace-notempty')
            else:
                self.button_main.set_icon_name('hs-workspace-empty')


    #Переключение воркспейса
    def on_exec_clicked(self, _button):
        CtlHypr.exec_set_workspace(self.id)

    #Переключение фокуса на приложение
    #Выпадающее меню - Переключение фокуса на приложение
    def on_exec_set_focus_clicked(self, _button):
        CtlHypr.exec_set_focus_window(_button.address)
        if hasattr(_button, 'popover'):
            _button.popover.hide()

    #Выпадающее меню
    def on_exec_secondary_clicked(self, *args, **kwargs):
        for rec in args:
            if type(rec) is Gtk.Button:
                self.showAppMenu(rec.address, rec.title)
                break

    #Выпадающее меню - Перемещение приложения на текущий воркспейс
    def on_exec_movetoworkspace_clicked(self, _button):
        CtlHypr.exec_movetoworkspace_window(HyprData.get_workspace_current(), _button.address)
        _button.popover.hide()

    #Выпадающее меню - Закрыть приложение
    def on_exec_closedwindow_clicked(self, _button):
        CtlHypr.exec_closed_window(_button.address)
        _button.popover.hide()

    #Выпадающее меню
    def showAppMenu(self, address, title):
        popover = Gtk.Popover()
        popoverBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        #Заголовок
        popoverBox.append(Gtk.Label(label=title))

        #Кнопка перемещения к приложению
        boxFocus = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        btFocus = Gtk.Button()
        btFocus.set_icon_name('hs-app-focus')
        btFocus.popover = popover
        btFocus.address = address
        btFocus.connect('clicked', self.on_exec_set_focus_clicked)
        boxFocus.append(btFocus)
        boxFocus.append(Gtk.Label(label=self.text.get_text('app_focus')))
        popoverBox.append(boxFocus)

        #Кнопка перемещения на текущий воркспейс
        boxMove = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        btMove = Gtk.Button()
        btMove.set_icon_name('hs-app-move')
        btMove.popover = popover
        btMove.address = address
        btMove.connect('clicked', self.on_exec_movetoworkspace_clicked)
        boxMove.append(btMove)
        boxMove.append(Gtk.Label(label=self.text.get_text('app_move')))
        popoverBox.append(boxMove)

        #Кнопка закрытия приложения
        boxClosed = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        btClosed = Gtk.Button()
        btClosed.set_icon_name('hs-app-closed')
        btClosed.popover = popover
        btClosed.address = address
        btClosed.connect('clicked', self.on_exec_closedwindow_clicked)
        boxClosed.append(btClosed)
        boxClosed.append(Gtk.Label(label=self.text.get_text('app_closed')))
        popoverBox.append(boxClosed)

        popover.set_child(popoverBox)
        popover.set_parent(self)
        popover.popup()