1. Create a folder for the output files, by default:

   ```shell
   mkdir ~/printer_data/config/adxl_results/chopper_magnitude
   ```

2. Download a program:

   ```shell
   git clone https://github.com/eoyilmaz/chopper-resonance-tuner
   ```

3. Create a link to the program:

   ```shell
   ln -sf ~/chopper-resonance-tuner/chopper_tune.cfg ~/printer_data/config/
   ```

4. Install via kiauh, or move the gcode_shell_command.py module from repo to
   the klipper:

   ```shell
   cp -i ~/chopper-resonance-tuner/gcode_shell_command.py ~/klipper/klippy/extras/
   ```

5. Install packages:

   ```shell
   sudo apt-get install libatlas-base-dev libopenblas-dev
   ```

   ```shell
   sudo apt-get install python3-tqdm python3-plotly python3-numpy python3-matplotlib
   ```

7. Add lines to the configuration -

   ```ini
   [respond]
   [include chopper_tune.cfg]
   ```

If you didn't use standard paths, be sure to edit them in `chopper_plot.py`,
`[gcode_shell_commandhop_tune]` in `Chopper_tune.cfg`

You can also optionally add an update section to `moonraker` for subsequent
updates via `Fluidd` / `Mainsail` update managers.

```ini
[update_manager chopper-resonance-tuner]
type: git_repo
path: ~/chopper-resonance-tuner/
origin: https://github.com/eoyilmaz/chopper-resonance-tuner.git
primary_branch: main
managed_services: klipper
```
