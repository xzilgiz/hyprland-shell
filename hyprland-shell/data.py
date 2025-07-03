import sqlite3
import os
import locale
from dataclasses import dataclass, field

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gio

from hyprdata import HyprData

@dataclass
class Category:
    id: int = ''
    name: str = ''
    ordernum: int = 0

@dataclass
class Active:
    address: str = ''
    workspace: str = ''
    title: str = ''

@dataclass
class App:
    id: str = ''
    name: str = ''
    icon: str = ''
    exec: str = ''
    terminal: bool = False
    categories: list[Category] = field(default_factory=list)  # id name ordernum
    actives: list[Active] = field(default_factory=list)  # address workspace

    def __post_init__(self):
        self.categories = []
        self.actives = []

    def is_active(self):
        return self.actives != []

    def is_favorite(self):
        if self.categories == []:
            return False

        for cat in self.categories:
            if cat.id == 1:
                return True

        return False

class DataApps:
    _apps = []

    @staticmethod
    def getConnect():
        home_directory = os.getenv("HOME")
        configPath = home_directory + '/.config/hyprland-shell'
        if not os.path.exists(configPath):
          os.mkdir(configPath)
        dbPath = configPath + '/DataApps.db'

        return sqlite3.connect(dbPath)

    @staticmethod
    def createDataBase():
        _params = DataConfig.getConfigBaseParams()
        language = _params['language']

        # Устанавливаем соединение с базой данных
        connection = DataApps.getConnect()

        # Создаём таблицы если их нет
        cursor = connection.cursor()
        sql = '''
           CREATE TABLE IF NOT EXISTS CATEGORY (
             ID          INT NOT NULL PRIMARY KEY,
             NAME        TEXT NOT NULL,
             ORDERNUM    INT);
           '''
        cursor.execute(sql)

        sql = '''
            INSERT INTO CATEGORY(ID, NAME, ORDERNUM)
            VALUES(?, ?, ?)
            ON CONFLICT(ID) DO NOTHING;
            '''
        if language == 'ru':
            params = (0, 'Все', 0)
            cursor.execute(sql, params)
            params = (1, 'Избранное', 1)
            cursor.execute(sql, params)
            params = (2, 'Игры', 2)
            cursor.execute(sql, params)
            params = (3, 'Утилиты', 3)
            cursor.execute(sql, params)
            params = (4, 'Мультимедия', 4)
            cursor.execute(sql, params)
            params = (5, 'Коммуникации', 5)
            cursor.execute(sql, params)
        else:
            params = (0, 'All', 0)
            cursor.execute(sql, params)
            params = (1, 'Favorites', 1)
            cursor.execute(sql, params)
            params = (2, 'Games', 2)
            cursor.execute(sql, params)
            params = (3, 'Utils', 3)
            cursor.execute(sql, params)
            params = (4, 'Multimedia', 4)
            cursor.execute(sql, params)
            params = (5, 'Communications', 5)
            cursor.execute(sql, params)

        sql = '''
           CREATE TABLE IF NOT EXISTS APP_CATEGORY (
             ID          TEXT NOT NULL,
             CATEGORY_ID INT NOT NULL,
             ORDERNUM    INT,
             PRIMARY KEY(ID, CATEGORY_ID));
           '''
        cursor.execute(sql)

        # Сохраняем изменения и закрываем соединение
        connection.commit()
        connection.close()

    @staticmethod
    def setCategoryApp(appId, categoryId):
        connection = DataApps.getConnect()
        cursor = connection.cursor()

        sql = '''
            DELETE FROM APP_CATEGORY WHERE ID = ? AND CATEGORY_ID <> 1;
            '''
        params = (appId,)
        cursor.execute(sql, params)

        if categoryId != 0:
            sql = 'SELECT COALESCE(MAX(ORDERNUM), 0) + 1 FROM APP_CATEGORY WHERE CATEGORY_ID = ?;'
            params = (categoryId,)
            cursor.execute(sql, params)
            next_ordernum = 0
            for rec in cursor.fetchall():
                next_ordernum = rec[0]

            sql = 'INSERT INTO APP_CATEGORY(ID, CATEGORY_ID, ORDERNUM) VALUES(?, ?, ?);'

            params = (appId, categoryId, next_ordernum)
            cursor.execute(sql, params)

        connection.commit()
        connection.close()

    @staticmethod
    def setFavoriteApp(appId):
        connection = DataApps.getConnect()
        cursor = connection.cursor()

        sql = 'DELETE FROM APP_CATEGORY WHERE ID = ? AND CATEGORY_ID = 1;'
        params = (appId,)
        cursor.execute(sql, params)

        sql = 'SELECT COALESCE(MAX(ORDERNUM), 0) + 1 FROM APP_CATEGORY WHERE CATEGORY_ID = 1;'
        cursor.execute(sql)
        next_ordernum = 0
        for rec in cursor.fetchall():
            next_ordernum = rec[0]

        sql = 'INSERT INTO APP_CATEGORY(ID, CATEGORY_ID, ORDERNUM) VALUES(?, 1, ?);'
        params = (appId, next_ordernum)
        cursor.execute(sql, params)

        connection.commit()
        connection.close()

    @staticmethod
    def removeFavoriteApp(appId):
        connection = DataApps.getConnect()
        cursor = connection.cursor()

        sql = 'DELETE FROM APP_CATEGORY WHERE ID = ? AND CATEGORY_ID = 1;'
        params = (appId,)
        cursor.execute(sql, params)

        connection.commit()
        connection.close()

    @staticmethod
    def getCategories():
        result = []

        connection = DataApps.getConnect()
        cursor = connection.cursor()
        cursor.execute('SELECT ID, NAME FROM CATEGORY ORDER BY ORDERNUM')
        categoryList = cursor.fetchall()
        connection.close()

        for category in categoryList:
            d = dict(id=category[0], name=category[1])
            result.append(d)

        return result

    @staticmethod
    def setCategory(name):
        connection = DataApps.getConnect()
        cursor = connection.cursor()

        sql = '''
            INSERT INTO CATEGORY(ID, NAME, ORDERNUM)
            VALUES((SELECT MAX(ID)+1 FROM CATEGORY), ?, (SELECT MAX(ORDERNUM)+1 FROM CATEGORY));
            '''

        params = (name,)
        cursor.execute(sql, params)
        connection.commit()
        connection.close()

    @staticmethod
    def renameCategory(id, name):
        connection = DataApps.getConnect()
        cursor = connection.cursor()

        sql = 'UPDATE CATEGORY SET NAME = ? WHERE ID = ?;'

        params = (name, id)
        cursor.execute(sql, params)
        connection.commit()
        connection.close()

    @staticmethod
    def removeCategory(id):
        connection = DataApps.getConnect()
        cursor = connection.cursor()

        sql = 'DELETE FROM APP_CATEGORY WHERE CATEGORY_ID = ?;'
        params = (id,)
        cursor.execute(sql, params)

        sql = 'DELETE FROM CATEGORY WHERE ID = ?;'
        params = (id,)
        cursor.execute(sql, params)

        connection.commit()
        connection.close()

    @staticmethod
    def moveUpCategory(id):
        connection = DataApps.getConnect()
        cursor = connection.cursor()

        #Текущая позиция
        sql = 'SELECT ORDERNUM FROM CATEGORY WHERE ID = ?;'
        params = (id,)
        cursor.execute(sql, params)
        cur_ordernum = 0
        for rec in cursor.fetchall():
            cur_ordernum = rec[0]

        #Поиск позиции и группы для обмена
        sql = 'SELECT ID, ORDERNUM FROM CATEGORY WHERE ORDERNUM < ? ORDER BY ORDERNUM DESC;'
        params = (cur_ordernum,)
        cursor.execute(sql, params)
        move_id = -999
        move_ordernum = -999
        for rec in cursor.fetchall():
            move_id = rec[0]
            move_ordernum = rec[1]
            break

        if move_ordernum != -999 and move_id != -999:
            sql = 'UPDATE CATEGORY SET ORDERNUM = ? WHERE ID = ?;'
            params = (move_ordernum, id)
            cursor.execute(sql, params)

            sql = 'UPDATE CATEGORY SET ORDERNUM = ? WHERE ID = ?;'
            params = (cur_ordernum, move_id)
            cursor.execute(sql, params)

        connection.commit()
        connection.close()

    @staticmethod
    def moveDownCategory(id):
        connection = DataApps.getConnect()
        cursor = connection.cursor()

        # Текущая позиция
        sql = 'SELECT ORDERNUM FROM CATEGORY WHERE ID = ?;'
        params = (id,)
        cursor.execute(sql, params)
        cur_ordernum = 0
        for rec in cursor.fetchall():
            cur_ordernum = rec[0]

        # Поиск позиции и группы для обмена
        sql = 'SELECT ID, ORDERNUM FROM CATEGORY WHERE ORDERNUM > ? ORDER BY ORDERNUM;'
        params = (cur_ordernum,)
        cursor.execute(sql, params)
        move_id = -999
        move_ordernum = -999
        for rec in cursor.fetchall():
            move_id = rec[0]
            move_ordernum = rec[1]
            break

        if move_ordernum != -999 and move_id != -999:
            sql = 'UPDATE CATEGORY SET ORDERNUM = ? WHERE ID = ?;'
            params = (move_ordernum, id)
            cursor.execute(sql, params)

            sql = 'UPDATE CATEGORY SET ORDERNUM = ? WHERE ID = ?;'
            params = (cur_ordernum, move_id)
            cursor.execute(sql, params)

        connection.commit()
        connection.close()

    @staticmethod
    def moveUpCategoryApp(appId, categoryId):
        connection = DataApps.getConnect()
        cursor = connection.cursor()

        # Текущая позиция
        sql = 'SELECT ORDERNUM FROM APP_CATEGORY WHERE ID = ? AND CATEGORY_ID = ?;'
        params = (appId, categoryId)
        cursor.execute(sql, params)
        cur_ordernum = 0
        for rec in cursor.fetchall():
            cur_ordernum = rec[0]

        # Поиск позиции и группы для обмена
        sql = 'SELECT ID, ORDERNUM FROM APP_CATEGORY WHERE CATEGORY_ID = ? AND ORDERNUM < ? ORDER BY ORDERNUM DESC;'
        params = (categoryId, cur_ordernum)
        cursor.execute(sql, params)
        move_appid = -999
        move_ordernum = -999
        for rec in cursor.fetchall():
            move_appid = rec[0]
            move_ordernum = rec[1]
            break

        if move_ordernum != -999 and move_appid != -999:
            sql = 'UPDATE APP_CATEGORY SET ORDERNUM = ? WHERE ID = ? AND CATEGORY_ID = ?;'
            params = (move_ordernum, appId, categoryId)
            cursor.execute(sql, params)

            sql = 'UPDATE APP_CATEGORY SET ORDERNUM = ? WHERE ID = ? AND CATEGORY_ID = ?;'
            params = (cur_ordernum, move_appid, categoryId)
            cursor.execute(sql, params)

        connection.commit()
        connection.close()

    @staticmethod
    def moveDownCategoryApp(appId, categoryId):
        connection = DataApps.getConnect()
        cursor = connection.cursor()

        # Текущая позиция
        sql = 'SELECT ORDERNUM FROM APP_CATEGORY WHERE ID = ? AND CATEGORY_ID = ?;'
        params = (appId, categoryId)
        cursor.execute(sql, params)
        cur_ordernum = 0
        for rec in cursor.fetchall():
            cur_ordernum = rec[0]

        # Поиск позиции и группы для обмена
        sql = 'SELECT ID, ORDERNUM FROM APP_CATEGORY WHERE CATEGORY_ID = ? AND ORDERNUM > ? ORDER BY ORDERNUM;'
        params = (categoryId, cur_ordernum)
        cursor.execute(sql, params)
        move_appid = -999
        move_ordernum = -999
        for rec in cursor.fetchall():
            move_appid = rec[0]
            move_ordernum = rec[1]
            break

        if move_ordernum != -999 and move_appid != -999:
            sql = 'UPDATE APP_CATEGORY SET ORDERNUM = ? WHERE ID = ? AND CATEGORY_ID = ?;'
            params = (move_ordernum, appId, categoryId)
            cursor.execute(sql, params)

            sql = 'UPDATE APP_CATEGORY SET ORDERNUM = ? WHERE ID = ? AND CATEGORY_ID = ?;'
            params = (cur_ordernum, move_appid, categoryId)
            cursor.execute(sql, params)

        connection.commit()
        connection.close()

    @staticmethod
    def getAppToCategories():
        result = []

        connection = DataApps.getConnect()
        cursor = connection.cursor()
        cursor.execute(
            'SELECT A.ID AS APP_ID, A.CATEGORY_ID, C.NAME AS CATEGORY_NAME, A.ORDERNUM FROM APP_CATEGORY A JOIN CATEGORY C ON C.ID = A.CATEGORY_ID ORDER BY C.ORDERNUM, A.ORDERNUM')
        appToCategories = cursor.fetchall()
        connection.close()

        for rec in appToCategories:
            d = dict(app_id=rec[0], category_id=rec[1], category_name=rec[2], ordernum=rec[3])
            result.append(d)

        return result

    @staticmethod
    def fill_apps():
        DataApps._apps = []

        _params = DataConfig.getConfigBaseParams()
        language = _params['language']

        appToCategories = DataApps.getAppToCategories()

        #Информация о приложениях из системы
        for rec in Gio.DesktopAppInfo.get_all():
            if rec.get_string('Type') != 'Application' or rec.get_string('NoDisplay') == 'true':
                continue

            app = App()
            app.id = rec.get_id()
            app.id = app.id.lower()
            app.id = app.id.replace('.desktop', '')

            app.name = rec.get_string('Name')
            app.icon = rec.get_string('Icon')

            app.exec = rec.get_string('Exec')
            app.exec = app.exec.rsplit('%', 1)[0]
            app.exec = app.exec.split('@@', 1)[0]
            app.exec = app.exec.rstrip('-')

            if rec.get_string('Terminal') == 'true':
                app.terminal = True
            else:
                app.terminal = False

            #Заполняем категории
            is_category = False
            for cat in appToCategories:
                if cat['app_id'] == app.id:
                    app.categories.append(Category(id=cat['category_id'], name=cat['category_name'], ordernum=cat['ordernum']))
                    if cat['category_id'] != 1: #Не избранное
                        is_category = True
            #Если никакой категории нет то указываем по умолчанию (избранная не учитывается)
            if not is_category:
                if language == 'ru':
                    app.categories.append(Category(id=0, name='Все', ordernum=0))
                else:
                    app.categories.append(Category(id=0, name='All', ordernum=0))

            app.actives = []
            DataApps._apps.append(app)

        #Сортируем по терминалу, т.к. активность надо с них определять
        DataApps._apps = sorted(DataApps._apps, key=lambda k: (k.terminal, len(k.id)), reverse=True)

        # Определение активности приложения
        for active_app in HyprData.get_active_apps():
            is_not_found = False
            for app in DataApps._apps:
                if app.terminal and active_app['app_title'] == app.id:
                    app.actives.append(Active(address=active_app['app_address'], workspace=active_app['app_workspace'], title=active_app['app_title']))
                    is_not_found = True
                    break
                elif active_app['app_initialTitle'] == app.name:
                    app.actives.append(Active(address=active_app['app_address'], workspace=active_app['app_workspace'], title=active_app['app_title']))
                    is_not_found = True
                    break
                elif active_app['app_class'] == app.id:
                    app.actives.append(Active(address=active_app['app_address'], workspace=active_app['app_workspace'], title=active_app['app_title']))
                    is_not_found = True
                    break

            #Если активное приложение ненайдено, то создаём фиктивно
            if not is_not_found:
                fapp = App()
                fapp.icon = 'hs-application-not-found'
                fapp.name = active_app['app_title']
                fapp.actives.append(Active(address=active_app['app_address'], workspace=active_app['app_workspace'], title=active_app['app_title']))
                DataApps._apps.append(fapp)

    @staticmethod
    def get_apps(is_fill:bool = True):
        if is_fill:
            DataApps.fill_apps()
        return DataApps._apps

    @staticmethod
    def get_apps_category(category_id:int):
        result = []
        for app in DataApps.get_apps(is_fill=False):
            for cat in app.categories:
                if cat.id == category_id:
                    result.append(app)

        #Сортировка
        def sortfunc(n):
            for rec in n.categories:
                if rec.id == category_id:
                    return rec.ordernum

            return 9999
        result.sort(key=sortfunc)

        return result

    @staticmethod
    def get_apps_favorite(is_and_active:bool):
        result = []
        for app in DataApps.get_apps():
            if app.is_favorite():
                result.append(app)

        #Сортировка
        def sortfunc(n):
            for rec in n.categories:
                if rec.id == 1:
                    return rec.ordernum

            return 9999
        result.sort(key=sortfunc)

        #Опционально добавляем ещё и активные приложения
        if is_and_active:
            for app in DataApps.get_apps():
                if app not in result:
                    if app.is_active():
                        result.append(app)

        return result

    @staticmethod
    def get_apps_active():
        result = []
        for app in DataApps.get_apps():
            if app.is_active():
                result.append(app)

        return result

class DataConfig:
    @staticmethod
    def getConnect():
        home_directory = os.getenv("HOME")
        configPath = home_directory + '/.config/hyprland-shell'
        if not os.path.exists(configPath):
          os.mkdir(configPath)
        dbPath = configPath + '/DataConfig.db'

        return sqlite3.connect(dbPath)

    @staticmethod
    def createDataBase():
        # Устанавливаем соединение с базой данных
        connection = DataConfig.getConnect()
        cursor = connection.cursor()

        # Создаём таблицы если их нет
        sql = '''
              CREATE TABLE IF NOT EXISTS CONFIG_BASE (
                TERMINAL_EXEC TEXT NOT NULL,
                THEME TEXT NOT NULL,
                LANGUAGE TEXT NOT NULL
              );
              '''
        cursor.execute(sql)

        sql = '''
              CREATE TABLE IF NOT EXISTS CONFIG (
                ID   INT NOT NULL PRIMARY KEY,
                TYPE TEXT NOT NULL
              );
              '''
        cursor.execute(sql)

        sql = '''
              CREATE TABLE IF NOT EXISTS CONFIG_DOCK (
                ID              INT NOT NULL PRIMARY KEY,
                MONITOR         TEXT,
                MONITOR_EXCLUDE TEXT,
                H_MARGIN        INT,
                V_MARGIN        INT,
                LAYER           TEXT,
                ANCHOR          TEXT
              );
              '''
        cursor.execute(sql)

        sql = '''
              CREATE TABLE IF NOT EXISTS CONFIG_DOCK_MODULES (
                ID              INT NOT NULL PRIMARY KEY,
                CONFIG_DOCK_ID  INT NOT NULL,
                POSITION        TEXT NOT NULL,
                ORDERNUM        INT NOT NULL,
                MODUL_ID        INT NOT NULL,
                GROUPNUM        INT
              );
              '''
        cursor.execute(sql)

        sql = '''
              CREATE TABLE IF NOT EXISTS CONFIG_MODUL (
                ID              INT NOT NULL PRIMARY KEY,
                TYPE            TEXT NOT NULL UNIQUE,
                IS_GROUP        INT
              );
              '''
        cursor.execute(sql)

        sql = '''
              CREATE TABLE IF NOT EXISTS CONFIG_MODUL_CLOCK (
                MASK_DATE TEXT,
                MASK_TIME TEXT
              );
              '''
        cursor.execute(sql)

        sql = '''
              CREATE TABLE IF NOT EXISTS CONFIG_MODUL_APPS (
                IS_ACTIVE INT
              );
              '''
        cursor.execute(sql)

        sql = '''
              CREATE TABLE IF NOT EXISTS CONFIG_MODUL_WORKSPACES (
                IS_ACTIVE INT,
                STYLE     TEXT
              );
              '''
        cursor.execute(sql)

        sql = '''
              CREATE TABLE IF NOT EXISTS CONFIG_MODUL_SOUND_VOLUME (
                EXEC_SETTING TEXT
              );
              '''
        cursor.execute(sql)

        sql = '''
              CREATE TABLE IF NOT EXISTS CONFIG_MODUL_SOUND_MICROPHONE (
                EXEC_SETTING TEXT
              );
              '''
        cursor.execute(sql)

        sql = '''
              CREATE TABLE IF NOT EXISTS CONFIG_MODUL_WEATHER (
                CITY TEXT
              );
              '''
        cursor.execute(sql)

        # Сохраняем изменения и закрываем соединение
        connection.commit()
        connection.close()

        DataConfig.fillConfigDefault()

    @staticmethod
    def get_system_language():
        """Определяет язык системы."""
        try:
            language, encoding = locale.getdefaultlocale()
            if language:
                return language.split('_')[0]  # Возвращает только код языка (например, "ru" для "ru_RU.UTF-8")
            else:
                return None
        except Exception:
            return None

    @staticmethod
    def fillConfigDefault():
        ### Базовые настройки
        if DataConfig.get_system_language() == 'ru':
            language = 'ru'
        else:
            language = 'en'

        DataConfig.setConfigBaseParams(terminal_exec='kitty', theme='dark', language=language)

        ### Модули и их настройки по умолчанию
        DataConfig.setConfigModul(modul='Apps', is_group=False)
        DataConfig.setConfigModul(modul='Launcher', is_group=False)
        DataConfig.setConfigModul(modul='Workspaces', is_group=False)
        DataConfig.setConfigModul(modul='WindowTitle', is_group=False)
        DataConfig.setConfigModul(modul='Clock', is_group=True)
        DataConfig.setConfigModul(modul='Language', is_group=False)
        DataConfig.setConfigModul(modul='SoundVolume', is_group=True)
        DataConfig.setConfigModul(modul='SoundMicrophone', is_group=True)
        DataConfig.setConfigModul(modul='Network', is_group=True)
        DataConfig.setConfigModul(modul='Battery', is_group=True)
        DataConfig.setConfigModul(modul='Power', is_group=True)
        DataConfig.setConfigModul(modul='PowerProfile', is_group=True)
        DataConfig.setConfigModul(modul='Setting', is_group=True)
        DataConfig.setConfigModul(modul='Weather', is_group=True)

        DataConfig.setConfigModulClockParams(mask_date='%d %m %Y', mask_time='%H:%M') #:%S
        DataConfig.setConfigModulAppsParams(is_active=True)
        DataConfig.setConfigModulWorkspacesParams(is_active=True, style='circle')
        DataConfig.setConfigModulSoundVolumeParams(exec_setting='pavucontrol')
        DataConfig.setConfigModulSoundMicrophoneParams(exec_setting='pavucontrol')
        DataConfig.setConfigModulWeatherParams(city='')

        ### Док панель если не заполнена
        if not DataConfig.isConfigDock():
            top_dock_id = DataConfig.setConfigDock(monitor='', monitor_exclude='', hmargin=5, vmargin=5, layer='top', anchor='top')
            DataConfig.setConfigDockModul(dock_id=top_dock_id, position='begin', modul='WindowTitle')
            DataConfig.setConfigDockModul(dock_id=top_dock_id, position='center', modul='Weather')
            DataConfig.setConfigDockModul(dock_id=top_dock_id, position='center', modul='Clock')
            DataConfig.setConfigDockModul(dock_id=top_dock_id, position='end', modul='Language')
            DataConfig.setConfigDockModul(dock_id=top_dock_id, position='end', modul='SoundVolume')
            DataConfig.setConfigDockModul(dock_id=top_dock_id, position='end', modul='SoundMicrophone')
            DataConfig.setConfigDockModul(dock_id=top_dock_id, position='end', modul='Battery')
            DataConfig.setConfigDockModul(dock_id=top_dock_id, position='end', modul='Network')
            DataConfig.setConfigDockModul(dock_id=top_dock_id, position='end', modul='PowerProfile')
            DataConfig.setConfigDockModul(dock_id=top_dock_id, position='end', modul='Power')

            DataConfig.setConfigDockGroupModules(dock_id=top_dock_id, position='center',modules=['Weather','Clock'])
            DataConfig.setConfigDockGroupModules(dock_id=top_dock_id, position='end', modules=['SoundVolume','SoundMicrophone'])
            DataConfig.setConfigDockGroupModules(dock_id=top_dock_id, position='end',modules=['Network', 'PowerProfile', 'Power', 'Battery'])

            bottom_dock_id = DataConfig.setConfigDock(monitor='', monitor_exclude='', hmargin=5, vmargin=5, layer='top', anchor='bottom')
            DataConfig.setConfigDockModul(dock_id=bottom_dock_id, position='begin', modul='Workspaces')
            DataConfig.setConfigDockModul(dock_id=bottom_dock_id, position='center', modul='Apps')
            DataConfig.setConfigDockModul(dock_id=bottom_dock_id, position='center', modul='Launcher')
            DataConfig.setConfigDockModul(dock_id=bottom_dock_id, position='end', modul='Setting')

    @staticmethod
    def setConfigBaseParams(terminal_exec:str, theme:str, language:str):
        connection = DataConfig.getConnect()
        cursor = connection.cursor()

        sql = '''        
              INSERT INTO CONFIG_BASE (TERMINAL_EXEC, THEME, LANGUAGE)
                SELECT ?, ?, ?
                WHERE NOT EXISTS (SELECT 1 FROM CONFIG_BASE);
              '''
        params = (terminal_exec, theme, language)
        cursor.execute(sql, params)

        connection.commit()
        connection.close()

    @staticmethod
    def getConfigBaseParams():
        connection = DataConfig.getConnect()
        cursor = connection.cursor()
        sql = 'SELECT TERMINAL_EXEC, THEME, LANGUAGE FROM CONFIG_BASE'
        cursor.execute(sql)
        baseParams = cursor.fetchone()
        connection.close()

        result = dict(terminal_exec=baseParams[0],theme=baseParams[1],language=baseParams[2])
        return result

    @staticmethod
    def updConfigBaseParams(terminal_exec:str, theme:str, language:str):
        connection = DataConfig.getConnect()
        cursor = connection.cursor()

        sql = '''
              UPDATE CONFIG_BASE
              SET
                TERMINAL_EXEC = ?, 
                THEME = ?, 
                LANGUAGE = ?
              '''
        params = (terminal_exec, theme, language)
        cursor.execute(sql, params)

        connection.commit()
        connection.close()

    @staticmethod
    def isConfigDock():
        connection = DataConfig.getConnect()
        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(1) FROM CONFIG_DOCK')
        count = cursor.fetchone()[0]
        connection.close()

        return count > 0

    @staticmethod
    def getConfigDocks(monitor:str):
        result = []
        connection = DataConfig.getConnect()
        cursor = connection.cursor()
        sql = 'SELECT ID FROM CONFIG_DOCK WHERE (LENGTH(MONITOR) > 0 AND MONITOR LIKE ?) OR (LENGTH(MONITOR) = 0 AND MONITOR_EXCLUDE NOT LIKE ?)'
        params = ('%'+monitor+'%', '%'+monitor+'%')
        cursor.execute(sql, params)
        dockList = cursor.fetchall()
        connection.close()

        for rec in dockList:
            d = dict(config_dock_id=rec[0])
            result.append(d)

        return result

    @staticmethod
    def getConfigDock(config_dock_id:int):
        connection = DataConfig.getConnect()
        cursor = connection.cursor()
        sql = 'SELECT H_MARGIN, V_MARGIN, LAYER, ANCHOR FROM CONFIG_DOCK WHERE ID = ?'
        params = (config_dock_id,)
        cursor.execute(sql, params)
        dockParams = cursor.fetchone()
        connection.close()

        result = dict(hmargin=dockParams[0],vmargin=dockParams[1],layer=dockParams[2],anchor=dockParams[3])
        return result

    @staticmethod
    def getConfigDockModules(config_dock_id:int):
        result = []
        connection = DataConfig.getConnect()
        cursor = connection.cursor()
        sql = '''
              SELECT 
                M.TYPE AS MODUL, DM.POSITION, DM.ORDERNUM, DM.GROUPNUM, M.IS_GROUP
              FROM CONFIG_DOCK_MODULES DM
                JOIN CONFIG_MODUL M ON M.ID = DM.MODUL_ID
              WHERE DM.CONFIG_DOCK_ID = ?
              ORDER BY DM.POSITION, DM.ORDERNUM
              '''
        params = (config_dock_id,)
        cursor.execute(sql, params)
        moduls = cursor.fetchall()
        connection.close()

        for rec in moduls:
            result.append(dict(modul=rec[0], position=rec[1], ordernum=rec[2], groupnum=rec[3], is_group=rec[4]==1))
        return result

    @staticmethod
    def getConfigDockModulParams(modul:str):
        connection = DataConfig.getConnect()
        cursor = connection.cursor()

        if modul == 'Clock':
            sql = 'SELECT MASK_DATE, MASK_TIME FROM CONFIG_MODUL_CLOCK;'
            cursor.execute(sql)
            modulParams = cursor.fetchone()
            result = dict(mask_date=modulParams[0], mask_time=modulParams[1])

        elif modul == 'Apps':
            sql = 'SELECT IS_ACTIVE FROM CONFIG_MODUL_APPS;'
            cursor.execute(sql)
            modulParams = cursor.fetchone()

            if modulParams[0] == 1:
                is_active = True
            else:
                is_active = False
            result = dict(is_active=is_active)

        elif modul == 'Workspaces':
            sql = 'SELECT IS_ACTIVE, STYLE FROM CONFIG_MODUL_WORKSPACES;'
            cursor.execute(sql)
            modulParams = cursor.fetchone()

            if modulParams[0] == 1:
                is_active = True
            else:
                is_active = False

            style = modulParams[1]

            result = dict(is_active=is_active, style=style)

        elif modul == 'SoundVolume':
            sql = 'SELECT EXEC_SETTING FROM CONFIG_MODUL_SOUND_VOLUME;'
            cursor.execute(sql)
            modulParams = cursor.fetchone()
            result = dict(exec_setting=modulParams[0])

        elif modul == 'SoundMicrophone':
            sql = 'SELECT EXEC_SETTING FROM CONFIG_MODUL_SOUND_MICROPHONE;'
            cursor.execute(sql)
            modulParams = cursor.fetchone()
            result = dict(exec_setting=modulParams[0])

        elif modul == 'Weather':
            sql = 'SELECT CITY FROM CONFIG_MODUL_WEATHER;'
            cursor.execute(sql)
            modulParams = cursor.fetchone()
            result = dict(city=modulParams[0])

        else:
            result = None

        connection.close()
        return result

    @staticmethod
    def setConfigDock(monitor:str, monitor_exclude:str, hmargin:int, vmargin:int, layer:str, anchor:str):
        connection = DataConfig.getConnect()
        cursor = connection.cursor()

        cursor.execute('SELECT COALESCE(MAX(ID),0) + 1 FROM CONFIG')
        new_id = cursor.fetchone()[0]
        type = 'Dock'
        sql = '''
              INSERT OR IGNORE INTO CONFIG (ID, TYPE) 
              VALUES (?, ?);
              '''
        params = (new_id, type)
        cursor.execute(sql, params)

        sql = '''
              INSERT OR IGNORE INTO CONFIG_DOCK (ID, MONITOR, MONITOR_EXCLUDE, H_MARGIN, V_MARGIN, LAYER, ANCHOR) 
              VALUES (?, ?, ?, ?, ?, ?, ?);
              '''
        params = (new_id, monitor, monitor_exclude, hmargin, vmargin, layer, anchor)
        cursor.execute(sql, params)

        connection.commit()
        connection.close()

        return new_id

    @staticmethod
    def updConfigDock(dock_id: int, monitor:str, monitor_exclude:str, hmargin:int, vmargin:int, layer:str, anchor:str):
        connection = DataConfig.getConnect()
        cursor = connection.cursor()

        sql = '''
              UPDATE CONFIG_DOCK
              SET
                MONITOR = ?, 
                MONITOR_EXCLUDE = ?, 
                H_MARGIN = ?, 
                V_MARGIN = ?, 
                LAYER = ?, 
                ANCHOR = ?
              WHERE ID = ?
              '''
        params = (monitor, monitor_exclude, hmargin, vmargin, layer, anchor, dock_id)
        cursor.execute(sql, params)

        connection.commit()
        connection.close()

    @staticmethod
    def removeConfigDock(dock_id:int):
        connection = DataConfig.getConnect()
        cursor = connection.cursor()
        params = (dock_id,)
        sql = 'DELETE FROM CONFIG WHERE ID = ?'
        cursor.execute(sql, params)

        sql = 'DELETE FROM CONFIG_DOCK WHERE ID = ?'
        cursor.execute(sql, params)

        sql = 'DELETE FROM CONFIG_DOCK_MODULES WHERE CONFIG_DOCK_ID = ?'
        cursor.execute(sql, params)

        connection.commit()
        connection.close()

    @staticmethod
    def setConfigDockModul(dock_id:int, position:str, modul:str):
        connection = DataConfig.getConnect()
        cursor = connection.cursor()

        cursor.execute('SELECT COALESCE(MAX(ID),0) + 1 FROM CONFIG_DOCK_MODULES')
        new_id = cursor.fetchone()[0]

        sql = 'SELECT COALESCE(MAX(ORDERNUM),0) + 1 FROM CONFIG_DOCK_MODULES WHERE CONFIG_DOCK_ID = ? AND POSITION = ?'
        params = (dock_id, position)
        cursor.execute(sql, params)
        ordernum = cursor.fetchone()[0]

        sql = 'SELECT ID FROM CONFIG_MODUL WHERE TYPE = ?'
        params = (modul,)
        cursor.execute(sql, params)
        modul_id = cursor.fetchone()[0]
        groupnum = 0

        sql = '''
              INSERT OR IGNORE INTO CONFIG_DOCK_MODULES (ID, CONFIG_DOCK_ID, POSITION, ORDERNUM, MODUL_ID, GROUPNUM) 
              VALUES (?, ?, ?, ?, ?, ?);
              '''
        params = (new_id, dock_id, position, ordernum, modul_id, groupnum)
        cursor.execute(sql, params)

        connection.commit()
        connection.close()

        return new_id

    @staticmethod
    def setConfigDockGroupModules(dock_id:int, position:str, modules:list):
        connection = DataConfig.getConnect()
        cursor = connection.cursor()

        sql = 'SELECT COALESCE(MAX(GROUPNUM),0) + 1 FROM CONFIG_DOCK_MODULES WHERE CONFIG_DOCK_ID = ? AND POSITION = ?'
        params = (dock_id, position)
        cursor.execute(sql, params)
        groupnum = cursor.fetchone()[0]

        sql = '''
              UPDATE CONFIG_DOCK_MODULES
              SET GROUPNUM = ?
              WHERE CONFIG_DOCK_ID = ?
                AND POSITION = ?
                AND MODUL_ID IN (SELECT ID FROM CONFIG_MODUL WHERE TYPE = ?);
              '''

        for rec in modules:
            params = (groupnum, dock_id, position, rec)
            cursor.execute(sql, params)

        connection.commit()
        connection.close()

    @staticmethod
    def setConfigModul(modul:str, is_group:bool):
        connection = DataConfig.getConnect()
        cursor = connection.cursor()

        cursor.execute('SELECT COALESCE(MAX(ID),0) + 1 FROM CONFIG_MODUL')
        new_id = cursor.fetchone()[0]

        sql = 'INSERT OR IGNORE INTO CONFIG_MODUL (ID, TYPE, IS_GROUP) VALUES (?, ?, ?);'

        if is_group:
            group_value = 1
        else:
            group_value = 0

        params = (new_id, modul, group_value)
        cursor.execute(sql, params)

        connection.commit()
        connection.close()

    @staticmethod
    def setConfigModulClockParams(mask_date:str, mask_time:str):
        connection = DataConfig.getConnect()
        cursor = connection.cursor()

        sql = '''
              INSERT INTO CONFIG_MODUL_CLOCK (MASK_DATE, MASK_TIME)
                SELECT ?, ?
                WHERE NOT EXISTS (SELECT 1 FROM CONFIG_MODUL_CLOCK);
              '''
        params = (mask_date, mask_time)
        cursor.execute(sql, params)

        connection.commit()
        connection.close()


    @staticmethod
    def setConfigModulAppsParams(is_active:bool):
        connection = DataConfig.getConnect()
        cursor = connection.cursor()

        sql = '''
              INSERT INTO CONFIG_MODUL_APPS (IS_ACTIVE)
                SELECT ?
                WHERE NOT EXISTS (SELECT 1 FROM CONFIG_MODUL_APPS);
              '''
        if is_active:
            params = (1,)
        else:
            params = (0,)
        cursor.execute(sql, params)

        connection.commit()
        connection.close()

    @staticmethod
    def setConfigModulWorkspacesParams(is_active:bool, style:str):
        connection = DataConfig.getConnect()
        cursor = connection.cursor()

        sql = '''
              INSERT INTO CONFIG_MODUL_WORKSPACES (IS_ACTIVE, STYLE)
                SELECT ?, ?
                WHERE NOT EXISTS (SELECT 1 FROM CONFIG_MODUL_WORKSPACES);
              '''
        if is_active:
            params = (1, style)
        else:
            params = (0, style)
        cursor.execute(sql, params)

        connection.commit()
        connection.close()

    @staticmethod
    def setConfigModulSoundVolumeParams(exec_setting:str):
        connection = DataConfig.getConnect()
        cursor = connection.cursor()

        sql = '''
              INSERT INTO CONFIG_MODUL_SOUND_VOLUME (EXEC_SETTING)
                SELECT ?
                WHERE NOT EXISTS (SELECT 1 FROM CONFIG_MODUL_SOUND_VOLUME);
              '''

        params = (exec_setting,)
        cursor.execute(sql, params)

        connection.commit()
        connection.close()

    @staticmethod
    def setConfigModulSoundMicrophoneParams(exec_setting:str):
        connection = DataConfig.getConnect()
        cursor = connection.cursor()

        sql = '''
              INSERT INTO CONFIG_MODUL_SOUND_MICROPHONE (EXEC_SETTING)
                SELECT ?
                WHERE NOT EXISTS (SELECT 1 FROM CONFIG_MODUL_SOUND_MICROPHONE);
              '''

        params = (exec_setting,)
        cursor.execute(sql, params)

        connection.commit()
        connection.close()

    @staticmethod
    def setConfigModulWeatherParams(city:str):
        connection = DataConfig.getConnect()
        cursor = connection.cursor()

        sql = '''
              INSERT INTO CONFIG_MODUL_WEATHER (CITY)
                SELECT ?
                WHERE NOT EXISTS (SELECT 1 FROM CONFIG_MODUL_WEATHER);
              '''

        params = (city,)
        cursor.execute(sql, params)

        connection.commit()
        connection.close()

    @staticmethod
    def getConfigDocksForSetting():
        result = []
        connection = DataConfig.getConnect()
        cursor = connection.cursor()
        sql = 'SELECT ID, MONITOR, MONITOR_EXCLUDE, H_MARGIN, V_MARGIN, LAYER, ANCHOR FROM CONFIG_DOCK'
        cursor.execute(sql)
        docks = cursor.fetchall()
        connection.close()

        for rec in docks:
            result.append(dict(id=rec[0], monitor=rec[1], monitor_exclude=rec[2], hmargin=rec[3],vmargin=rec[4],layer=rec[5],anchor=rec[6]))

        return result

    @staticmethod
    def getConfigDockModulesForSetting(dock_id:int):
        return DataConfig.getConfigDockModules(config_dock_id=dock_id)

    @staticmethod
    def moveUpConfigDockModuleForSetting(dock_id:int, position:str, modul:str):
        connection = DataConfig.getConnect()
        cursor = connection.cursor()

        # Текущая позиция
        sql = '''
              SELECT DM.ORDERNUM
              FROM CONFIG_DOCK_MODULES DM
                JOIN CONFIG_MODUL M ON M.ID = DM.MODUL_ID
              WHERE DM.CONFIG_DOCK_ID = ?
                AND DM.POSITION = ?
                AND M.TYPE = ?
              '''

        params = (dock_id, position, modul)
        cursor.execute(sql, params)
        cur_ordernum = cursor.fetchone()[0]

        # Поиск позиции и группы для обмена
        sql = '''
              SELECT M.TYPE, DM.ORDERNUM
              FROM CONFIG_DOCK_MODULES DM
                JOIN CONFIG_MODUL M ON M.ID = DM.MODUL_ID
              WHERE DM.CONFIG_DOCK_ID = ?
                AND DM.POSITION = ?
                AND DM.ORDERNUM < ?
              ORDER BY DM.ORDERNUM DESC;
              '''

        params = (dock_id, position, cur_ordernum)
        cursor.execute(sql, params)
        move_modul = ''
        move_ordernum = -999
        for rec in cursor.fetchall():
            move_modul = rec[0]
            move_ordernum = rec[1]
            break

        if move_ordernum != -999 and move_modul != '':
            sql = '''
                  UPDATE CONFIG_DOCK_MODULES 
                  SET ORDERNUM = ? 
                  WHERE CONFIG_DOCK_ID = ? AND POSITION = ? AND MODUL_ID IN (SELECT ID FROM CONFIG_MODUL WHERE TYPE = ?);
                  '''
            params = (move_ordernum, dock_id, position, modul)
            cursor.execute(sql, params)

            params = (cur_ordernum, dock_id, position, move_modul)
            cursor.execute(sql, params)

        connection.commit()
        connection.close()

    @staticmethod
    def moveDownConfigDockModuleForSetting(dock_id: int, position: str, modul: str):
        connection = DataConfig.getConnect()
        cursor = connection.cursor()

        # Текущая позиция
        sql = '''
               SELECT DM.ORDERNUM
               FROM CONFIG_DOCK_MODULES DM
                 JOIN CONFIG_MODUL M ON M.ID = DM.MODUL_ID
               WHERE DM.CONFIG_DOCK_ID = ?
                 AND DM.POSITION = ?
                 AND M.TYPE = ?
               '''

        params = (dock_id, position, modul)
        cursor.execute(sql, params)
        cur_ordernum = cursor.fetchone()[0]

        # Поиск позиции и группы для обмена
        sql = '''
               SELECT M.TYPE, DM.ORDERNUM
               FROM CONFIG_DOCK_MODULES DM
                 JOIN CONFIG_MODUL M ON M.ID = DM.MODUL_ID
               WHERE DM.CONFIG_DOCK_ID = ?
                 AND DM.POSITION = ?
                 AND DM.ORDERNUM > ?
               ORDER BY DM.ORDERNUM;
               '''

        params = (dock_id, position, cur_ordernum)
        cursor.execute(sql, params)
        move_modul = ''
        move_ordernum = -999
        for rec in cursor.fetchall():
            move_modul = rec[0]
            move_ordernum = rec[1]
            break

        if move_ordernum != -999 and move_modul != '':
            sql = '''
                   UPDATE CONFIG_DOCK_MODULES 
                   SET ORDERNUM = ? 
                   WHERE CONFIG_DOCK_ID = ? AND POSITION = ? AND MODUL_ID IN (SELECT ID FROM CONFIG_MODUL WHERE TYPE = ?);
                   '''
            params = (move_ordernum, dock_id, position, modul)
            cursor.execute(sql, params)

            params = (cur_ordernum, dock_id, position, move_modul)
            cursor.execute(sql, params)

        connection.commit()
        connection.close()

    @staticmethod
    def setGroupnumConfigDockModuleForSetting(dock_id: int, position: str, modul: str, groupnum:int):
        connection = DataConfig.getConnect()
        cursor = connection.cursor()

        sql = '''
               UPDATE CONFIG_DOCK_MODULES 
               SET GROUPNUM = ? 
               WHERE CONFIG_DOCK_ID = ? AND POSITION = ? AND MODUL_ID IN (SELECT ID FROM CONFIG_MODUL WHERE TYPE = ?);
               '''
        params = (groupnum, dock_id, position, modul)
        cursor.execute(sql, params)

        connection.commit()
        connection.close()

    @staticmethod
    def removeConfigDockModuleForSetting(dock_id: int, position: str, modul: str):
        connection = DataConfig.getConnect()
        cursor = connection.cursor()

        sql = '''
           DELETE FROM CONFIG_DOCK_MODULES  
           WHERE CONFIG_DOCK_ID = ? AND POSITION = ? AND MODUL_ID IN (SELECT ID FROM CONFIG_MODUL WHERE TYPE = ?);
           '''
        params = (dock_id, position, modul)
        cursor.execute(sql, params)

        connection.commit()
        connection.close()


    @staticmethod
    def addConfigDockModuleForSetting(dock_id: int, position: str, modul: str):
        DataConfig.setConfigDockModul(dock_id=dock_id, position=position, modul=modul)

    @staticmethod
    def getConfigModulesForSetting():
        result = []
        connection = DataConfig.getConnect()
        cursor = connection.cursor()
        sql = '''
              SELECT TYPE, IS_GROUP
              FROM CONFIG_MODUL
              ORDER BY TYPE
              '''
        cursor.execute(sql)
        moduls = cursor.fetchall()
        connection.close()

        for rec in moduls:
            type = rec[0]
            is_group = rec[1] == 1
            result.append(dict(type=type, is_group=is_group))
        return result

    @staticmethod
    def getConfigDockForSetting(config_dock_id:int):
        connection = DataConfig.getConnect()
        cursor = connection.cursor()
        sql = 'SELECT MONITOR, MONITOR_EXCLUDE, H_MARGIN, V_MARGIN, ANCHOR FROM CONFIG_DOCK WHERE ID = ?'
        params = (config_dock_id,)
        cursor.execute(sql, params)
        dockParams = cursor.fetchone()
        connection.close()

        result = dict(monitor=dockParams[0], monitor_exclude=dockParams[1], hmargin=dockParams[2], vmargin=dockParams[3], anchor=dockParams[4])
        return result

    @staticmethod
    def addConfigDockForSetting(monitor: str, monitor_exclude: str, hmargin: int, vmargin: int, anchor: str):
        return DataConfig.setConfigDock(monitor=monitor, monitor_exclude=monitor_exclude, hmargin=hmargin, vmargin=vmargin, layer='top', anchor=anchor)

    @staticmethod
    def updConfigDockForSetting(dock_id: int, monitor: str, monitor_exclude: str, hmargin: int, vmargin: int, anchor: str):
        return DataConfig.updConfigDock(dock_id=dock_id, monitor=monitor, monitor_exclude=monitor_exclude, hmargin=hmargin, vmargin=vmargin, layer='top', anchor=anchor)

    @staticmethod
    def removeConfigDockForSetting(dock_id: int):
        DataConfig.removeConfigDock(dock_id=dock_id)

    @staticmethod
    def getConfigModulesForSettingModules():
        result = []
        connection = DataConfig.getConnect()
        cursor = connection.cursor()
        sql = '''
              SELECT TYPE
              FROM CONFIG_MODUL
              WHERE TYPE IN ('Clock','Apps','Workspaces','SoundVolume','SoundMicrophone','Weather')
              ORDER BY TYPE
              '''
        cursor.execute(sql)
        moduls = cursor.fetchall()
        connection.close()

        for rec in moduls:
            result.append(rec[0])
        return result

    @staticmethod
    def setConfigModulClockForSettingModules(mask_date:str, mask_time:str):
        connection = DataConfig.getConnect()
        cursor = connection.cursor()

        sql = '''
              UPDATE CONFIG_MODUL_CLOCK 
              SET
                MASK_DATE = ?, 
                MASK_TIME = ?
              '''
        params = (mask_date, mask_time)
        cursor.execute(sql, params)

        connection.commit()
        connection.close()

    @staticmethod
    def setConfigModulAppsForSettingModules(is_active:bool):
        connection = DataConfig.getConnect()
        cursor = connection.cursor()

        sql = '''
              UPDATE CONFIG_MODUL_APPS 
              SET
                IS_ACTIVE = ? 
              '''
        if is_active:
            params = (1,)
        else:
            params = (0,)
        cursor.execute(sql, params)

        connection.commit()
        connection.close()

    @staticmethod
    def setConfigModulWorkspacesForSettingModules(is_active:bool, style:str):
        connection = DataConfig.getConnect()
        cursor = connection.cursor()

        sql = '''
              UPDATE CONFIG_MODUL_WORKSPACES 
              SET
                IS_ACTIVE = ?, 
                STYLE = ?
              '''
        if is_active:
            params = (1, style)
        else:
            params = (0, style)
        cursor.execute(sql, params)

        connection.commit()
        connection.close()

    @staticmethod
    def setConfigModulSoundVolumeForSettingModules(exec_setting:str):
        connection = DataConfig.getConnect()
        cursor = connection.cursor()

        sql = '''
              UPDATE CONFIG_MODUL_SOUND_VOLUME
              SET
                EXEC_SETTING = ?
              '''

        params = (exec_setting,)
        cursor.execute(sql, params)

        connection.commit()
        connection.close()

    @staticmethod
    def setConfigModulSoundMicrophoneForSettingModules(exec_setting:str):
        connection = DataConfig.getConnect()
        cursor = connection.cursor()

        sql = '''
              UPDATE CONFIG_MODUL_SOUND_MICROPHONE
              SET
                EXEC_SETTING = ?
              '''

        params = (exec_setting,)
        cursor.execute(sql, params)

        connection.commit()
        connection.close()

    @staticmethod
    def setConfigModulWeatherForSettingModules(city:str):
        connection = DataConfig.getConnect()
        cursor = connection.cursor()

        sql = '''
              UPDATE CONFIG_MODUL_WEATHER
              SET
                CITY = ?
              '''

        params = (city,)
        cursor.execute(sql, params)

        connection.commit()
        connection.close()
