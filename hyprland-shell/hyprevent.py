import os
import socket
import threading

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import GLib

from hyprdata import HyprData

### Класс типов евентов в разрезе программы
class HyprEventType:
    ON_WINDOW_TITLE = 1
    ON_WORKSPACE = 2
    ON_WORKSPACE_CURRENT = 3
    ON_APP = 4
    ON_APP_URGENT = 5
    ON_LANGUAGE = 6

### Класс входящих евентов из сокета
class HyprEventListener:
    def start(self):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server_address = f"{os.getenv('XDG_RUNTIME_DIR')}/hypr/{os.environ["HYPRLAND_INSTANCE_SIGNATURE"]}/.socket2.sock"
        sock.connect(server_address)

        buffer = b""
        while True:
            new_data = sock.recv(4096)
            if not new_data:
                break

            buffer += new_data
            while b"\n" in buffer:
                data, buffer = buffer.split(b"\n", 1)
                #print('event: '+data.decode("utf-8"))
                yield data.decode("utf-8")

### Класс получения евентов
class HyprEvent:
    events = []
    task = None
    listener = None

    @staticmethod
    def add_handle(object: object, eventType: HyprEventType, callback: callable):
        isNew = True
        for rec in HyprEvent.events:
            if rec['object'] == object and rec['eventType'] == eventType:
                rec['callback'] = callable
                isNew = False
                break
        if isNew:
            HyprEvent.events.append(dict(object=object, eventType=eventType, callback=callback))

        HyprEvent().start()

    @staticmethod
    def remove_handle(object: object, eventType: HyprEventType):
        for rec in HyprEvent.events:
            if rec['object'] == object and rec['eventType'] == eventType:
                HyprEvent.events.remove(rec)
                break

    @staticmethod
    def get_events():
        HyprEvent.listener = HyprEventListener()
        for event in HyprEvent.listener.start():
            if ">>" in event:
                event_name, args = event.split(">>")
                args = args.split(",")
                HyprEvent.emit(event_name, *args)
            else:
                HyprEvent.emit(event)
        return True

    @staticmethod
    def start():
        if HyprEvent.task == None:
            HyprEvent.task = threading.Thread(target=HyprEvent.get_events, daemon=True)
            HyprEvent.task.start()

    @staticmethod
    def emit(event_name: str, *args, **kwargs):
        event_processed = []
        for event_type in HyprEvent.get_event_type_list(event_name):
            for rec in HyprEvent.events:
                if rec['eventType'] == event_type:
                    if event_type not in event_processed:
                        HyprEvent.update_data(event_type, event_name, *args, **kwargs)
                        event_processed.append(event_type)

                    callback = rec['callback']
                    #object = rec['object']
                    #callback() #Просто вызвать похоже некошерно надо согласованно с основным GTK потоком
                    GLib.idle_add(callback)

    #Сопоставление евентов хурмы с евентами программы
    @staticmethod
    def get_event_type_list(event_name):
        result = []
        if event_name in ('activewindow'):
            result.append(HyprEventType.ON_WINDOW_TITLE)

        if event_name in ('workspace','destroyworkspace','openwindow','movewindow','movewindowv2','closewindow','focusedmon'):
            result.append(HyprEventType.ON_WORKSPACE)

        if event_name in ('workspace','focusedmon','workspacev2'):
            result.append(HyprEventType.ON_WORKSPACE_CURRENT)

        if event_name in ('activelayout'):
            result.append(HyprEventType.ON_LANGUAGE)

        if event_name in ('openwindow', 'closewindow'):
            result.append(HyprEventType.ON_APP)

        if event_name in ('urgent'):
            result.append(HyprEventType.ON_APP_URGENT)

        return result

    #Обогащение данных по евентам
    @staticmethod
    def update_data(event_type:HyprEventType, event_name, *args, **kwargs):
        if event_type == HyprEventType.ON_WINDOW_TITLE:
            if event_name == 'activewindow':
                HyprData.upd_active_window_title(args[1])

        if event_type == HyprEventType.ON_LANGUAGE:
            if event_name == 'activelayout':
                HyprData.upd_language(args[0], args[1])

        if event_type == HyprEventType.ON_APP_URGENT:
            if event_name == 'urgent':
                HyprData.upd_urgent_address(args[0])

        if event_type == HyprEventType.ON_WORKSPACE_CURRENT:
            if event_name == 'workspace':
                HyprData.upd_workspace_current(args[0])
            if event_name == 'workspacev2':
                HyprData.upd_workspace_current(args[1])
            elif event_name == 'focusedmon':
                HyprData.upd_workspace_current(args[1])

        if event_type == HyprEventType.ON_WORKSPACE:
            HyprData.upd_workspaces()
            HyprData.upd_active_apps()

        if event_type == HyprEventType.ON_APP:
            HyprData.upd_active_apps()

