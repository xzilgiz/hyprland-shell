import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from setting.setting import SettingWindow
from lang import Lang

class SettingWidget:
    def lang_init(self):
        self.text = Lang()
        self.text.set_text('ru','title','Настройки')
        self.text.set_text('en','title','Setting')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lang_init()
        self.title = self.text.get_text('title')

    def build_button(self, button_box:Gtk.Box):
        icon = Gtk.Image.new_from_icon_name('hs-more-horizontal')
        icon.set_icon_size(Gtk.IconSize.NORMAL)
        button_box.append(icon)

    def build_window(self, window_box:Gtk.Box):
        group_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        group_box.add_css_class("group-widget-box")
        group_box.append(Setting(is_group_widget=True))
        group_box.append(Gtk.Label(label=self.title))
        window_box.append(group_box)

class Setting(Gtk.Button):
    _instans = None
    def __init__(self, is_group_widget:bool = False, **kwargs):
        super().__init__(**kwargs)
        if not is_group_widget:
            self.add_css_class("dock-button")

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        self.widget = SettingWidget()
        self.widget.build_button(button_box)
        self.set_child(button_box)

        self.connect('clicked', self.on_setting_clicked)

    def on_setting_clicked(self, _button):
        if Setting._instans is None or not Setting._instans.get_visible():
            Setting._instans = SettingWindow()
            Setting._instans.present()
        else:
            Setting._instans.close()
