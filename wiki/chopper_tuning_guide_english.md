### The method of semi-automatic calibration of driver parameters is based on Trinamic’s [manual](https://www.analog.com/en/app-notes/AN-001.html) for “behavioral” motor tuning.


### 1. Install the calibration script on the printer host. (the klipper will reboot!)
```
cd ~
git clone https://github.com/MRX8024/chopper-resonance-tuner
bash ~/chopper-resonance-tuner/install.sh
```
If everything went well, you will see folders with the program appear in your home directory (printer configuration), and into which the calibration results will be placed, as well as an already available macro from the macro panel on the main page of the Fluidd / Mainsail.
And if for some reason not, then install [manually](/wiki/manual_install_en.md).

2. Connect the accelerometer to the head, as for example when measuring resonances for input_shaper.

3. Calibration: (Further commands in this article will be interpreted with the minimum required parameters (functions))

   1. We determine the “resonating” speeds by entering the command `CHOPPER_TUNE FIND_VIBRATIONS=1` into the web terminal, you can additionally set the speed with the parameters `MIN_SPEED=20 MAX_SPEED=80`, the printer head will make runs at the specified speeds in increments of 1mm/s.
   2. After the macro is completed, the algorithm will automatically generate a table of data and graphics, place them in the `.../adxl_results/chopper_magnitude/` directory, download and open `interactive_plot.html`, and see the following picture -
   ![](/wiki/pictures/img_1.png)
   The graph will usually show 2 peaks, at a speed of about 50mm/s and 100mm/s - these are resonant speeds, we need the lowest of these speeds, for example, 55mm/s.
   3. Run the macro to iterate through all the chopper options at the previously selected speed, the command will look like this
   -`CHOPPER_TUNE TBL_MIN=0 TBL_MAX=3 TOFF_MIN=1 TOFF_MAX=8 MIN_HSTRT=0 MAX_HSTRT=7 MIN_HEND=2 MAX_HEND=15 MIN_SPEED=55 MAX_SPEED=55`. Check the availability of free space on the host, about half a GB is required for data.
   The data collection time will take approximately an hour or two, after completion we open the graph in the same way as the previous time, we get a graph of the form -
   ![](/wiki/pictures/img_2.png)
   In this example, the minimum vibrations are at TBL=0 and TOFF=8. Let's enlarge this area.
   ![](/wiki/pictures/img_3.png)
   4. Select the chopper option with the minimum magnitude value - these are the required parameters. It is also necessary to take into account that with large values of `TBL` and `TOFF` the motor frequency decreases, which leads to the appearance of unpleasant noise, and in some cases resonances may appear at high speeds, which will only worsen the performance of the chopper. Find the edge, usually reducing `TOFF` to values 0-4.
   We enter them into the drivers section in printer.cfg, example -
   ```
   [tmc**** stepper_x]
   cs_pin: PC4
   ...
   driver_TBL: 0
   driver_TOFF: 8
   driver_HSTRT: 5
   driver_HEND: 5
   ```

   5. You can repeat the procedure with smaller variations of the chopper, for example, only `TBL=0` and `TOFF=8` and iterate over the full ranges of `HSTRT` and `HEND`, but with more repetitions of `ITERATIONS`. In this case, the graph will be based on average results to reduce the influence of mechanics on the readings.
   6. If you are the lucky owner of a TMC2240 or TMC5160, then after setting all of the above registers, you have the opportunity to configure another parameter called `TPFD`.
   It is responsible for dampening of motor mid-range resonances, and has a value range of '0-15', in addition to vibration analysis, as in the previous paragraphs, I recommend that you configure it based on sound.
   The command looks like this, with the correct registers found above, two `ITERATIONS` - for greater accuracy, and the speed you can set at which you usually print - `CHOPPER_TUNE TBL_MIN=0 TBL_MAX=0 TOFF_MIN=8 TOFF_MAX=5 MIN_HSTRT=5 MAX_HSTRT=5 MIN_HEND=5 MAX_HEND=5 MIN_TPFD=0 MAX_TPFD=15 MIN_SPEED=55 MAX_SPEED=55 ITERATIONS=2`


4. Description of the program functionality -
   1. `CURRENT_MIN_MA` and `CURRENT_MAX_MA` - are responsible for changes in the supplied current `(mA)` to stepper motors in 10mA steps, for example, if you have enough torque that the stepper motors produce, you can reduce their current in order to make the system quieter, this function and allows you to analyze whether the game is worth the candle.
   2. `TBL_MIN-0` and `TBL_MAX-3`, `TOFF_MIN-1` and `TOFF_MAX-8`, `MIN_HSTRT-0` and `MAX_HSTRT-7`, `MIN_HEND-0` and `MAX_HEND-15`, `MIN_TPFD-0` and `MAX_TPFD-15` are actually also responsible for enumerating parameters, in this case, registers of driver pairs. Their range of work and search is indicated, and `HSTRT_HEND_MAX-16` is a const. ([more](https://www.analog.com/en/app-notes/AN-001.html))
   3. `MIN_SPEED` and `MAX_SPEED` - enumerate the speed range, with a step of `1mm/s`.
   4. `ITERATIONS` - the number of repetitions of measurements, for more accurate data.
   5. `TRAVEL_DISTANCE` - distance `(mm)` of the print head movement during which vibrations are read. By default, the auto is calculated based on the printer's capabilities and travel time.
   6. `ACCELEROMETER` - an accelerometer that will be used to measure vibrations, auto will be detected if one is specified in the `resonance_tester` configuration, otherwise adxl345 will be used.
   7. `FIND_VIBRATIONS` - mode for measuring vibrations from speed, useful in order to remove resonant speeds from everyday printing, as for step 3.1 of this article. Values ​​- `(True / False), (1 / 0)`

The `'default'` parameters mean that if there is no argument, this variable will assign the default parameters from printer.cfg, or calculate the minimum required ones.
