This suite is for carrying out basic single pixel imaging/ ghost imaging on the TI DLP2000EVM.

The scripts are classes which need to be imported, either in the Python terminal or in another Python script, on the BeagleBone.

Example usage of the GhostImageScan module:

Python terminal
===========================================================
>>> from GhostImageScan import GhostImageScan

Creating an instance of an imaging experiment:
>>> foo = GhostImageScan(32,10) <-- 32x32 resolution with pixel size of 10

Run a designated number of iterations of ghost imaging:
>>> foo.run(500) <-- display 500 patterns

The run function can be called any number of times, since image output is saved in the object:

>>> foo.run(500)
followed by
>>> foo.run(500)
is equivalent to
>>> foo.run(500+500)

Printing result:
The result is printed as a list of numbers, image display on the BeagleBone was not implemented.
To see the result displayed as a plot, first the printed list is copied onto a personal computer running Python with matplotlib and numpy.
The list is cast into an array, reshaped and plotted using the imshow function from pyplot.

>>> foo.printResultAsList()
prints to the terminal for example
[0.0033434, 0.15, ... ]


The HadamardBasisScan module is almost exactly the same as the GhostImaging module. Due to the difference in their algorithm, the basis scan
does not require any arguments to its run() function and the run() function only needs to be called once.
