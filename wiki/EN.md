
# Welcome to the project of modifying registers for TRINAMIC drivers, but now ANALOG DEVICES...

## About the project
The Klipper firmware provides powerful capabilities for controlling 3D printers, however, in order to achieve maximum performance and proper operation of such an important component as the “drive”, careful tuning of stepper motor control parameters is required.
Our project was created to provide you with guidance on optimizing driver parameters for various types of steppers.

## Introduction
Why is it needed?
First you need to know that there are at least 2 “main” registers, these are none other than TBL (Comparator blank time) and TOFF (Turn-Off Time), they are both responsible for turning off and supplying power to the mosfets, which in turn open to motor windings, thereby affecting the loss of currents. Based on this little context,
we can already conclude that thanks to the selection of the correct current control on our windings, we reduce interference, “extra” currents that interfere with the operation of the motor, knock off the rotor angle, vibrate, and the energy is simply transformed into heat, absorbed by the housing, and this, in turn, means that the rotor torque is also lost.
To summarize, of course stepper motors can be used on "defaults" registers, but this is simply inefficient. After conducting research, we found out that the correct selection of motor control modes gives it up to 30% of torque! As for heat generation, we have not carried out precise measurements, but it is decreasing.
It is important to note that registers are relevant only for a specific pair: driver - motor, and depend on the specific implementation of the driver. It is also worth considering that the characteristics of the motor have an average variation of +-20%, as does the measurement error, accelerometer, so you should not be surprised at the variation of the parameters at different settings.

## Assistance
We welcome contributions from the community! If you have experience and advice on tuning stepper motors, do not hesitate to share the material with us. Provide information about the tested stepper motors in the format (see below), and of the above, everything except the stepper motor model is already automatically generated in the file name.
```
interactive_plot_accelerometer_stepper_driver_resistor_date.html
```

### Further [instructions](/wiki/wiki.md), good luck!

### [Support](https://ko-fi.com/altzbox) project

### Contacts - @altzbox @mrx8024 telegram / discord

### This project is distributed under the [MIT License](/wiki/license.txt)
