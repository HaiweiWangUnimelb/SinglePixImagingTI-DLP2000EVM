# Usage

This suite is for carrying out basic single pixel imaging/ ghost imaging on the TI DLP2000EVM.

The scripts are classes which need to be imported, either in the Python terminal or in another Python script, on the BeagleBone.

Example usage of the GhostImageScan module:

```python
>>> from GhostImageScan import GhostImageScan
```

Creating an instance of an imaging experiment:
```python
>>> foo = GhostImageScan(32,10) # 32x32 resolution with pixel size of 10
```
Run a designated number of iterations of ghost imaging:
```python
>>> foo.run(500) # display and measure from 500 patterns
```
The run function can be called any number of times, since image output is saved in the object:

```python
>>> foo.run(500)
```
followed by
```python
>>> foo.run(500)
```
is equivalent to
```python
>>> foo.run(500+500)
```

Viewing result:

```python
>>> foo.printResultAsList()
```
prints to the terminal for example
[0.0033434, 0.15, ... ]

Another way of visualising the result is to use the function which creates a jpeg image in the current directory:

```python
>>> foo.resultToImage("myResult.jpg")
```

This option requires [pillow](https://pillow.readthedocs.io/en/stable/) to be installed in the Python environment.

The HadamardBasisScan module is almost exactly the same as the GhostImaging module. Due to the difference in their algorithm, the basis scan
does not require any arguments to its run() function and the run() function only needs to be called once.
