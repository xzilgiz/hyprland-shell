import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk,Gio,Gdk

from data import DataConfig
from hyprdata import HyprData
from lang import Lang
import dock

class SettingDock(Gtk.Box):
    _dock_list = []
    _dock_id = 0

    #Модули на док панели
    _module_begin_list = []
    _module_center_list = []
    _module_end_list = []

    #Параметры док панели
    _monitor_list = []
    _monitor_exclude_list = []
    _anchor_list = []
    _hmargin = None
    _vmargin = None

    def lang_init(self):
        self.text = Lang()
        self.text.set_text('ru','name','Панели')
        self.text.set_text('ru', 'label_begin', 'Начало')
        self.text.set_text('ru', 'label_center', 'Центр')
        self.text.set_text('ru', 'label_end', 'Конец')
        self.text.set_text('ru', 'label_dock_params', 'Параметры панели')
        self.text.set_text('ru', 'label_monitor', 'Мониторы')
        self.text.set_text('ru', 'label_monitor_exclude', 'Мониторы исключить')
        self.text.set_text('ru', 'label_anchor', 'Расположение')
        self.text.set_text('ru', 'label_hmargin', 'Отступ по горизонтали')
        self.text.set_text('ru', 'label_vmargin', 'Отступ по вертикали')
        self.text.set_text('ru', 'button_add_dock', 'Добавить панель')
        self.text.set_text('ru', 'button_upd_dock', 'Изменить панель')
        self.text.set_text('ru', 'button_remove_dock', 'Удалить панель')
        self.text.set_text('ru', 'value_all', 'Все')
        self.text.set_text('ru', 'value_new', 'Новая')
        self.text.set_text('ru', 'check_top', 'Вверху')
        self.text.set_text('ru', 'check_bottom', 'Внизу')
        self.text.set_text('ru', 'button_up', 'Вверх')
        self.text.set_text('ru', 'button_down', 'Вниз')
        self.text.set_text('ru', 'label_group', 'Группа')
        self.text.set_text('ru', 'button_remove', 'Удалить')
        self.text.set_text('ru', 'button_add', 'Добавить')
        self.text.set_text('ru', 'value_group', 'Групповой')

        self.text.set_text('en','name','Dock panels')
        self.text.set_text('en', 'label_begin', 'Begin')
        self.text.set_text('en', 'label_center', 'Center')
        self.text.set_text('en', 'label_end', 'End')
        self.text.set_text('en', 'label_dock_params', 'Params panel')
        self.text.set_text('en', 'label_monitor', 'Monitors')
        self.text.set_text('en', 'label_monitor_exclude', 'Exclude monitors')
        self.text.set_text('en', 'label_anchor', 'Anchor')
        self.text.set_text('en', 'label_hmargin', 'Horizontal margin')
        self.text.set_text('en', 'label_vmargin', 'Vertical margin')
        self.text.set_text('en', 'button_add_dock', 'Add panel')
        self.text.set_text('en', 'button_upd_dock', 'Change panel')
        self.text.set_text('en', 'button_remove_dock', 'Remove panel')
        self.text.set_text('en', 'value_all', 'All')
        self.text.set_text('en', 'value_new', 'New')
        self.text.set_text('en', 'check_top', 'Top')
        self.text.set_text('en', 'check_bottom', 'Bottom')
        self.text.set_text('en', 'button_up', 'Up')
        self.text.set_text('en', 'button_down', 'Down')
        self.text.set_text('en', 'label_group', 'Group')
        self.text.set_text('en', 'button_remove', 'Remove')
        self.text.set_text('en', 'button_add', 'Add')
        self.text.set_text('en', 'value_group', 'Group')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.lang_init()

        SettingDock._dock_list.clear()
        SettingDock._module_begin_list.clear()
        SettingDock._module_center_list.clear()
        SettingDock._module_end_list.clear()
        SettingDock._monitor_list.clear()
        SettingDock._monitor_exclude_list.clear()
        SettingDock._anchor_list.clear()
        SettingDock._hmargin = None
        SettingDock._vmargin = None

        self.name = self.text.get_text('name')
        self.set_orientation(Gtk.Orientation.HORIZONTAL)

        ### Макет
        # док панели верх(док панели)-низ(добавить новую, ...)
        dock_box = Gtk.CenterBox(orientation=Gtk.Orientation.VERTICAL)
        dock_box.add_css_class("setting-launcher-category")

        self.dock_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        dock_box.set_start_widget(self.dock_list_box)
        self.dock_action_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        dock_box.set_end_widget(self.dock_action_box)
        self.append(dock_box)

        # Док тело
        dock_body_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.append(dock_body_box)

        # Док тело - заголовок
        self.dock_title = Gtk.Label(label='')
        self.dock_title.add_css_class("setting-launcher-category")
        dock_body_box.append(self.dock_title)

        # Модули 3ри позиции
        # Модули список (начало)
        self.modul_begin_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.modul_begin_list.add_css_class("setting-launcher-app")
        self.modul_begin_list.props.vexpand = True
        self.modul_begin_list.props.hexpand = True

        modul_begin_list_scroll = Gtk.ScrolledWindow()
        modul_begin_list_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        modul_begin_list_scroll.set_child(self.modul_begin_list)
        dock_body_box.append(modul_begin_list_scroll)
        self.modul_begin_list.append(Gtk.Label(label=self.text.get_text('label_begin')))

        # Модули список (центер)
        self.modul_center_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.modul_center_list.add_css_class("setting-launcher-app")
        self.modul_center_list.props.vexpand = True
        self.modul_center_list.props.hexpand = True

        modul_center_list_scroll = Gtk.ScrolledWindow()
        modul_center_list_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        modul_center_list_scroll.set_child(self.modul_center_list)
        dock_body_box.append(modul_center_list_scroll)
        self.modul_center_list.append(Gtk.Label(label=self.text.get_text('label_center')))

        # Модули список (конец)
        self.modul_end_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.modul_end_list.add_css_class("setting-launcher-app")
        self.modul_end_list.props.vexpand = True
        self.modul_end_list.props.hexpand = True

        modul_end_list_scroll = Gtk.ScrolledWindow()
        modul_end_list_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        modul_end_list_scroll.set_child(self.modul_end_list)
        dock_body_box.append(modul_end_list_scroll)
        self.modul_end_list.append(Gtk.Label(label=self.text.get_text('label_end')))

        self.build_dock_params()
        self.build_dock_actions()

        # Заполняем док панелей
        self.fill_docks()

    ###### Док
    def build_dock_params(self):
        # Параметры панели
        self.box_dock_params = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.box_dock_params.set_visible(False)
        self.dock_action_box.append(self.box_dock_params)
        self.box_dock_params.add_css_class("setting-launcher-category")
        self.box_dock_params.append(Gtk.Label(label=self.text.get_text('label_dock_params')))

        ##Мониторы
        self.box_dock_param_monitor = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.box_dock_param_monitor.set_margin_bottom(5)
        self.box_dock_param_monitor.set_margin_top(5)
        self.box_dock_param_monitor.append(Gtk.Label(label=self.text.get_text('label_monitor')))
        self.box_dock_params.append(self.box_dock_param_monitor)

        ##Мониторы исключить
        self.box_dock_param_monitor_exclude = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.box_dock_param_monitor_exclude.set_margin_bottom(5)
        self.box_dock_param_monitor_exclude.set_margin_top(5)
        self.box_dock_param_monitor_exclude.append(Gtk.Label(label=self.text.get_text('label_monitor_exclude')))
        self.box_dock_params.append(self.box_dock_param_monitor_exclude)

        ##Расположение
        self.box_dock_param_anchor = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.box_dock_param_anchor.set_margin_bottom(5)
        self.box_dock_param_anchor.set_margin_top(5)
        self.box_dock_param_anchor.append(Gtk.Label(label=self.text.get_text('label_anchor')))
        self.box_dock_params.append(self.box_dock_param_anchor)

        ##Отступ
        self.box_dock_param_hmargin = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.box_dock_param_hmargin.set_margin_bottom(5)
        self.box_dock_param_hmargin.set_margin_top(5)
        self.box_dock_param_hmargin.append(Gtk.Label(label=self.text.get_text('label_hmargin')))
        self.box_dock_params.append(self.box_dock_param_hmargin)

        self.box_dock_param_vmargin = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.box_dock_param_vmargin.set_margin_bottom(5)
        self.box_dock_param_vmargin.set_margin_top(5)
        self.box_dock_param_vmargin.append(Gtk.Label(label=self.text.get_text('label_vmargin')))
        self.box_dock_params.append(self.box_dock_param_vmargin)

    def build_dock_actions(self):
        # Добавление
        self.box_add_dock = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.box_add_dock.add_css_class("setting-launcher-category")
        self.button_add_dock = Gtk.Button(label=self.text.get_text('button_add_dock'))
        self.button_add_dock.connect('clicked', self.on_add_dock_clicked)
        self.box_add_dock.append(self.button_add_dock)
        self.box_add_dock.set_visible(False)
        self.dock_action_box.append(self.box_add_dock)

        # Редактирование
        self.box_upd_dock = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.box_upd_dock.add_css_class("setting-launcher-category")
        self.button_upd_dock = Gtk.Button(label=self.text.get_text('button_upd_dock'))
        self.button_upd_dock.connect('clicked', self.on_upd_dock_clicked)
        self.box_upd_dock.append(self.button_upd_dock)
        self.box_upd_dock.set_visible(False)
        self.dock_action_box.append(self.box_upd_dock)

        # Удаление
        self.box_remove_dock = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.box_remove_dock.add_css_class("setting-launcher-category")
        self.button_remove_dock = Gtk.Button(label=self.text.get_text('button_remove_dock'))
        self.button_remove_dock.connect('clicked', self.on_remove_dock_clicked)
        self.box_remove_dock.append(self.button_remove_dock)
        self.box_remove_dock.set_visible(False)
        self.dock_action_box.append(self.box_remove_dock)

    def fill_docks(self):
        self.dock_title.set_text('')
        for rec in SettingDock._dock_list:
            self.dock_list_box.remove(rec)
        SettingDock._dock_list.clear()

        for dock in DataConfig.getConfigDocksForSetting():
            button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            button_box.props.hexpand = True

            button_dock = Gtk.Button()
            button_dock.set_halign(Gtk.Align.FILL)
            button_dock.set_hexpand(True)
            button_dock.id = dock['id']
            button_dock.monitor = dock['monitor']
            button_dock.monitor_exclude = dock['monitor_exclude']
            button_dock.hmargin = dock['hmargin']
            button_dock.vmargin = dock['vmargin']
            button_dock.layer = dock['layer']
            button_dock.anchor = dock['anchor']
            button_dock.title = 'М:' + (button_dock.monitor if button_dock.monitor != ''  else self.text.get_text('value_all')) + ' A:' + button_dock.anchor

            button_dock.set_label(button_dock.title)
            button_dock.connect('clicked', self.on_dock_clicked)
            button_box.append(button_dock)

            self.dock_list_box.append(button_box)
            SettingDock._dock_list.append(button_box)

            if button_dock.id == SettingDock._dock_id:
              self.dock_title.set_text(button_dock.title)

        #Новая панель
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button_box.props.hexpand = True

        button_dock = Gtk.Button()
        button_dock.set_halign(Gtk.Align.FILL)
        button_dock.set_hexpand(True)
        button_dock.id = -1
        button_dock.title = self.text.get_text('value_new')
        button_dock.set_label(button_dock.title)
        button_dock.connect('clicked', self.on_new_dock_clicked)
        button_box.append(button_dock)
        self.dock_list_box.append(button_box)
        SettingDock._dock_list.append(button_box)

        if button_dock.id == SettingDock._dock_id:
            self.dock_title.set_text(button_dock.title)

        self.fill_dock_params(dock_id=SettingDock._dock_id)
        self.fill_modules(dock_id=SettingDock._dock_id)

    def on_dock_clicked(self, _button):
        self.fill_dock_params(dock_id=_button.id)
        self.fill_modules(dock_id=_button.id)
        self.dock_title.set_text(_button.title)

    def on_new_dock_clicked(self, _button):
        self.fill_dock_params(dock_id=_button.id)
        self.fill_modules(dock_id=_button.id)
        self.dock_title.set_text(_button.title)

    def fill_dock_params(self, dock_id):
        SettingDock._dock_id = dock_id

        self.box_add_dock.set_visible(dock_id == -1)
        self.box_upd_dock.set_visible(dock_id > 0)
        self.box_remove_dock.set_visible(dock_id > 0)
        self.box_dock_params.set_visible(dock_id != 0)

        #Заполняем мониторами
        for rec in SettingDock._monitor_list:
            self.box_dock_param_monitor.remove(rec)
        SettingDock._monitor_list.clear()

        m = Gtk.CheckButton(label=self.text.get_text('value_all'))
        m.monitor = ''
        SettingDock._monitor_list.append(m)
        self.box_dock_param_monitor.append(m)

        for monitor in HyprData.get_monitors():
            m = Gtk.CheckButton(label=monitor['name'])
            m.monitor = monitor['name']
            SettingDock._monitor_list.append(m)
            self.box_dock_param_monitor.append(m)

        #Заполняем мониторами - исключения
        for rec in SettingDock._monitor_exclude_list:
            self.box_dock_param_monitor_exclude.remove(rec)
        SettingDock._monitor_exclude_list.clear()

        for monitor in HyprData.get_monitors():
            m = Gtk.CheckButton(label=monitor['name'])
            m.monitor_exclude = monitor['name']
            SettingDock._monitor_exclude_list.append(m)
            self.box_dock_param_monitor_exclude.append(m)

        #Расположение
        for rec in SettingDock._anchor_list:
            self.box_dock_param_anchor.remove(rec)
        SettingDock._anchor_list.clear()

        radio1 = Gtk.CheckButton(label=self.text.get_text('check_top'))
        radio1.anchor = 'top'
        SettingDock._anchor_list.append(radio1)
        self.box_dock_param_anchor.append(radio1)

        radio2 = Gtk.CheckButton(label=self.text.get_text('check_bottom'))
        radio2.anchor = 'bottom'
        radio2.set_group(radio1)
        SettingDock._anchor_list.append(radio2)
        self.box_dock_param_anchor.append(radio2)

        #Отступ по горизонтали
        if SettingDock._hmargin is not None:
            self.box_dock_param_hmargin.remove(SettingDock._hmargin)
            SettingDock._hmargin = None

        adjustment = Gtk.Adjustment(upper=800, step_increment=1, page_increment=10)
        sb = Gtk.SpinButton()
        sb.props.adjustment = adjustment
        sb.props.numeric = True
        SettingDock._hmargin = sb
        self.box_dock_param_hmargin.append(sb)

        #Отступ по вертикали
        if SettingDock._vmargin is not None:
            self.box_dock_param_vmargin.remove(SettingDock._vmargin)
            SettingDock._vmargin = None

        adjustment = Gtk.Adjustment(upper=50, step_increment=1, page_increment=10)
        sb = Gtk.SpinButton()
        sb.props.adjustment = adjustment
        sb.props.numeric = True
        SettingDock._vmargin = sb
        self.box_dock_param_vmargin.append(sb)

        #Заполняем параметры дока
        if dock_id > 0:
            params = DataConfig.getConfigDockForSetting(config_dock_id=dock_id)
            for rec in SettingDock._monitor_list:
                if rec.monitor in params['monitor'].split(';'):
                    rec.props.active = True

            for rec in SettingDock._monitor_exclude_list:
                if rec.monitor_exclude in params['monitor_exclude'].split(';'):
                    rec.props.active = True

            for rec in SettingDock._anchor_list:
                if rec.anchor == params['anchor']:
                    rec.props.active = True

            SettingDock._hmargin.set_value(params['hmargin'])
            SettingDock._vmargin.set_value(params['vmargin'])

        #Пустые параметры
        elif dock_id == -1:
            pass

    def get_ui_monitors(self):
        result = ''
        for rec in SettingDock._monitor_list:
            if rec.props.active:
                if result != '':
                    result = result + ';'
                result=result + rec.monitor
        return result

    def get_ui_monitor_excludes(self):
        result = ''
        for rec in SettingDock._monitor_exclude_list:
            if rec.props.active:
                if result != '':
                    result = result + ';'
                result=result + rec.monitor_exclude
        return result

    def get_ui_anchor(self):
        result = ''
        for rec in SettingDock._anchor_list:
            if rec.props.active:
                result = rec.anchor
                break
        return result

    def on_add_dock_clicked(self, _button):
        SettingDock._dock_id = DataConfig.addConfigDockForSetting(
            monitor= self.get_ui_monitors(),
            monitor_exclude=self.get_ui_monitor_excludes(),
            hmargin=SettingDock._hmargin.get_value(),
            vmargin=SettingDock._vmargin.get_value(),
            anchor=self.get_ui_anchor())
        self.fill_docks()
        dock.DockBuild.build()

    def on_upd_dock_clicked(self, _button):
        DataConfig.updConfigDockForSetting(
            dock_id=SettingDock._dock_id,
            monitor=self.get_ui_monitors(),
            monitor_exclude=self.get_ui_monitor_excludes(),
            hmargin=SettingDock._hmargin.get_value(),
            vmargin=SettingDock._vmargin.get_value(),
            anchor=self.get_ui_anchor())
        self.fill_docks()
        dock.DockBuild.build()

    def on_remove_dock_clicked(self, _button):
        DataConfig.removeConfigDockForSetting(dock_id=SettingDock._dock_id)
        SettingDock._dock_id = 0
        self.fill_docks()
        dock.DockBuild.build()

    ###### Модули
    def fill_modules(self, dock_id):
        SettingDock._dock_id = dock_id

        for rec in SettingDock._module_begin_list:
            self.modul_begin_list.remove(rec)
        SettingDock._module_begin_list.clear()

        for rec in SettingDock._module_center_list:
            self.modul_center_list.remove(rec)
        SettingDock._module_center_list.clear()

        for rec in SettingDock._module_end_list:
            self.modul_end_list.remove(rec)
        SettingDock._module_end_list.clear()

        for modul in DataConfig.getConfigDockModulesForSetting(dock_id=SettingDock._dock_id):
            _modul = modul['modul']
            _position = modul['position']
            _ordernum = modul['ordernum']
            _groupnum = modul['groupnum']
            _is_group = modul['is_group']

            modul_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            modul_box.modul = _modul

            button_up = Gtk.Button(label=self.text.get_text('button_up'))
            button_up.set_icon_name('hs-position-up')
            button_up.modul = _modul
            button_up.position = _position
            button_up.ordernum = _ordernum
            button_up.groupnum = _groupnum

            button_up.connect('clicked', self.on_up_clicked)
            modul_box.append(button_up)

            button_down = Gtk.Button(label=self.text.get_text('button_down'))
            button_down.set_icon_name('hs-position-down')
            button_down.modul = _modul
            button_down.position = _position
            button_down.ordernum = _ordernum
            button_down.groupnum = _groupnum

            button_down.connect('clicked', self.on_down_clicked)
            modul_box.append(button_down)

            if _is_group:
                modul_box.append(Gtk.Label(label=' '+self.text.get_text('label_group')+':'))
                adjustment = Gtk.Adjustment(upper=5, step_increment=1, page_increment=1)
                button_group = Gtk.SpinButton()
                button_group.props.adjustment = adjustment
                button_group.props.numeric = True
                button_group.set_value(_groupnum)
                button_group.modul = _modul
                button_group.position = _position
                #button_group.ordernum = _ordernum
                #button_group.groupnum = _groupnum
                button_group.connect('value-changed', self.on_group_changed)
                modul_box.append(button_group)

            button_remove = Gtk.Button(label=self.text.get_text('button_remove'))
            button_remove.set_icon_name('hs-list-remove')
            button_remove.modul = _modul
            button_remove.position = _position
            button_remove.ordernum = _ordernum
            button_remove.groupnum = _groupnum

            button_remove.connect('clicked', self.on_remove_clicked)
            modul_box.append(button_remove)

            modul_box.append(Gtk.Label(label=_modul))

            if _position == 'begin':
                self.modul_begin_list.append(modul_box)
                SettingDock._module_begin_list.append(modul_box)
            elif _position == 'center':
                self.modul_center_list.append(modul_box)
                SettingDock._module_center_list.append(modul_box)
            elif _position == 'end':
                self.modul_end_list.append(modul_box)
                SettingDock._module_end_list.append(modul_box)

        if SettingDock._dock_id > 0:
            for rec in ['begin','center','end']:
                add_modul_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

                _position = rec
                button_add = Gtk.Button(label=self.text.get_text('button_add'))
                button_add.set_icon_name('hs-list-add')
                button_add.position = _position
                button_add.connect('clicked', self.on_add_clicked)
                add_modul_box.append(button_add)
                add_modul_box.append(Gtk.Label(label=self.text.get_text('button_add')))

                if _position == 'begin':
                    self.modul_begin_list.append(add_modul_box)
                    SettingDock._module_begin_list.append(add_modul_box)
                elif _position == 'center':
                    self.modul_center_list.append(add_modul_box)
                    SettingDock._module_center_list.append(add_modul_box)
                elif _position == 'end':
                    self.modul_end_list.append(add_modul_box)
                    SettingDock._module_end_list.append(add_modul_box)

    def on_up_clicked(self, _button):
        DataConfig.moveUpConfigDockModuleForSetting(dock_id=SettingDock._dock_id, position=_button.position, modul=_button.modul)
        self.fill_modules(dock_id=SettingDock._dock_id)
        dock.DockBuild.build()

    def on_down_clicked(self, _button):
        DataConfig.moveDownConfigDockModuleForSetting(dock_id=SettingDock._dock_id, position=_button.position, modul=_button.modul)
        self.fill_modules(dock_id=SettingDock._dock_id)
        dock.DockBuild.build()

    def on_group_changed(self, _scroll):
        DataConfig.setGroupnumConfigDockModuleForSetting(dock_id=SettingDock._dock_id, position=_scroll.position, modul=_scroll.modul, groupnum=_scroll.get_value_as_int())
        self.fill_modules(dock_id=SettingDock._dock_id)
        dock.DockBuild.build()

    def on_remove_clicked(self, _button):
        DataConfig.removeConfigDockModuleForSetting(dock_id=SettingDock._dock_id, position=_button.position, modul=_button.modul)
        self.fill_modules(dock_id=SettingDock._dock_id)
        dock.DockBuild.build()

    def on_add_clicked(self, _button):
        popover = Gtk.Popover()
        popoverBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        for rec in DataConfig.getConfigModulesForSetting():
            modul = rec['type']
            is_group = rec['is_group']
            label = modul
            if is_group:
                label = label + ' ('+self.text.get_text('value_group')+')'
            button_modul = Gtk.Button(label=label)
            button_modul.position = _button.position
            button_modul.modul = modul
            button_modul.popover = popover
            button_modul.connect('clicked', self.on_add_modul_clicked)
            popoverBox.append(button_modul)

        modul_end_list_scroll = Gtk.ScrolledWindow()
        modul_end_list_scroll.set_size_request(200,300)
        modul_end_list_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        modul_end_list_scroll.set_child(popoverBox)

        popover.set_child(modul_end_list_scroll)
        popover.set_parent(_button)
        popover.popup()

    def on_add_modul_clicked(self, _button):
        _button.popover.hide()
        DataConfig.addConfigDockModuleForSetting(dock_id=SettingDock._dock_id, position=_button.position, modul=_button.modul)
        self.fill_modules(dock_id=SettingDock._dock_id)
        dock.DockBuild.build()
