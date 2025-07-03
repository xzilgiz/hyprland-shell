import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk,Gio,Gdk

from data import DataConfig
from lang import Lang
import dock

class SettingBase(Gtk.Box):
    _base_param_list = []
    _base_action_list = []

    def lang_init(self):
        self.text = Lang()
        self.text.set_text('ru','name','Базовые настройки')
        self.text.set_text('ru', 'label_terminal', 'Терминал')
        self.text.set_text('ru', 'label_theme', 'Тема')
        self.text.set_text('ru', 'value_dark', 'Темная')
        self.text.set_text('ru', 'value_light', 'Светлая')
        self.text.set_text('ru', 'label_language', 'Язык')
        self.text.set_text('ru', 'button_save', 'Применить')
        self.text.set_text('ru', 'button_reset', 'Сбросить')

        self.text.set_text('en', 'name', 'Base setting')
        self.text.set_text('en', 'label_terminal', 'Terminal')
        self.text.set_text('en', 'label_theme', 'Theme')
        self.text.set_text('en', 'value_dark', 'Dark')
        self.text.set_text('en', 'value_light', 'Light')
        self.text.set_text('en', 'label_language', 'Language')
        self.text.set_text('en', 'button_save', 'Apply')
        self.text.set_text('en', 'button_reset', 'Reset')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lang_init()

        SettingBase._base_param_list.clear()
        SettingBase._base_action_list.clear()

        self.name = self.text.get_text('name')
        self.set_orientation(Gtk.Orientation.HORIZONTAL)

        ### Макет
        # Модуль тело
        base_body_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.append(base_body_box)

        # Модуль тело - заголовок
        self.base_title = Gtk.Label(label='')
        self.base_title.add_css_class("setting-launcher-category")
        base_body_box.append(self.base_title)

        # Модуль параметры
        base_params_box = Gtk.CenterBox(orientation=Gtk.Orientation.VERTICAL)
        base_params_box.props.vexpand = True
        base_params_box.props.hexpand = True
        base_body_box.append(base_params_box)

        # Параметры
        self.base_params = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.base_params.add_css_class("setting-launcher-app")
        self.base_params.props.vexpand = True
        self.base_params.props.hexpand = True
        base_params_box.set_start_widget(self.base_params)

        # Кнопки
        self.base_action = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.base_action.add_css_class("setting-section-list")
        base_params_box.set_end_widget(self.base_action)

        self.fill_params()

    def fill_params(self):
        for rec in SettingBase._base_param_list:
            self.base_params.remove(rec)
        SettingBase._base_param_list.clear()

        for rec in SettingBase._base_action_list:
            self.base_action.remove(rec)
        SettingBase._base_action_list.clear()

        _params = DataConfig.getConfigBaseParams()

        terminal_exec = _params['terminal_exec']
        theme = _params['theme']
        language = _params['language']

        self.set_param_label(text=self.text.get_text('label_terminal'))
        self.set_param_entry(field='terminal_exec', value=terminal_exec)

        self.set_param_label(text=self.text.get_text('label_theme'))
        items = []
        items.append(dict(value='dark', label=self.text.get_text('value_dark')))
        items.append(dict(value='light', label=self.text.get_text('value_light')))
        self.set_radio_button(field='theme', value=theme, items=items)

        self.set_param_label(text=self.text.get_text('label_language'))
        items = []
        items.append(dict(value='ru', label='Русский'))
        items.append(dict(value='en', label='English'))
        self.set_radio_button(field='language', value=language, items=items)

        self.set_action_buttons()

    def save_params(self):
        DataConfig.updConfigBaseParams(
            terminal_exec=self.get_param_entry(field='terminal_exec'),
            theme=self.get_radio_button(field='theme'),
            language=self.get_radio_button(field='language'))

    def set_param_label(self, text:str):
        lb = Gtk.Label(label=text)
        lb.field = ''
        lb.set_margin_top(10)
        SettingBase._base_param_list.append(lb)
        self.base_params.append(lb)

    def set_param_entry(self, field:str, value:str):
        entry = Gtk.Entry()
        entry.field = field
        entry.set_text(value)
        SettingBase._base_param_list.append(entry)
        self.base_params.append(entry)

    def get_param_entry(self, field:str) -> str:
        for rec in SettingBase._base_param_list:
            if rec.field == field:
                return rec.get_text()

    def set_radio_button(self, field:str, value:bool, items:list):
        parent_cb = None
        for item in items:
            cb = Gtk.CheckButton(label=item['label'])
            cb.field = field
            cb.value = item['value']
            cb.props.active = cb.value == value

            if parent_cb is None:
                parent_cb = cb
            else:
                cb.set_group(parent_cb)

            SettingBase._base_param_list.append(cb)
            self.base_params.append(cb)

    def get_radio_button(self, field: str) -> str:
        for rec in SettingBase._base_param_list:
            if rec.field == field and rec.props.active:
                return rec.value

    def set_action_buttons(self):
        button = Gtk.Button(label=self.text.get_text('button_save'))
        button.connect('clicked', self.on_save_clicked)

        self.base_action.append(button)
        SettingBase._base_action_list.append(button)

        button = Gtk.Button(label=self.text.get_text('button_reset'))
        button.connect('clicked', self.on_reset_clicked)

        self.base_action.append(button)
        SettingBase._base_action_list.append(button)

    def on_save_clicked(self, _button):
        self.save_params()
        dock.DockBuild.build()

    def on_reset_clicked(self, _button):
        self.fill_params()