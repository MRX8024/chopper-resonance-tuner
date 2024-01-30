1. Upload the repository to the host at ~/Chopper-tuning-guide
2. Unpack it - `unzip ~/Chopper-tuning-guide.zip -d ~/Chopper-tuning-guide`
3. Create a dir to export files, default is `mkdir ~/printer_data/config/adxl_results/chopper_magnitude`
4. Create a dir to store the handler and place it in it - `mkdir ~/printer_data/config/scripts & cp ~/Chopper-tuning-guide/chopper_plot.py ~/printer_data/config/scripts/chopper_plot.py`
5. Move the macros to the printer configuration directory `cp ~/Chopper-tuning-guide/chopper_tune.cfg ~/printer_data/config/chopper_tune.cfg`
6. Install via kiauh, or move the gcode_shell_command.py module in the klipper - `cp ~/Chopper-tuning-guide/gcode_shell_command.py ~/klipper/klippy/extras/gcode_shell_command.py`
7. Add lines to the configuration -
```
[reply]
[include scripts/chopper-resonance-tuner/chopper_tune.cfg]
```
If you used NOT standard paths, be sure to edit them in `chopper_plot.py`, `[gcode_shell_commandhop_tune] in Chopper_tune.cfg`

You can also optionally add an update section to moonraker for subsequent updates via Fluidd / Mainsail update managers.
```
[update_manager chopper-resonance-tuner]
type: git_repo
path: ~/printer_data/config/scripts/chopper-resonance-tuner
origin: https://github.com/MRX8024/chopper-resonance-tuner.git
is_system_service: False
```