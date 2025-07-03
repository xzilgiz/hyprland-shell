import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk,Gio,Gdk

from data import DataConfig
from lang import Lang
import dock

class SettingModules(Gtk.Box):
    _modul = ''
    _modul_list = []
    _modul_param_list = []
    _modul_action_list = []

    def lang_init(self):
        self.text = Lang()
        self.text.set_text('ru','name','Модули')
        self.text.set_text('ru', 'button_save', 'Применить')
        self.text.set_text('ru', 'button_reset', 'Сбросить')
        self.text.set_text('ru', 'label_clock_mask_date', 'Маска даты')
        self.text.set_text('ru', 'label_clock_mask_time', 'Маска часов')
        self.text.set_text('ru', 'label_apps_is_active', 'Показывать активные (не избранные) приложения')
        self.text.set_text('ru', 'label_workspaces_is_active', 'Показывать активные приложения на рабочем столе')
        self.text.set_text('ru', 'label_workspaces_style', 'Стиль')
        self.text.set_text('ru', 'value_workspaces_circle', 'Кружки')
        self.text.set_text('ru', 'value_workspaces_number', 'Числа')
        self.text.set_text('ru', 'label_sound_exec_setting', 'Комманда запуска приложения для дополнительных настроек')
        self.text.set_text('ru', 'label_weather_city', 'Город')

        self.text.set_text('en','name','Modules')
        self.text.set_text('en', 'button_save', 'Apply')
        self.text.set_text('en', 'button_reset', 'Reset')
        self.text.set_text('en', 'label_clock_mask_date', 'Date mask')
        self.text.set_text('en', 'label_clock_mask_time', 'Watch mask')
        self.text.set_text('en', 'label_apps_is_active', 'Show active (non-favorite) applications')
        self.text.set_text('en', 'label_workspaces_is_active', 'Show active applications on desktop')
        self.text.set_text('en', 'label_workspaces_style', 'Style')
        self.text.set_text('en', 'value_workspaces_circle', 'Circles')
        self.text.set_text('en', 'value_workspaces_number', 'Numbers')
        self.text.set_text('en', 'label_sound_exec_setting', 'Command to launch the application for additional settings')
        self.text.set_text('en', 'label_weather_city', 'City')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.lang_init()

        SettingModules._modul_list.clear()
        SettingModules._modul_param_list.clear()
        SettingModules._modul_action_list.clear()

        self.name = self.text.get_text('name')
        self.set_orientation(Gtk.Orientation.HORIZONTAL)

        ### Макет
        # модули верх(модули)-низ(сохранить)
        modul_box = Gtk.CenterBox(orientation=Gtk.Orientation.VERTICAL)
        modul_box.add_css_class("setting-launcher-category")

        self.modul_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        modul_box.set_start_widget(self.modul_list_box)
        self.modul_action_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        modul_box.set_end_widget(self.modul_action_box)
        self.append(modul_box)

        # Модуль тело
        modul_body_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.append(modul_body_box)

        # Модуль тело - заголовок
        self.modul_title = Gtk.Label(label='')
        self.modul_title.add_css_class("setting-launcher-category")
        modul_body_box.append(self.modul_title)

        # Модуль параметры
        modul_params_box = Gtk.CenterBox(orientation=Gtk.Orientation.VERTICAL)
        modul_params_box.props.vexpand = True
        modul_params_box.props.hexpand = True
        modul_body_box.append(modul_params_box)

        # Параметры
        self.modul_params = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.modul_params.add_css_class("setting-launcher-app")
        self.modul_params.props.vexpand = True
        self.modul_params.props.hexpand = True
        modul_params_box.set_start_widget(self.modul_params)

        # Кнопки
        self.modul_action = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.modul_action.add_css_class("setting-section-list")
        modul_params_box.set_end_widget(self.modul_action)

        self.fill_modules()

    def fill_modules(self):
        self.modul_title.set_text('')

        for modul in DataConfig.getConfigModulesForSettingModules():
            button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            button_box.props.hexpand = True

            button = Gtk.Button()
            button.set_halign(Gtk.Align.FILL)
            button.set_hexpand(True)
            button.modul = modul
            button.title = modul

            button.set_label(button.title)
            button.connect('clicked', self.on_modul_clicked)
            button_box.append(button)

            self.modul_list_box.append(button_box)
            SettingModules._modul_list.append(button_box)

            if button.modul == SettingModules._modul:
                self.modul_title.set_text(button.title)
                self.fill_modul_params(modul=SettingModules._modul)

    def on_modul_clicked(self, _button):
        self.modul_title.set_text(_button.title)
        self.fill_modul_params(modul=_button.modul)

    def set_param_label(self, text:str):
        lb = Gtk.Label(label=text)
        lb.field = ''
        lb.set_margin_top(10)
        SettingModules._modul_param_list.append(lb)
        self.modul_params.append(lb)

    def set_param_entry(self, field:str, value:str):
        entry = Gtk.Entry()
        entry.field = field
        entry.set_text(value)
        SettingModules._modul_param_list.append(entry)
        self.modul_params.append(entry)

    def get_param_entry(self, field:str) -> str:
        for rec in SettingModules._modul_param_list:
            if rec.field == field:
                return rec.get_text()

    def set_check_button(self, field:str, value:bool, label:str):
        cb = Gtk.CheckButton(label=label)
        cb.field = field
        cb.props.active = value
        SettingModules._modul_param_list.append(cb)
        self.modul_params.append(cb)

    def get_check_button(self, field: str) -> bool:
        for rec in SettingModules._modul_param_list:
            if rec.field == field:
                return rec.props.active

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

            SettingModules._modul_param_list.append(cb)
            self.modul_params.append(cb)

    def get_radio_button(self, field: str) -> str:
        for rec in SettingModules._modul_param_list:
            if rec.field == field and rec.props.active:
                return rec.value

    def set_action_buttons(self, modul:str):
        button = Gtk.Button(label=self.text.get_text('button_save'))
        button.connect('clicked', self.on_save_clicked)

        self.modul_action.append(button)
        SettingModules._modul_action_list.append(button)

        button = Gtk.Button(label=self.text.get_text('button_reset'))
        button.connect('clicked', self.on_reset_clicked)

        self.modul_action.append(button)
        SettingModules._modul_action_list.append(button)

    def on_save_clicked(self, _button):
        self.save_modul_params()
        dock.DockBuild.build()

    def on_reset_clicked(self, _button):
        self.fill_modul_params(modul=SettingModules._modul)

    def fill_modul_params(self, modul:str):
        SettingModules._modul = modul

        for rec in SettingModules._modul_param_list:
            self.modul_params.remove(rec)
        SettingModules._modul_param_list.clear()

        for rec in SettingModules._modul_action_list:
            self.modul_action.remove(rec)
        SettingModules._modul_action_list.clear()

        _params = DataConfig.getConfigDockModulParams(modul=modul)
        if modul == 'Clock':
            mask_date = _params['mask_date']
            mask_time = _params['mask_time']

            self.set_param_label(text=self.text.get_text('label_clock_mask_date'))
            self.set_param_entry(field='mask_date', value=mask_date)

            self.set_param_label(text=self.text.get_text('label_clock_mask_time'))
            self.set_param_entry(field='mask_time', value=mask_time)
        elif modul == 'Apps':
            is_active = _params['is_active']
            self.set_check_button(field='is_active', value=is_active, label=self.text.get_text('label_apps_is_active'))

        elif modul == 'Workspaces':
            is_active = _params['is_active']
            style = _params['style']

            self.set_check_button(field='is_active', value=is_active, label=self.text.get_text('label_workspaces_is_active'))

            self.set_param_label(text=self.text.get_text('label_workspaces_style'))
            items = []
            items.append(dict(value='circle', label=self.text.get_text('value_workspaces_circle')))
            items.append(dict(value='number', label=self.text.get_text('value_workspaces_number')))
            self.set_radio_button(field='style', value=style, items=items)

        elif modul == 'SoundVolume':
            exec_setting = _params['exec_setting']
            self.set_param_label(text=self.text.get_text('label_sound_exec_setting'))
            self.set_param_entry(field='exec_setting', value=exec_setting)

        elif modul == 'SoundMicrophone':
            exec_setting = _params['exec_setting']
            self.set_param_label(text=self.text.get_text('label_sound_exec_setting'))
            self.set_param_entry(field='exec_setting', value=exec_setting)

        elif modul == 'Weather':
            exec_setting = _params['city']
            self.set_param_label(text=self.text.get_text('label_weather_city'))
            self.set_param_entry(field='city', value=exec_setting)

        self.set_action_buttons(modul=modul)

    def save_modul_params(self):
        if SettingModules._modul == 'Clock':
            DataConfig.setConfigModulClockForSettingModules(
                mask_date=self.get_param_entry(field='mask_date'),
                mask_time=self.get_param_entry(field='mask_time'))

        elif SettingModules._modul == 'Apps':
            DataConfig.setConfigModulAppsForSettingModules(
                is_active=self.get_check_button(field='is_active'))

        elif SettingModules._modul == 'Workspaces':
            DataConfig.setConfigModulWorkspacesForSettingModules(
                is_active=self.get_check_button(field='is_active'),
                style=self.get_radio_button(field='style'))

        elif SettingModules._modul == 'SoundVolume':
            DataConfig.setConfigModulSoundVolumeForSettingModules(
                exec_setting=self.get_param_entry(field='exec_setting'))

        elif SettingModules._modul == 'SoundMicrophone':
            DataConfig.setConfigModulSoundMicrophoneForSettingModules(
                exec_setting=self.get_param_entry(field='exec_setting'))

        elif SettingModules._modul == 'Weather':
            DataConfig.setConfigModulWeatherForSettingModules(
                city=self.get_param_entry(field='city'))