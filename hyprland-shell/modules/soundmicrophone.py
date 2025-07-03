import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk,GObject

from ctl import CtlSoundMicrophone
from data import DataConfig
from lang import Lang

class SoundMicrophoneWidget:
    def lang_init(self):
        self.text = Lang()
        self.text.set_text('ru','title','Микрофон')
        self.text.set_text('en','title','Microphone')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lang_init()
        self.title = self.text.get_text('title')

        self.is_mute = False
        self.value = 0
        self.value_timeout_id = 0
        self.iconNameMute = 'hs-microphone-disabled'
        self.iconNameUnMute = 'hs-microphone'

        _params = DataConfig.getConfigDockModulParams(modul='SoundMicrophone')
        self.exec_setting = _params['exec_setting']

    def build_button(self, button_box:Gtk.Box):
        self.icon = Gtk.Image()
        self.icon.set_icon_size(Gtk.IconSize.NORMAL)
        button_box.append(self.icon)
        self.refreshInfo(is_button=True, is_window=False)

    def build_window(self, window_box:Gtk.Box):
        group_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        group_box.add_css_class("group-widget-box")

        title = Gtk.Label(label=self.title)
        title.add_css_class("group-widget-title")
        group_box.append(title)

        line_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.buttonMute = Gtk.Button()
        self.buttonMute.connect('clicked', self.on_button_mute_clicked)
        line_box.append(self.buttonMute)

        self.buttonSetting = Gtk.Button()
        self.buttonSetting.set_icon_name('hs-more-horizontal')
        self.buttonSetting.connect('clicked', self.on_button_setting_clicked)
        line_box.append(self.buttonSetting)

        self.slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0.0, 100.0, 1.0)
        self.slider.set_size_request(200, 0)
        self.slider.connect('value-changed', self.on_slider_changed)
        line_box.append(self.slider)

        self.label = Gtk.Label()
        line_box.append(self.label)

        group_box.append(line_box)

        window_box.append(group_box)

        self.refreshInfo(is_button=True, is_window=True)

    def on_slider_changed(self, slider):
        val = str(int(self.slider.get_value()))
        self.label.set_label(str(val) + '%')

        if self.value_timeout_id == 0:
            self.value_timeout_id = GObject.timeout_add(300, self.refreshValue)

    def on_button_mute_clicked(self, _button):
        CtlSoundMicrophone.exec_toggle_mute()
        self.refreshInfo(is_button=True, is_window=True)

    def on_button_setting_clicked(self, _button):
        CtlSoundMicrophone.exec_setting(exec=self.exec_setting)

    def refreshValue(self):
        GObject.source_remove(self.value_timeout_id)
        self.value = str(int(self.slider.get_value()))

        CtlSoundMicrophone.exec_set_value(self.value)

        self.refreshInfo(is_button=True, is_window=True)
        self.value_timeout_id = 0

        return True

    def refreshButtonInfo(self):
        if self.is_mute:
            self.icon.set_from_icon_name(self.iconNameMute)
        else:
            self.icon.set_from_icon_name(self.iconNameUnMute)

    def refreshWindowInfo(self):
        if self.is_mute:
            self.buttonMute.set_icon_name(self.iconNameUnMute)
        else:
            self.buttonMute.set_icon_name(self.iconNameMute)

        self.slider.set_value(self.value)
        self.label.set_label(str(self.value) + '%')

    def refreshInfo(self, is_button:bool, is_window:bool):
        CtlSoundMicrophone.exec_get()
        self.is_mute = CtlSoundMicrophone.is_mute()
        self.value = CtlSoundMicrophone.get_value()

        if is_button:
            self.refreshButtonInfo()

        if is_window:
            self.refreshWindowInfo()

        return True

class SoundMicrophone(Gtk.Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_css_class("dock-button")

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        window_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.widget = SoundMicrophoneWidget()
        self.widget.build_button(button_box)
        self.widget.build_window(window_box)

        self.set_child(button_box)
        self.popover = Gtk.Popover()
        self.popover.set_child(window_box)
        self.popover.set_parent(self)

        self.connect('clicked', self.on_button_clicked)

    def on_button_clicked(self, _button):
        self.widget.refreshInfo(is_button=True, is_window=True)
        self.popover.popup()
