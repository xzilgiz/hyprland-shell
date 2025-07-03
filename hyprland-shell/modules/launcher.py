import os

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gtk4LayerShell', '1.0')
from gi.repository import Gtk,Gio,Gdk
from gi.repository import Gtk4LayerShell as LayerShell

from hyprdata import HyprData
from data import DataApps, DataConfig
from modules.apps import Apps
from lang import Lang

#Окно лаунчера
class LauncherWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_css_class("launcher")

        self.set_title('hyprland.shell.launcher')
        self.app_ = self.get_application()
        self.set_default_size(600, 400)

        self.buildWindow()
        self.initLayer()
        self.fillWindow()

    def initLayer(self):
        LayerShell.init_for_window(self)
        LayerShell.set_namespace(self, 'hyprland-shell-launcher')
        LayerShell.set_layer(self, LayerShell.Layer.OVERLAY)
        LayerShell.set_anchor(self, LayerShell.Edge.BOTTOM, True)
        LayerShell.set_anchor(self, LayerShell.Edge.TOP, True)
        LayerShell.set_anchor(self, LayerShell.Edge.LEFT, True)
        LayerShell.set_anchor(self, LayerShell.Edge.RIGHT, True)

        LayerShell.set_margin(self, LayerShell.Edge.BOTTOM, 5)
        LayerShell.set_margin(self, LayerShell.Edge.TOP, 5)
        LayerShell.set_margin(self, LayerShell.Edge.LEFT, 5)
        LayerShell.set_margin(self, LayerShell.Edge.RIGHT, 5)

    def buildWindow(self):
        self.main_box = Gtk.Box.new( Gtk.Orientation.VERTICAL,0)
        self.set_child(self.main_box)

        self.stack = Gtk.Stack.new()
        self.stack.props.hexpand = True
        self.stack.props.vexpand = True

        stack_switcher =  Gtk.StackSwitcher.new()
        stack_switcher.add_css_class('launcher-category')
        stack_switcher.set_orientation(Gtk.Orientation.HORIZONTAL)
        stack_switcher.props.halign = Gtk.Align.CENTER
        stack_switcher.props.hexpand = False
        stack_switcher.props.vexpand = False
        stack_switcher.set_stack(self.stack)

        self.main_box.append(self.stack)
        self.main_box.append(stack_switcher)

    def fillWindow(self):
        self.categoryToflowbox = []
        DataApps.fill_apps()
        for category in DataApps.getCategories():
            categoryId = category['id']
            categoryName = category['name']

            sw = Gtk.ScrolledWindow.new()
            flowbox = Gtk.FlowBox.new()
            sw.set_child(flowbox)
            flowbox.props.homogeneous = True
            flowbox.set_valign(Gtk.Align.START)  # top to bottom
            flowbox.props.margin_start = 10
            flowbox.props.margin_end = 10
            flowbox.props.margin_top = 10
            flowbox.props.margin_bottom = 10
            flowbox.props.hexpand = True
            flowbox.props.vexpand = True
            # flowbox.props.max_children_per_line = 8
            flowbox.props.selection_mode = Gtk.SelectionMode.NONE
            self.stack.add_titled(sw, categoryName, categoryName)  # Widget,name,title to show in Gtk.StackSidebar
            self.categoryToflowbox.append(dict(categoryId=categoryId, categoryName=categoryName, flowbox=flowbox))

            for app in DataApps.get_apps_category(category_id=categoryId):
                flowbox.append(App(
                    window=self,
                    categoryId=categoryId,
                    app=app
                ))

    def setAppCategory(self, app_obj, newCategoryId, action):
        #Делаем перенос в базе
        if action == 'move_category':
            DataApps.setCategoryApp(appId=app_obj.app.id, categoryId=newCategoryId)
        elif action == 'add_favorite':
            DataApps.setFavoriteApp(appId=app_obj.app.id)
        elif action == 'remove_favorite':
            DataApps.removeFavoriteApp(appId=app_obj.app.id)

        #Убираем из категории или избранного
        if action in ('move_category','remove_favorite'):
            for fb in self.categoryToflowbox:
                if fb['categoryId'] == app_obj.categoryId:
                    fb['flowbox'].remove(app_obj)
                    break

        #Добавляем в категорию
        if action == 'move_category':
            for ofb in self.categoryToflowbox:
                if ofb['categoryId'] == newCategoryId:
                    ofb['flowbox'].append(
                        App(window=self,
                            categoryId=newCategoryId,
                            app=app_obj.app))
                    break
        elif action == 'add_favorite':
            for ofb in self.categoryToflowbox:
                if ofb['categoryId'] == 1:
                    ofb['flowbox'].append(
                        App(window=self,
                            categoryId=1,
                            app=app_obj.app))
                    break

        #Если есть панели с избранным, перечитываем их
        if action in ('add_favorite','remove_favorite'):
            Apps.refill()

#Кнопки в лаунчере
class App(Gtk.Button):
    def lang_init(self):
        self.text = Lang()
        self.text.set_text('ru','move_to_category','Перенести в категорию')
        self.text.set_text('ru', 'add_favorite', 'Добавить в избранное')
        self.text.set_text('ru', 'add_action', 'Добавить')
        self.text.set_text('ru', 'remove_favorite', 'Убрать из избранного')
        self.text.set_text('ru', 'remove_action', 'Убрать')

        self.text.set_text('en','move_to_category','Move to category')
        self.text.set_text('en', 'add_favorite', 'Add to favorites')
        self.text.set_text('en', 'add_action', 'Add')
        self.text.set_text('en', 'remove_favorite', 'Remove from favorites')
        self.text.set_text('en', 'remove_action', 'Remove')

    def __init__(self, window, categoryId, app, **kwargs):
        super().__init__(**kwargs)

        self.lang_init()

        self.add_css_class("launcher-app")

        self.window = window
        self.categoryId = categoryId
        self.app = app

        self.box = Gtk.Box()
        self.box.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_child(self.box)

        self.setIcon()
        self.setLabel()

        #Клик левой кнопки мыши
        self.connect('clicked', self.on_exec_clicked)

        #Клик правой кнопки мыши
        gs = Gtk.GestureClick()
        gs.set_button(Gdk.BUTTON_SECONDARY)
        gs.connect('pressed',self.on_exec_secondary_clicked)
        self.add_controller(gs)

    def setIcon(self):
        if os.path.isfile(self.app.icon):
            icon = Gtk.Image.new_from_file(self.app.icon)
        else:
            icon = Gtk.Image.new_from_icon_name(self.app.icon)

        icon.add_css_class('launcher-app-icon')
        self.box.append(icon)

    def setLabel(self):
        label = Gtk.Label(label=self.app.name)
        label.set_margin_top(5)
        self.box.append(label)

    def on_exec_clicked(self, _button):
        HyprData.set_urgent_allowed(True)
        if self.app.terminal:
            os.popen(Launcher._terminal_exec + " " + self.app.exec + " &")
        else:
            os.popen(self.app.exec + " &")
        self.window.close()

    def on_exec_secondary_clicked(self, *args, **kwargs):
        self.showAppMenu()

    def showAppMenu(self):
        popoverBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Если не в избранном
        if self.categoryId != 1:
            ## Перенос в категорию
            categoryBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            #Заголовок
            categoryBox.append(Gtk.Label(label=self.text.get_text('move_to_category')))

            #Кнопки:
            # Имя категорри "ХХХ"
            for category in DataApps.getCategories():
                if self.categoryId != category['id'] and category['id'] != 1:
                    btCategory = Gtk.Button()
                    btCategory.category_id = category['id']
                    btCategory.set_label(category['name'])
                    #btCategory.set_halign(Gtk.Align.FILL)
                    btCategory.connect('clicked', self.on_exec_set_category_clicked)
                    categoryBox.append(btCategory)

            popoverBox.append(categoryBox)

            ## Добавление в избранное
            addFavoriteBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            #Заголовок
            addFavoriteBox.append(Gtk.Label(label=self.text.get_text('add_favorite')))
            #Кнопка
            btAddFavorite = Gtk.Button()
            btAddFavorite.category_id = 1
            btAddFavorite.set_label(self.text.get_text('add_action'))
            # btCategory.set_halign(Gtk.Align.FILL)
            btAddFavorite.connect('clicked', self.on_exec_add_favorite_clicked)
            addFavoriteBox.append(btAddFavorite)

            popoverBox.append(addFavoriteBox)

        else: #Если в избанном
            ## Убрать из избранного
            removeFavoriteBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            #Заголовок
            removeFavoriteBox.append(Gtk.Label(label=self.text.get_text('remove_favorite')))
            #Кнопка
            btRemoveFavorite = Gtk.Button()
            btRemoveFavorite.category_id = 1
            btRemoveFavorite.set_label(self.text.get_text('remove_action'))
            # btCategory.set_halign(Gtk.Align.FILL)
            btRemoveFavorite.connect('clicked', self.on_exec_remove_favorite_clicked)
            removeFavoriteBox.append(btRemoveFavorite)

            popoverBox.append(removeFavoriteBox)

        self.popover = Gtk.Popover()
        self.popover.set_child(popoverBox)
        self.popover.set_parent(self)
        self.popover.popup()

    def on_exec_set_category_clicked(self, _button):
        self.window.setAppCategory(app_obj=self, newCategoryId=_button.category_id, action='move_category')

    def on_exec_add_favorite_clicked(self, _button):
        self.window.setAppCategory(app_obj=self, newCategoryId=None, action='add_favorite')
        self.popover.hide()

    def on_exec_remove_favorite_clicked(self, _button):
        self.window.setAppCategory(app_obj=self, newCategoryId=None, action='remove_favorite')

#Класс кнопки лаунчера для док панели
class Launcher(Gtk.Box):
    _terminal_exec = ''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_css_class("apps") #app-launcher

        _params = DataConfig.getConfigBaseParams()
        Launcher._terminal_exec = _params['terminal_exec']

        bt = Gtk.Button()
        bt.add_css_class("app")
        icon = Gtk.Image.new_from_icon_name('hs-launcher')
        icon.set_icon_size(Gtk.IconSize.LARGE)
        bt.set_child(icon)
        bt.connect('clicked', self.on_launcher_clicked)
        self.append(bt)

    def on_launcher_clicked(self, _button):
        if not hasattr(self, 'lau') or not self.lau.get_visible():
            self.lau = LauncherWindow()
            self.lau.present()
        else:
            self.lau.close()
