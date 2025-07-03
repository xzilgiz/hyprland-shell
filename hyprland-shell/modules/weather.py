import http.client
import threading
import time
import json
from datetime import datetime

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk,GObject

from data import DataConfig
from lang import Lang

WWO_CODE = {
    "113": "Sunny",
    "116": "Partly cloudy",
    "119": "Cloudy",
    "122": "Very cloudy",
    "143": "Fog",
    "176": "Light showers",
    "179": "Light sleet showers",
    "182": "Light sleet",
    "185": "Light sleet",
    "200": "Thundery showers",
    "227": "Light snow",
    "230": "Heavy snow",
    "248": "Fog",
    "260": "Fog",
    "263": "Light showers",
    "266": "Light rain",
    "281": "Light sleet",
    "284": "Light sleet",
    "293": "Light rain",
    "296": "Light rain",
    "299": "Heavy showers",
    "302": "Heavy rain",
    "305": "Heavy showers",
    "308": "Heavy rain",
    "311": "Light sleet",
    "314": "Light sleet",
    "317": "Light sleet",
    "320": "Light snow",
    "323": "Light snow showers",
    "326": "Light snow showers",
    "329": "Heavy snow",
    "332": "Heavy snow",
    "335": "Heavy snow showers",
    "338": "Heavy snow",
    "350": "Light sleet",
    "353": "Light showers",
    "356": "Heavy showers",
    "359": "Heavy rain",
    "362": "Light sleet showers",
    "365": "Light sleet showers",
    "368": "Light snow showers",
    "371": "Heavy snow showers",
    "374": "Light sleet showers",
    "377": "Light sleet",
    "386": "Thundery showers",
    "389": "Thundery heavy rain",
    "392": "Thundery snow showers",
    "395": "Heavy snow showers",
}

WWO_CODE_RU = {
    "113": "Солнечно",
    "116": "Переменная облачность",
    "119": "Облачно",
    "122": "Очень облачно",
    "143": "Туман",
    "176": "Небольшой ливень",
    "179": "Небольшой ливень",
    "182": "Небольшой ливень",
    "185": "Небольшой ливень",
    "200": "Гроза",
    "227": "Небольшой снегопад",
    "230": "Сильный снегопад",
    "248": "Туман",
    "260": "Туман",
    "263": "Небольшой ливень",
    "266": "Небольшой дождь",
    "281": "Небольшой ливень",
    "284": "Небольшой ливень",
    "293": "Небольшой дождь",
    "296": "Слабый дождь",
    "299": "Сильный ливень",
    "302": "Слабый дождь",
    "305": "Слабый дождь",
    "308": "Слабый дождь",
    "311": "Слабый мокрый снег",
    "314": "Слабый мокрый снег",
    "317": "Слабый мокрый снег",
    "320": "Слабый снег",
    "323": "Слабый мокрый снег",
    "326": "Слабый мокрый снег",
    "329": "Слабый снег",
    "332": "Слабый снег",
    "335": "Слабый мокрый снег",
    "338": "Слабый снег",
    "350": "Слабый мокрый снег",
    "353": "Слабый мокрый снег",
    "356": "Слабый мокрый снег",
    "359": "Сильный дождь",
    "362": "Дождь со снегом",
    "365": "Дождь со снегом",
    "368": "Дождь со снегом",
    "371": "Дождь со снегом",
    "374": "Дождь со снегом",
    "377": "Дождь со снегом",
    "386": "Ливень с грозой",
    "389": "Сильный дождь, гроза",
    "392": "Дождь, гроза, снег",
    "395": "Слабый мокрый снег"
}

#Погода
class WeatherWidget:
    _task = None
    _stop_task = False
    _city = ''
    _data = []
    _current_data = None

    @staticmethod
    def refreshData():
        refresh_time = None
        while True:
            if WeatherWidget._stop_task:
                break
            elif refresh_time is not None and (datetime.now() - refresh_time).total_seconds() < 300:
                time.sleep(1)
                continue

            refresh_time = datetime.now()
            conn = http.client.HTTPSConnection("wttr.in")
            conn.request("GET", f"/{WeatherWidget._city.encode("utf-8")}?format=j1")
            response = conn.getresponse()
            if response.status == 200:
                http_result = response.read().decode("utf-8")

                try:
                    json_result = json.loads(http_result)
                    for weather in json_result['current_condition']:
                        WeatherWidget._current_data = dict(temp=weather['temp_C'], weatherCode=weather['weatherCode'])

                    WeatherWidget._data = []
                    for weather in json_result['weather']:
                        _hour = []
                        for hourly in weather['hourly']:
                            _hour.append(dict(time=hourly['time'], temp=hourly['tempC'], weatherCode=hourly['weatherCode']))

                        _day = dict(date=weather['date'], avgtemp=weather['avgtempC'], hourly=_hour)
                        WeatherWidget._data.append(_day)

                    #print(WeatherWidget._data)
                except Exception as e:
                    print(e)

            conn.close()

    def lang_init(self):
        self.text = Lang()
        self.text.set_text('ru','title','Погода')
        self.text.set_text('ru', 'code', 'ru')
        self.text.set_text('ru', 'avg_temp', 'средняя')
        self.text.set_text('ru', 'night', 'Ночь')
        self.text.set_text('ru', 'morning', 'Утро')
        self.text.set_text('ru', 'day', 'День')
        self.text.set_text('ru', 'evening', 'Вечер')

        self.text.set_text('en','title','Weather')
        self.text.set_text('en', 'code', 'en')
        self.text.set_text('en', 'avg_temp', 'average')
        self.text.set_text('en', 'night', 'Night')
        self.text.set_text('en', 'morning', 'Morning')
        self.text.set_text('en', 'day', 'Day')
        self.text.set_text('en', 'evening', 'Evening')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lang_init()
        self.title = self.text.get_text('title')


        _params = DataConfig.getConfigDockModulParams(modul='Weather')
        city = _params['city']

        if city != WeatherWidget._city and WeatherWidget._task is not None:
            WeatherWidget._stop_task = True
            WeatherWidget._task.join()
            WeatherWidget._task = None

        WeatherWidget._city = city

        if WeatherWidget._task is None:
            WeatherWidget._stop_task = False
            WeatherWidget._task = threading.Thread(target=self.refreshData, daemon=True)
            WeatherWidget._task.start()

    def build_button(self, button_box:Gtk.Box):
        icon = Gtk.Image.new_from_icon_name('hs-weather')
        icon.set_icon_size(Gtk.IconSize.NORMAL)
        button_box.append(icon)

        self.label = Gtk.Label(label='')
        button_box.append(self.label)
        self.refreshInfo()

        GObject.timeout_add(5000, self.refreshInfo)

    def build_window(self, window_box:Gtk.Box):
        group_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        group_box.add_css_class("group-widget-box")

        # Текущая
        temp = WeatherWidget._current_data['temp']
        weatherCode = WeatherWidget._current_data['weatherCode']
        text = self.get_temp_text(temp) + ' ' + self.get_status_text(weatherCode)

        title = Gtk.Label(label=self.title + ' ' + text)
        title.add_css_class("group-widget-title")
        group_box.append(title)

        #На день
        for day in WeatherWidget._data:
            day_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            day_box.add_css_class("widget-weather-day")

            date = day['date']
            avgtemp = day['avgtemp']
            text = date + ' ' + self.text.get_text('avg_temp') + ': ' + self.get_temp_text(avgtemp)
            day_box.append(Gtk.Label(label=text, halign=Gtk.Align.START))

            hour_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            hour_box.add_css_class("widget-weather-hour")
            day_box.append(hour_box)
            for hour in day['hourly']:
                time = hour['time']
                temp = hour['temp']
                weatherCode = hour['weatherCode']

                text = ''
                if time == '0':
                    text = self.text.get_text('night')
                elif time == '600':
                    text = self.text.get_text('morning')
                elif time == '1200':
                    text = self.text.get_text('day')
                elif time == '1800':
                    text = self.text.get_text('evening')
                else:
                    continue

                text = text + ' ' + self.get_temp_text(temp) + ' ' + self.get_status_text(weatherCode)

                hour_box.append(Gtk.Label(label=text, halign=Gtk.Align.START))

            group_box.append(day_box)

        window_box.append(group_box)

    def get_temp_text(self, temp):
        if '-' in temp:
            return temp
        else:
            return '+' + temp

    def get_status_text(self, code):
        if self.text.get_text('code') == 'ru':
            return WWO_CODE_RU[code]
        else:
            return WWO_CODE[code]

    def refreshInfo(self):
        if WeatherWidget._current_data is not None:
            temp = WeatherWidget._current_data['temp']
            weatherCode = WeatherWidget._current_data['weatherCode']
            text = self.get_temp_text(temp) + ' ' +  self.get_status_text(weatherCode)
            self.label.set_label(text)

class Weather(Gtk.Button):
    @staticmethod
    def is_check():
        try:
            conn = http.client.HTTPSConnection("wttr.in")
            conn.request("GET", "/?format=%l:+%t")

            response = conn.getresponse()
            ststus = response.status
            conn.close()
            return ststus == 200
        except:
            return False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_css_class("dock-button")

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.widget = WeatherWidget()
        self.widget.build_button(button_box)
        self.set_child(button_box)

        self.connect('clicked', self.on_info_clicked)

    def on_info_clicked(self, _button):
        window_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.widget.build_window(window_box)

        popover = Gtk.Popover()
        popover.set_child(window_box)
        popover.set_parent(self)
        popover.popup()