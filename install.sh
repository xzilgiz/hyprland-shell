#!/usr/bin/env bash

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (sudo ./install.sh)"
  exit
fi

is_pkg_instal=0

#dnf (fedora)
if [ "$is_pkg_instal" == "0" ]; then
  check=1
  if ! command -v dnf &> /dev/null; then
    check=0
  fi

  if [ "$check" == "1" ]; then
    echo "install packages..."
    dnf install sqlite3
    dnf install python3-gobject gtk4
    dnf install gcc gobject-introspection-devel cairo-gobject-devel pkg-config python3-devel gtk4
    dnf install gtk4-layer-shell
    is_pkg_instal=1
  fi
fi

#pacman (arch)
if [ "$is_pkg_instal" == "0" ]; then
  check=1
  if ! command -v pacman &> /dev/null; then
    check=0
  fi

  if [ "$check" == "1" ]; then
    echo "install packages..."
    pacman -S sqlite3
    pacman -S python-gobject gtk4
    pacman -S python cairo pkgconf gobject-introspection gtk4
    pacman -S gtk4-layer-shell
    is_pkg_instal=1
  fi
fi

if [ "$is_pkg_instal" == "0" ]; then
    echo "packet manager not found"
    exit 1
fi

echo "copy files..."
rm -Rf /usr/share/hyprland-shell
rm -f /usr/bin/hyprland-shell.sh
cp -r hyprland-shell /usr/share/hyprland-shell
cp hyprland-shell.sh /usr/bin

cd /usr/share/hyprland-shell

echo "create venv..."
python3 -m venv .venv

echo "activate venv..."
source .venv/bin/activate

echo "install venv packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo "install ok"

echo "..."
echo "In config hyprland:"
echo "$HOME/.config/hypr/hyprland.conf"
echo "append:"
echo "exec-once = hyprland-shell.sh"
