import os
import socket
import json

class HyprCtl:
    _is_workspace_rules = False

    @staticmethod
    def hyprctl(cmd, buf_size=2048):
        xdg_runtime_dir = os.getenv("XDG_RUNTIME_DIR")
        hypr_dir = f"{xdg_runtime_dir}/hypr" if xdg_runtime_dir and os.path.isdir(f"{xdg_runtime_dir}/hypr") else "/tmp/hypr"
        p_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        p_socket.connect(f"{hypr_dir}/{os.getenv('HYPRLAND_INSTANCE_SIGNATURE')}/.socket.sock")

        try:
            p_socket.send(cmd.encode("utf-8"))

            output = b""
            while True:
                buffer = p_socket.recv(buf_size)
                if buffer:
                    output = b"".join([output, buffer])
                else:
                    break
            p_socket.close()
            return output.decode('utf-8', errors='replace')
        except Exception as e:
            print(f"hyprctl: {e}")
            return ""

    @staticmethod
    def get_ctl_json(cmd):
        reply = HyprCtl.hyprctl(cmd)
        try:
            return json.loads(reply)
        except Exception as e:
            print(e)
            return {}

    @staticmethod
    def get_workspaces():
        result = []

        monitors = HyprCtl.get_ctl_json('j/monitors')
        wsrules = HyprCtl.get_ctl_json('j/workspacerules')

        #Если правила воркспейсов не заданы в системе, то делаем 4ри постоянных + 4ри дополнительных
        if not HyprCtl._is_workspace_rules:
            if wsrules != []:
                HyprCtl._is_workspace_rules = True
            else:
                for monitor in monitors:
                    monitor_id = monitor['id']
                    monitor_name = monitor['name']
                    start_index = monitor_id*10+1
                    end_index = start_index + 8
                    
                    count_persistent = 0
                    for i in range(start_index, end_index):
                        count_persistent += 1
                        if count_persistent < 5:
                            os.system("hyprctl keyword workspace {}, monitor:{}, default:true, persistent:true".format(i, monitor_name))
                        else:
                            os.system("hyprctl keyword workspace {}, monitor:{}, default:true, persistent:false".format(i,monitor_name))

                wsrules = HyprCtl.get_ctl_json('j/workspacerules')
                HyprCtl._is_workspace_rules = True

        wslist = HyprCtl.get_ctl_json('j/workspaces')
        wsactive = HyprCtl.get_ctl_json('j/activeworkspace')

        #Проходим по мониторам
        for monitor in monitors:
            result.append(dict(id = monitor['id'], name = monitor['name']))
            #Проходим по правилам воркспейсов
            ws = []
            for wsrule in wsrules:
                if wsrule['monitor'] == monitor['name']:
                    ws_id = wsrule['workspaceString']
                    #Постоянные
                    try:
                        if wsrule['persistent'] == True:
                            ws_persistent = 'True'
                        else:
                            ws_persistent = 'False'
                    except Exception as e:
                        ws_persistent = 'False'

                    #Пустые
                    ws_empty = 'True'
                    for wsc in wslist:
                        if wsc['monitor'] == monitor['name'] and wsc['name'] == ws_id:
                            if wsc['windows'] == 0:
                                ws_empty = 'True'
                            else:
                                ws_empty = 'False'

                    #Активный
                    ws_active = 'False'
                    if wsactive['monitor'] == monitor['name'] and wsactive['name'] == ws_id:
                        ws_active = 'True'

                    ws.append(dict(id = ws_id, persistent = ws_persistent, empty = ws_empty, active = ws_active))

            # Проходим по имеющимся воркспейсам но которых нет в правилах
            for wsc in wslist:
                is_exists = False
                if wsc['monitor'] == monitor['name']:
                    for w in ws:
                        if w['id'] == wsc['name']:
                            is_exists = True

                    ws_active = 'False'
                    if is_exists == False:
                        if wsactive['monitor'] == monitor['name'] and wsactive['name'] == wsc['name']:
                            ws_active = 'True'

                        ws.append(dict(id=wsc['name'], persistent='False', empty='False', active=ws_active))

            def sortfunc(n):
                return int(n['id'])
            ws.sort(key = sortfunc)
            result[len(result) - 1]['ws'] = ws

        return result

    @staticmethod
    def get_language():
        devices = HyprCtl.get_ctl_json('j/devices')
        result = dict(device = '', value = '')

        for rec in devices['keyboards']:
            if rec['main']:
                result['device'] = rec['name']
                result['value'] = rec['active_keymap']
                break

        return result

    @staticmethod
    def get_active_apps():
        result = []

        apps = HyprCtl.get_ctl_json('j/clients')
        monitors = HyprCtl.get_ctl_json('j/monitors')

        for monitor in monitors:
            monitor_id = monitor['id']
            monitor_name = monitor['name']
            #done = []
            for app in apps:
                app_monitor_id = app['monitor']
                app_class = app['class']
                app_class = app_class.lower()
                app_title = app['title']
                app_title = app_title.lower()
                app_initialTitle = app['initialTitle']
                app_address = app['address']
                app_workspace = app['workspace']['name']

                if app_monitor_id == monitor_id:
                    #if app_class not in done:
                        result.append(dict(monitor_id=monitor_id, monitor_name=monitor_name, app_class=app_class, app_title=app_title, app_initialTitle=app_initialTitle, app_address=app_address, app_workspace=app_workspace))
                        #done.append(app_class)
        return result

    @staticmethod
    def get_monitors():
        result = []
        monitors = HyprCtl.get_ctl_json('j/monitors')
        for monitor in monitors:
            result.append(dict(id = monitor['id'], name = monitor['name']))

        return result