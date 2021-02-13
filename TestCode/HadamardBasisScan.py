import Adafruit_BBIO.ADC as ADC
import numpy as np
from scipy.linalg import hadamard
import time
from os import system

# Constants

PIN_IN = "AIN0"
IMAGE_WIDTH = 640 # pixels
IMAGE_HEIGHT = 360 # pixels

SAMPLE_RATE = 200 # Hz
SAMPLE_INTERVAL = 0.01 # seconds

WHITE_PIX_VAL = 256**4 - 1 # Usually written as (255, 255, 255, 255), where each entry is an 8-bit integer. Instead of a tuple
                           # a 32-bit integer equivalent of the tuple is used to be able to perform scalar multiplication of arrays.

class HadamardBasisScan:

    def __init__(self,resolution,pixel_size):
        """
        Parameters:

            resolution - an int greater than 0 and is a power of 2
            pixel_size - an int greater than 0 and divides both 640 and 360,
                         resolution*pixel_size <= 360.

        Creates a HadamardBasisScan object with the given parameters.
        """

        self.res = resolution
        self.pixel_size = pixel_size

        if IMAGE_WIDTH % pixel_size != 0 or IMAGE_HEIGHT % pixel_size != 0:
            print("Pixel size does not divide both image height and width")

        self.result = np.zeros((self.res,self.res))

        self.time_taken = 1
                
    def run(self,waitTime = 0.07):
        """
        kwargs:
            waitTime - Time between pattern display and bucket detector reading.

        Runs the imaging experiment on a setup for a determined number of patterns given by
        N_patterns = resolution**2.
        """

        start_time = time.time()
        
        print("Running...")
        
        # Initialisation
        fb = np.memmap("/dev/fb0", dtype = "uint32",
                       mode = "w+", shape = (IMAGE_HEIGHT, IMAGE_WIDTH)) # numpy function which implements memory access features from c. Maps an array of the same size as the framebuffer directly to the framebuffer.
        fb[:] = 0 # Set the screen black
        ADC.setup()

        samples_per_reading = int(SAMPLE_INTERVAL*SAMPLE_RATE)
        rest_time = 1/SAMPLE_RATE
        
        x_start = int( ( IMAGE_WIDTH - self.res*self.pixel_size )/ 2)
        x_end = int(IMAGE_WIDTH - ( IMAGE_WIDTH - self.res*self.pixel_size )/ 2)
        y_start = int( ( IMAGE_HEIGHT - self.res*self.pixel_size )/ 2)
        y_end = int(IMAGE_HEIGHT - ( IMAGE_HEIGHT - self.res*self.pixel_size )/ 2)

        patterns = hadamard(self.res*self.res)

        # Data acquisition loop

        for pattern_index in range(self.res**2):

            pattern = patterns[pattern_index].reshape((self.res,self.res))
            disp_pattern = (pattern + 1) / 2

            # display pattern
            system("i2cset -y 2 0x1b 0xa3 0x00 0x00 0x00 0x01 i") # freeze framebufffer
            fb[y_start:y_end, x_start:x_end] = np.repeat( np.repeat(
                disp_pattern * WHITE_PIX_VAL, self.pixel_size, axis=0), self.pixel_size, axis=1)
                # use the numpy repeat function on both dimensions of the array to convert each entry into a block of the same values
                # of size pixel_size x pixel_size. Fast way of upscaling the resolution of a low resolution pattern.
            system("i2cset -y 2 0x1b 0xa3 0x00 0x00 0x00 0x00 i") # unfreeze framebuffer

            # get readings from pattern
            time.sleep(waitTime) # wait for voltage to stabilise. It was found that if waitTime is too low, the image visibility is poor.
            readings = []
            for i in range(samples_per_reading):
                readings.append(ADC.read(PIN_IN))
                time.sleep(rest_time)

            bucket_val = max(readings)

            # display inverse pattern
            inv_pattern = -pattern
            disp_pattern = (inv_pattern + 1) / 2
            system("i2cset -y 2 0x1b 0xa3 0x00 0x00 0x00 0x01 i") # freeze framebufffer
            fb[y_start:y_end, x_start:x_end] = np.repeat( np.repeat( disp_pattern * WHITE_PIX_VAL, self.pixel_size, axis=0), self.pixel_size, axis=1)
            system("i2cset -y 2 0x1b 0xa3 0x00 0x00 0x00 0x00 i") # unfreeze framebuffer

            # get readings from inverse pattern
            time.sleep(waitTime)
            readings = []
            for i in range(samples_per_reading):
                readings.append(ADC.read(PIN_IN))
                time.sleep(rest_time)

            inv_bucket_val = max(readings)

            self.result += (bucket_val - inv_bucket_val) * pattern

        fb[:] = 0
        
        print("Finished!")

        self.time_taken = time.time() - start_time

    def printResultAsList(self):

        print(list(self.result.flatten()))

    def resultToCSV(self, filename):
        """
        parameters

            filename - a string ending in .csv.

        Creates a csv file in the current directory with the given filename.
        """
        
        if filename.split('.')[-1] != "csv":
            print("Error: output file format name is not csv")
            return None

        np.savetxt(filename, self.result.flatten(), delimiter=',', fmt='%s')

    def resultToImage(self, filename):
        """
        parameters

            filename - a string ending in .jpg.

        Creates a jpeg image with size resolution by resolution that represents the
        result of the experiment.
        """

        try:
            from PIL import Image
        except:
            print("Error importing PIL, maybe it hasn't been installed? \n To install, search: pillow python.")
            return
        

        if filename.split('.')[-1] != "jpg":
            print("Error: output file format name is not jpg")
            return None
        
        
        im = Image.new("RGB", (self.res,self.res))
        pixels = im.load()

        max_val = np.amax(self.result)
        min_val = np.amin(self.result)
        val_range = max_val - min_val
        
        for x in range(self.res):
            for y in range(self.res):
                color = int( 255 * ( (self.result[y,x] - min_val ) / val_range ) ) 
                pixels[x,y] = (color,color,color)

        im.save(filename, "JPEG")

    def printLastRunStatistics(self):

        print(f"Total time taken: {self.time_taken:.3f} seconds")
        print(f"Number of patterns displayed: {self.res**2 * 2}")
        print(f"Average framerate: {self.res**2 * 2 / self.time_taken: .2f}")
        
