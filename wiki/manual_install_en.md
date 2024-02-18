1. Create a folder for the output files, by default - `sudo mkdir ~/printer_data/config/adxl_results/chopper_magnitude`
2. Download a program - `sudo git clone https://github.com/MRX8024/chopper-resonance-tuner`
3. Give permissions to run files - `sudo chmod -R +x ~/chopper-resonance-tuner/`
4. Install via kiauh, or move the gcode_shell_command.py module from repo to the klipper - `cp -i ~/chopper-resonance-tuner/gcode_shell_command.py ~/klipper/klippy/extras/`
7. Add lines to the configuration -
```
[respond]
[include chopper_tune.cfg]
```
If you used NOT standard paths, be sure to edit them in `chopper_plot.py`, `[gcode_shell_commandhop_tune] in Chopper_tune.cfg`

You can also optionally add an update section to moonraker for subsequent updates via Fluidd / Mainsail update managers.
```
[update_manager chopper-resonance-tuner]
type: git_repo
path: ~/chopper-resonance-tuner
origin: https://github.com/MRX8024/chopper-resonance-tuner.git
is_system_service: False
managed_services: klipper
```