#!/bin/bash
repo=chopper-resonance-tuner
repo_path=~/chopper-resonance-tuner/
script_name=chopper_plot.py

# Сворачивание от root
if [ "$(id -u)" = "0" ]; then
    echo "Script must run from non-root !!!"
    exit
fi

result_folder=~/printer_data/config/adxl_results/chopper_magnitude
if [ ! -d "$result_folder" ]; then # Проверка папки chopper_magnitude & создание
    mkdir -p "$result_folder"
    echo "Make $result_folder direction successfully complete"
fi

#s_folder=~/printer_data/config/scripts
## Перемещение репозитория
#if [ ! -d "$s_folder" ]; then # Проверка папки scripts & создание
#    mkdir -p "$s_folder"
#fi
#if [ -f "$s_folder/$repo/$script_name" ]; then # Проверка папки в папке
#    read -p "Folder $repo already exists in $s_folder. Do you want to overwrite it? (y/n): " answer
#    if [ "$answer" != "${answer#[Yy]}" ]; then
#        sudo cp -r $repo_path "$s_folder" # Перезапись
#        # echo "Copying $repo to $s_folder successfully complete"
#    else
#        echo "Copying $repo aborted"
#    fi
#else
#    sudo cp -r $repo_path "$s_folder/$repo" # Копирование
#    # echo "Copying $repo to $s_folder successfully complete"
#fi
#sudo chmod -R +x "$s_folder/"

g_shell_path=~/klipper/klippy/extras/
g_shell_name=gcode_shell_command.py
# Перемещение gcode_shell_command.py
if [ -f "$g_shell_path/$g_shell_name" ]; then # Проверка файла в папке
     echo "Including $g_shell_name aborted, $g_shell_name already exists in $g_shell_path"
#    read -p "File $g_shell_name already exists in $g_shell_path. Do you want to overwrite it? (y/n): " answer
#    if [ "$answer" != "${answer#[Yy]}" ]; then
#        sudo cp "$repo/$g_shell_name" "$g_shell_path" # Перезапись
#        sudo chmod +x "$g_shell_path/$g_shell_name"
#        # echo "Copying $g_shell_name to $g_shell_path successfully complete"
#    else
#        echo "Copying $g_shell_name aborted"
#    fi
else
    sudo cp $repo"$g_shell_name" "$g_shell_path" # Копирование
    echo "Copying $g_shell_name to $g_shell_path successfully complete"
    sudo chmod +x "$g_shell_path/$g_shell_name"
fi

cfg_name=chopper_tune.cfg
cfg_path=~/printer_data/config/
cfg_incl_path=~/printer_data/config/printer.cfg

ln -sf "$repo_path/$cfg_name" $cfg_path # Перезапись

# Добавление строки [include] в printer.cfg
if [ -f "$cfg_incl_path" ]; then
    if ! grep -q "^\[include $cfg_name\]$" "$cfg_incl_path"; then
        sudo service klipper stop
        sed -i "1i\[include $cfg_name]" "$cfg_incl_path"
        # echo "Including $cfg_name to $cfg_incl_path successfully complete"
        sudo service klipper start
    else
        echo "Including $cfg_name aborted, $cfg_name already exists in $cfg_incl_path"
    fi
fi
# Добавление строки [respond] в printer.cfg
if [ -f "$cfg_incl_path" ]; then
    if ! grep -q "^\[respond\]$" "$cfg_incl_path"; then
        sudo service klipper stop
        sed -i "1i\[respond]" "$cfg_incl_path"
        # echo "Including [respond] to $cfg_incl_path successfully complete"
        sudo service klipper start
    else
        echo "Including [respond] aborted, [respond] already exists in $cfg_incl_path"
    fi
fi

blk_path=~/printer_data/config/moonraker.conf
# Добавление блока обновления в moonraker.conf
if [ -f "$blk_path" ]; then
    if ! grep -q "^\[update_manager chopper-resonance-tuner\]$" "$blk_path"; then
        read -p " Do you want to install updater? (y/n): " answer
        if [ "$answer" != "${answer#[Yy]}" ]; then
          sudo service moonraker stop
          sed -i "\$a \ " "$blk_path"
          sed -i "\$a [update_manager chopper-resonance-tuner]" "$blk_path"
          sed -i "\$a type: git_repo" "$blk_path"
          sed -i "\$a path: $repo_path" "$blk_path"
          sed -i "\$a origin: https://github.com/MRX8024/$repo.git" "$blk_path"
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

sudo chmod -R +x "$repo_path/"

# Удаление директории репозитория
#sudo rm -rf ~/chopper-resonance-tuner
#echo "Temp repository was removed"