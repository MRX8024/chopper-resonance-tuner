1. Скачайте репозиторий на хост в ~/Chopper-tuning-guide
2. Распакуйте его - `unzip ~/Chopper-tuning-guide.zip -d ~/Chopper-tuning-guide`
3. Создайте папку для выходных файлов, по умолчанию - `mkdir ~/printer_data/config/adxl_results/chopper_magnitude`
4. Создайте папку для хранения обработчика, и переместите его в неё - `mkdir ~/printer_data/config/scripts & cp ~/Chopper-tuning-guide/chopper_plot.py ~/printer_data/config/scripts/chopper_plot.py`
5. Переместите макрос в директорию конфигурации принтера `cp ~/Chopper-tuning-guide/chopper_tune.cfg ~/printer_data/config/chopper_tune.cfg`
6. Установите через kiauh, либо переместите модуль gcode_shell_command.py в клиппер - `cp ~/Chopper-tuning-guide/gcode_shell_command.py ~/klipper/klippy/extras/gcode_shell_command.py`
7. Добавьте в конфигурацию принтера строки -
```
[respond]
[include scripts/chopper-resonance-tuner/chopper_tune.cfg]
```
Если вы использовали НЕ стандартные пути, не забудьте поправить их в `chopper_plot.py`, `[gcode_shell_command chop_tune] в chopper_tune.cfg`

Также, по желанию, можно добавить раздел обновления в moonraker для последующих обновлений через ведморду в разделе обновлений.
```
[update_manager chopper-resonance-tuner]
type: git_repo
path: ~/printer_data/config/scripts/chopper-resonance-tuner
origin: https://github.com/MRX8024/chopper-resonance-tuner.git
is_system_service: False
managed_services: klipper
```