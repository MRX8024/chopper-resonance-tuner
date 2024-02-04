#!/bin/bash
repo=chopper-resonance-tuner
repo_path=~/chopper-resonance-tuner/
script_name=chopper_plot.py

# Сворачивание от root
if [ "$(id -u)" = "0" ]; then
    echo "Script must run from non-root !!!"
    exit
fi

r_folder=~/printer_data/config/adxl_results/chopper_magnitude
if [ ! -d "$r_folder" ]; then # Проверка папки chopper_magnitude & создание
    mkdir -p "$r_folder"
    echo "Make $r_folder direction successfully complete"
fi

s_folder=~/printer_data/config/scripts
# Перемещение репозитория
if [ ! -d "$s_folder" ]; then # Проверка папки scripts & создание
    mkdir -p "$s_folder"
fi
if [ -f "$s_folder/$repo/$script_name" ]; then # Проверка папки в папке
    read -p "Folder $repo already exists in $s_folder. Do you want to overwrite it? (y/n): " answer
    if [ "$answer" != "${answer#[Yy]}" ]; then
        sudo cp -r $repo_path "$s_folder/$repo" # Перезапись
        sudo chmod +x $s_folder/$repo/*
        # echo "Copying $repo to $s_folder successfully complete"
    else
        echo "Copying $repo aborted"
    fi
else
    sudo cp -r $repo_path "$s_folder/$repo" # Копирование
    # echo "Copying $repo to $s_folder successfully complete"
fi

g_shell_folder=~/klipper/klippy/extras/
g_shell_name=gcode_shell_command.py
# Перемещение gcode_shell_command.py
if [ -f "$g_shell_folder/$g_shell_name" ]; then # Проверка файла в папке
    read -p "File $g_shell_name already exists in $g_shell_folder. Do you want to overwrite it? (y/n): " answer
    if [ "$answer" != "${answer#[Yy]}" ]; then
        sudo cp "$repo/$g_shell_name" "$g_shell_folder" # Перезапись
        sudo chmod +x $g_shell_folder/$g_shell_name
        # echo "Copying $g_shell_name to $g_shell_folder successfully complete"
    else
        echo "Copying $g_shell_name aborted"
    fi
else
    sudo cp $repo"$g_shell_name" "$g_shell_folder" # Копирование
    echo "Copying $g_shell_name to $g_shell_folder successfully complete"
fi

cfg_name=chopper_tune.cfg
prcfg_path=~/printer_data/config/printer.cfg
# Добавление строки [include] в printer.cfg
if [ -f "$prcfg_path" ]; then
    if ! grep -q "^\[include ${s_folder##*/}/$repo/$cfg_name\]$" "$prcfg_path"; then
        sudo service klipper stop
        sed -i "1i\[include ${s_folder##*/}/$repo/$cfg_name]" "$prcfg_path"
        # echo "Including $cfg_name to $prcfg_path successfully complete"
        sudo service klipper start
    else
        echo "Including $cfg_name aborted, $cfg_name already exists in $prcfg_path"
    fi
fi
# Добавление строки [respond] в printer.cfg
if [ -f "$prcfg_path" ]; then
    if ! grep -q "^\[respond\]$" "$prcfg_path"; then
        sudo service klipper stop
        sed -i "1i\[respond]" "$prcfg_path"
        # echo "Including [respond] to $prcfg_path successfully complete"
        sudo service klipper start
    else
        echo "Including [respond] aborted, [respond] already exists in $prcfg_path"
    fi
fi

blk_path=~/printer_data/config/moonraker.conf
# Добавление блока обновления в moonraker.conf
if [ -f "$blk_path" ]; then
    if ! grep -q "^\[update_manager chopper-resonance-tuner\]$" "$blk_path"; then
        read -p " Do you want to install updater? (y/n): " answer
        if [ "$answer" != "${answer#[Yy]}" ]; then
          sudo service moonraker stop
          sed -i "\$a #" "$blk_path"
          sed -i "\$a [update_manager chopper-resonance-tuner]" "$blk_path"
          sed -i "\$a type: git_repo" "$blk_path"
          sed -i "\$a path: $s_folder/$repo" "$blk_path"
          sed -i "\$a origin: https://github.com/MRX8024/chopper-resonance-tuner.git" "$blk_path"
          sed -i "\$a is_system_service: False" "$blk_path"
          sed -i "\$a managed_services: klipper" "$blk_path"
          # echo "Including [update_manager] to $blk_path successfully complete"
          sudo service moonraker start
        else
          echo "Installing updater aborted"
        fi
    else
        echo "Including [update_manager] aborted, [update_manager] already exists in $blk_path"
    fi
fi

sudo apt update
sudo apt-get install libopenblas-dev
sudo pip install -r "$repo_path"wiki/requirements.txt

# Удаление директории репозитория
sudo rm -rf ~/chopper-resonance-tuner
echo "Temp repository was removed"