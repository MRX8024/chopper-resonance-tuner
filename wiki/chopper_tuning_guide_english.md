### The method of semi-automatic calibration of driver parameters is based on Trinamic’s [manual](https://www.analog.com/en/app-notes/AN-001.html) for “behavioral” motor tuning.


### 1. Install the calibration script on the printer host. (the klipper will reboot!)

```shell
   cd ~
   git clone https://github.com/eoyilmaz/chopper-resonance-tuner
   bash ~/chopper-resonance-tuner/install.sh
```

If everything went well, you will see folder - `adxl_results` in your printer
home directory (~/printer_data/config), into which the calibration results will
be placed, as well as an already available macro from the macro panel on the
main page of the Fluidd / Mainsail.

And if for some reason not, then install [manually](/wiki/manual_install_en.md).

2. Connect the accelerometer to the motor by screwing it in, this guarantees
   accurate vibration measurement.

   However, it is possible to connect, as for example when measuring resonances,
   for input_shaper - to the print head / bed, depending on the type of printer,
   selected measuring axis, to collect vibrations.

   This method may give incorrect data if the mechanics are crooked, but on
   properly assembled printers, it is not inferior to the first.

3. Calibration: (Further commands in this article will be interpreted with the
   minimum required parameters, all supported are listed at the bottom of the manual).

   1. We determine the resonant speeds by entering the command:

      ```G-code
      CHOPPER_TUNE FIND_RESONANCES=1 DIRECTION=1
      ```

      into the web terminal.

   2. After the macro is completed, the algorithm will report the speed that
      has the maximum resonances and automatically generate a table of data and
      graphics, place them in the `.../adxl_results/chopper_magnitude/`
      directory, download and open `{date}_interactive_plot_*.html`, and see the
      following picture:

   ![](/wiki/pictures/img_1.png)

   The graph will usually show 2 peaks, at a speed of about 50mm/s and 100mm/s,
   these are resonant speeds, we need the lowest of these speeds, for example,
   55mm/s.

   3. Run the macro to iterate through all the chopper options at the previously
      selected speed, the command will look like this:

      ```G-code
      CHOPPER_TUNE MIN_SPEED=55 MAX_SPEED=55
      ```

   The data collection time will take approximately two hours (depending on
   kinematics), after completion we open the graph in the same way as the
   previous time, we get a graph of the form:

   ![](/wiki/pictures/img_2.png)

   In this example, the minimum vibrations are at TBL=0 and TOFF=8. Let's
   enlarge this area.

   ![](/wiki/pictures/img_3.png)

   4. Select the chopper option with the minimum magnitude value - these are
   the required parameters. It is also necessary to take into account that with
   large values of `TBL` and `TOFF` the motor frequency decreases, which leads
   to the appearance of nasty high frequency noise.

   If the vibration decreases with the occurrence of this phenomenon, move to a
   pleasant range of work between vibrations and noise, by using the program
   functionality (entering the registers ranges you need into the macro
   parameters), if this bothers you. If not, then it would be preferable to
   leave the high-frequency squeak.

   We enter them into the drivers section in printer.cfg, example:

   ```ini
   [tmc**** stepper_*]
   cs_pin: PC4
   ...
   driver_TBL: 0
   driver_TOFF: 8
   driver_HSTRT: 5
   driver_HEND: 5
   ```

   5. You can repeat the procedure with smaller variations of the chopper, for
   example, only `TBL=0` and `TOFF=8` and iterate over the full ranges of
   `HSTRT` and `HEND`, but with more repetitions of `ITERATIONS`. In this case,
   the graph will be based on average results to reduce the influence of
   mechanics on the readings.

   6. If you are the lucky owner of a TMC2240 or TMC5160, then after setting
   all of the above registers, you have the opportunity to configure another
   parameter called `TPFD`.

   It is responsible for damping the average resonances of the motor, and has a
   value range of `0-15`. Set its parameter value to `driver_TPFD: 0`, or
   calibrate it.

   The command with the data registers found above, two `ITERATIONS`, for
   greater accuracy, and resonant speed looks like this:

   ```G-code
   CHOPPER_TUNE TBL_MIN=0 TBL_MAX=0 TOFF_MIN=8 TOFF_MAX=8 HSTRT_MIN=5 HSTRT_MAX=5 HEND_MIN=5 HEND_MAX=5 TPFD_MIN=0 TPFD_MAX=15 MIN_SPEED=55 MAX_SPEED=55 ITERATIONS=2
   ```

### Description of the program functionality

The values `'default'` in parameters mean that if there is no argument, this
variable will assign the default parameters from printer.cfg, or calculate the
minimum required ones.

1. `AXIS`

   Direction `X/Y/Z` in which the measurement will be run.

2. `CURRENT_MIN_MA` and `CURRENT_MAX_MA`

   These are responsible for changes in th supplied current (mA) to stepper
   motors in 25mA steps. For example, if you have enough torque that the
   stepper motors produce, you can reduce their current to make the system
   quieter and reduce motor heating. This function partly allows you to analyze
   is it worth it, or just choose the current you need in measure.

3. `TBL_MIN-0` and `TBL_MAX-3`, `TOFF_MIN-1` and `TOFF_MAX-8`, `HSTRT_MIN-0`
   and `HSTRT_MAX-7`, `HEND_MIN-0` and `HEND_MAX-15`, `TPFD_MIN-0` and
   `TPFD_MAX-15` are actually also responsible for enumerating parameters, in
   this case, registers of driver/s. Their range of work and search is
   indicated.

4. `HSTRT_HEND_MAX-16`

   Limit on the sum of `HSTRT and HEND`, change is undesirable. ([more](https://www.analog.com/media/en/technical-documentation/data-sheets/TMC5160A_datasheet_rev1.17.pdf))

5. `MIN_SPEED` and `MAX_SPEED`

   Enumerate the speed range, with a step of `SPEED_CHANGE_STEP`. By default,
   it is calculated based on the required rpm by gear ratios.

6. `ITERATIONS`

   The number of repetitions of measurements, for more accurate data.

7. `TRAVEL_DISTANCE`

   Distance `(mm)` of the print head movement during which vibrations are read.
   By default, is calculated based on the printer's capabilities and
   measurement time.

8. `ACCELEROMETER`

   An accelerometer that will be used to measure vibrations, auto will be
   detected if one is specified in the `resonance_tester` configuration,
   otherwise, without specifying will be applied `adxl345`.

9. `FIND_RESONANCES`

   Mode to measure resonances at different speeds, so that the measurement is
   done at the most resonant speed and the system finds the best register
   values for the lowest vibrations/noise. Values: `(True / False), (1 / 0)`

10. `DIRECTON`

   The measurement direction. If set to 1 the measurement will be done towards
   the positive direction, and if set to -1 the measurement will be done
   towards the negative direction. Values: `(1 / -1)`.

11. `SEARCH_METHOD`

   The iteration method to use when looking for the next values for chopper
   parameters. Defaults to `brute_force`. Adaptive uses an adaptive optimization
   algorithm which generally works ~10-20x faster in finding the smallest
   vibration parameters. Values: `brute_force / bruteforce / adaptive`.

12. `RUN_PLOTTER`

   Run the graph generation script. Values - `(True / False), (1 / 0)`


### About Core XY Printers

This fork of the original library uses stepper motor isolation for CoreXY
printers by doing diagonal moves so that the steppers are individually
activated and calibrated.

Here are some results compared to the original library:

Initial Vibrations:

   Before:

   ![Measured Vibrations Before](/wiki/pictures/core_xy_isolation_vibrations_before.png)

   After:

   ![Measured Vibrations After](/wiki/pictures/core_xy_isolation_vibrations_after.png)

As you see, by moving on diagonals and isolating a particular stepper motor,
the peak resonance speed reduces by `sqrt(2)` from `89 mm/s` to `63 mm/s`
as we are now moving in only one logical axis.

Measured vibrations:

   Before:

   ![Vibrations Before](/wiki/pictures/core_xy_isolation_before.png)

   After:

   ![Vibrations After](/wiki/pictures/core_xy_isolation_after.png)

As seen in the images above, by isolating the stepper motors we achieved much
lower vibration levels as the second stepper driver is not spoiling our
measurements anymore.