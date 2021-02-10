# Instructions

### Power

The projector driver board requires a 5V power supply, supplied via a barrel jack.
The BeagleBone can be powered through the USB connection from a computer.

### Interfacing with the BeagleBone

First, connect the BeagleBone and PC with USB.

Then, the best way to access the BeagleBone is by connecting to 192.168.7.2 on a browser. This opens an IDE environment where code can be edited and run.

### BeagleBone pins

Pin 39 is the "AIN0" (analog in) input used in the code.
The complete BeagleBone pin labelling can be found at https://beagleboard.org/Support/bone101

### Experimental setup

Positive lenses are used to decrease the image size of the projected pattern from the DLP. After passing through the object, the light is focused into a small blur spot which can fit
entirely on a small-area photodiode.

The voltage signal of the photodiode is assumed to be directly proportional to the total radiant flux after the light has passed through the object, this signal is used in the cross-correlation with the
projected pattern to reconstruct the image of the object.

