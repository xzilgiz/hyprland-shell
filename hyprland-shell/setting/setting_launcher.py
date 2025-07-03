import os

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk,Gio,Gdk

from data import DataApps
from modules.apps import Apps
from lang import Lang

class SettingLauncher(Gtk.Box):
    _category_id = 0
    _app_list = []
    _category_list = []

    def lang_init(self):
        self.text = Lang()
        self.text.set_text('ru','name','Приложения')
        self.text.set_text('ru', 'box_add', 'Добавить категорию')
        self.text.set_text('ru', 'button_add', 'Добавить')
        self.text.set_text('ru', 'box_rename', 'Переименовать категорию')
        self.text.set_text('ru', 'button_rename', 'Переименовать')
        self.text.set_text('ru', 'box_remove', 'Удалить категорию')
        self.text.set_text('ru', 'button_remove', 'Удалить')
        self.text.set_text('ru', 'button_up', 'Вверх')
        self.text.set_text('ru', 'button_down', 'Вниз')

        self.text.set_text('en', 'name', 'Applications')
        self.text.set_text('en', 'box_add', 'Add category')
        self.text.set_text('en', 'button_add', 'Add')
        self.text.set_text('en', 'box_rename', 'Rename category')
        self.text.set_text('en', 'button_rename', 'Rename')
        self.text.set_text('en', 'box_remove', 'Remove category')
        self.text.set_text('en', 'button_remove', 'Remove')
        self.text.set_text('en', 'button_up', 'Up')
        self.text.set_text('en', 'button_down', 'Down')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.lang_init()

        SettingLauncher._app_list.clear()
        SettingLauncher._category_list.clear()

        self.name = self.text.get_text('name')
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        ### Макет
        # Категрии верх(категории)-низ(добавить новую, ...)
        category_box = Gtk.CenterBox(orientation=Gtk.Orientation.VERTICAL)
        category_box.add_css_class("setting-launcher-category")

        self.category_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        category_box.set_start_widget(self.category_list_box)
        self.category_action_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        category_box.set_end_widget(self.category_action_box)
        self.append(category_box)

        # Категории тело
        category_body_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.append(category_body_box)

        # Категории тело - заголовок
        self.category_title = Gtk.Label(label='')
        self.category_title.add_css_class("setting-launcher-category")
        category_body_box.append(self.category_title)

        # Приложения список
        self.app_box_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.app_box_list .add_css_class("setting-launcher-app")
        self.app_box_list.props.vexpand = True
        self.app_box_list.props.hexpand = True

        app_box_list_scroll = Gtk.ScrolledWindow()
        app_box_list_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        app_box_list_scroll.set_child(self.app_box_list)
        category_body_box.append(app_box_list_scroll)

        # Категории действия
        #category_body_action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        #category_body_action_box.add_css_class("setting-launcher-category")
        #category_body_box.append(category_body_action_box)

        ### Кнопки
        #Добавление
        box_add_category = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box_add_category.add_css_class("setting-launcher-category")
        box_add_category.append(Gtk.Label(label=self.text.get_text('box_add')))

        self.entry_add_category = Gtk.Entry()
        self.entry_add_category.set_text('')
        box_add_category.append(self.entry_add_category)

        self.button_add_category = Gtk.Button(label=self.text.get_text('button_add'))
        self.button_add_category.connect('clicked', self.on_add_category_clicked)
        box_add_category.append(self.button_add_category)

        self.category_action_box.append(box_add_category)

        # Переименование
        self.box_rename_category = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.box_rename_category.add_css_class("setting-launcher-category")
        self.box_rename_category.append(Gtk.Label(label=self.text.get_text('box_rename')))

        self.entry_rename_category = Gtk.Entry()
        self.entry_rename_category.set_text('')
        self.box_rename_category.append(self.entry_rename_category)

        self.button_rename_category = Gtk.Button(label=self.text.get_text('button_rename'))
        self.button_rename_category.connect('clicked', self.on_rename_category_clicked)
        self.box_rename_category.append(self.button_rename_category)

        self.category_action_box.append(self.box_rename_category)

        # Удаление
        self.box_remove_category = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.box_remove_category.add_css_class("setting-launcher-category")
        self.box_remove_category.append(Gtk.Label(label=self.text.get_text('box_remove')))

        self.button_remove_category = Gtk.Button(label=self.text.get_text('button_remove'))
        self.button_remove_category.connect('clicked', self.on_remove_category_clicked)
        self.box_remove_category.append(self.button_remove_category)

        self.category_action_box.append(self.box_remove_category)

        # Заполняем категории
        self.fill_categories()

    def fill_categories(self):
        for rec in SettingLauncher._category_list:
            self.category_list_box.remove(rec)
        SettingLauncher._category_list.clear()

        for category in DataApps.getCategories():
            button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            button_box.props.hexpand = True

            button_category = Gtk.Button()
            button_category.set_halign(Gtk.Align.FILL)
            button_category.set_hexpand(True)
            button_category.id = category['id']
            button_category.name = category['name']
            button_category.set_label(button_category.name)
            button_category.connect('clicked', self.on_category_clicked)
            button_box.append(button_category)

            button_category_up = Gtk.Button(label=self.text.get_text('button_up'))
            button_category_up.set_icon_name('hs-position-up')
            button_category_up.set_halign(Gtk.Align.END)
            button_category_up.set_hexpand(False)
            button_category_up.id = category['id']
            button_category_up.connect('clicked', self.on_category_up_clicked)
            button_box.append(button_category_up)

            button_category_down = Gtk.Button(label=self.text.get_text('button_down'))
            button_category_down.set_icon_name('hs-position-down')
            button_category_down.set_halign(Gtk.Align.END)
            button_category_down.set_hexpand(False)
            button_category_down.id = category['id']
            button_category_down.connect('clicked', self.on_category_down_clicked)
            button_box.append(button_category_down)

            self.category_list_box.append(button_box)
            SettingLauncher._category_list.append(button_box)

            if SettingLauncher._category_id == category['id']:
                self.fill_apps(category_id=category['id'], category_name=category['name'])

    def on_category_clicked(self, _button):
        self.fill_apps(category_id=_button.id, category_name=_button.name)

    def on_category_up_clicked(self, _button):
        DataApps.moveUpCategory(_button.id)
        self.fill_categories()

    def on_category_down_clicked(self, _button):
        DataApps.moveDownCategory(_button.id)
        self.fill_categories()

    def on_add_category_clicked(self, _button):
        name = self.entry_add_category.get_text().strip()
        if name != '':
            DataApps.setCategory(name=name)
            self.entry_add_category.set_text('')
            self.fill_categories()

    def on_rename_category_clicked(self, _button):
        if SettingLauncher._category_id > 1:
            name = self.entry_rename_category.get_text().strip()
            DataApps.renameCategory(id=SettingLauncher._category_id, name=name)
            self.fill_categories()

    def on_remove_category_clicked(self, _button):
        #Категрию все и избранное удалять нельзя
        if SettingLauncher._category_id > 1:
            DataApps.removeCategory(SettingLauncher._category_id)
            SettingLauncher._category_id = 0
            self.fill_categories()

    def fill_apps(self, category_id, category_name):
        SettingLauncher._category_id = category_id

        self.box_remove_category.set_visible(SettingLauncher._category_id > 1)
        self.box_rename_category.set_visible(SettingLauncher._category_id > 1)

        self.category_title.set_label(category_name)
        self.entry_rename_category.set_text(category_name)

        for rec in SettingLauncher._app_list:
            self.app_box_list.remove(rec)
        SettingLauncher._app_list.clear()

        DataApps.fill_apps()
        for rec in DataApps.get_apps_category(category_id):
            app_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            app_box.id = rec.id
            #В катогории "Все" кнопок сортировок нет, она виртуальная
            if category_id != 0:
                button_app_up = Gtk.Button(label=self.text.get_text('button_up'))
                button_app_up.set_icon_name('hs-position-up')
                button_app_up.id = rec.id
                button_app_up.category_id = category_id
                button_app_up.category_name = category_name

                button_app_up.connect('clicked', self.on_app_up_clicked)
                app_box.append(button_app_up)

                button_app_down = Gtk.Button(label=self.text.get_text('button_down'))
                button_app_down.set_icon_name('hs-position-down')
                button_app_down.id = rec.id
                button_app_down.category_id = category_id
                button_app_down.category_name = category_name
                button_app_down.connect('clicked', self.on_app_down_clicked)
                app_box.append(button_app_down)

            if os.path.isfile(rec.icon):
                icon = Gtk.Image.new_from_file(rec.icon)
            else:
                icon = Gtk.Image.new_from_icon_name(rec.icon)
            app_box.append(icon)

            app_box.append(Gtk.Label(label=rec.name))

            self.app_box_list.append(app_box)
            SettingLauncher._app_list.append(app_box)

    def on_app_up_clicked(self, _button):
        DataApps.moveUpCategoryApp(_button.id, _button.category_id)
        if _button.category_id == 1:
            Apps.refill()
        self.fill_apps(category_id=_button.category_id, category_name=_button.category_name)

    def on_app_down_clicked(self, _button):
        DataApps.moveDownCategoryApp(_button.id, _button.category_id)
        if _button.category_id == 1:
            Apps.refill()
        self.fill_apps(category_id=_button.category_id, category_name=_button.category_name)



