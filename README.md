# hyprland-shell

***
## Description
Hyprland shell

Includes the following elements:
- Dock panel
- Settings

Modules on the dock panel:
- Apps - Panel with applications (favorites + running)
- Launcher - Window with application selection (grouped by categories)
- Workspaces - Desktops (+ displays active applications on the desktop)
- Clock - Date, time, calendar
- Battery - Battery
- Language - Language
- Network - Network connections
- SoundVolume/SoundMicrophone - Sound
- PowerProfile - Power profiles
- Power - Shutdown
- WindowTitle - Active window title
- Weather - Weather
- Setting - Settings

Language:
- Russian
- English

Theme:
- Dark
- Light

## Installation
Pre-update
for Fedora
```
sudo dnf update
```
for Arch
```
sudo pacman -Suy
```

Get and install
```
git clone https://github.com/xzilgiz/hyprland-shell.git
cd hyprland-shell
sudo ./install.sh
```
then in the hyprland config
$HOME/.config/hypr/hyprland.conf

add
exec-once = hyprland-shell.sh

restart the session (or just reboot)

## Gallery
<img src="https://raw.githubusercontent.com/xzilgiz/hyprland-shell/refs/heads/main/.img/desktop.png">

### Operations with running applications
<img src="https://raw.githubusercontent.com/xzilgiz/hyprland-shell/refs/heads/main/.img/workspace_app_operations.png">
<img src="https://raw.githubusercontent.com/xzilgiz/hyprland-shell/refs/heads/main/.img/app_operations.png">

### Moving apps into categories
<img src="https://raw.githubusercontent.com/xzilgiz/hyprland-shell/refs/heads/main/.img/launcher_app_to_category.png">
<img src="https://raw.githubusercontent.com/xzilgiz/hyprland-shell/refs/heads/main/.img/launcher_app_to_dock.png">

### Setting
<img src="https://raw.githubusercontent.com/xzilgiz/hyprland-shell/refs/heads/main/.img/setting_base.png">
<img src="https://raw.githubusercontent.com/xzilgiz/hyprland-shell/refs/heads/main/.img/setting_dock.png">
<img src="https://raw.githubusercontent.com/xzilgiz/hyprland-shell/refs/heads/main/.img/setting_launcher.png">
<img src="https://raw.githubusercontent.com/xzilgiz/hyprland-shell/refs/heads/main/.img/setting_modules.png">