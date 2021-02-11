import Adafruit_BBIO.ADC as ADC
import numpy as np
from os import system
import time

PIN_IN = "AIN0"
IMAGE_WIDTH = 640 # pixels
IMAGE_HEIGHT = 360 # pixels

SAMPLE_RATE = 200 # Hz
SAMPLE_INTERVAL = 0.01 # seconds

WHITE_PIX_VAL = 4294967295

class GhostImageScan:
    
    def __init__(self,resolution,pixel_size):
        """
        Parameters:

            resolution - an int greater than 0.
            pixel_size - an int greater than 0 and divides both 640 and 360,
                         resolution*pixel_size <= 360.

        Creates a GhostImageScan Object with the given parameters.
        """

        self.res = resolution
        self.pixel_size = pixel_size

        if IMAGE_WIDTH % pixel_size != 0 or IMAGE_HEIGHT % pixel_size != 0:
            print("Pixel size does not divide both image height and width")

        self.result = np.zeros((self.res,self.res))

        self.M = 0
                
    def run(self,N_iters, waitTime = 0.07, benchmark = False):
        """
        parameters:
            N_iters - an int greater than 0
        kwarg:
            waitTime - Time between pattern display and bucket detector reading.

        Runs the imaging experiment on a setup for N_iters number of patterns, improving upon the current result.
        """

        start_time = time.time()
        
        print("Running...")
        
        # Initialisation
        fb = np.memmap("/dev/fb0", dtype = "uint32", mode = "w+", shape = (IMAGE_HEIGHT, IMAGE_WIDTH))
        fb[:] = 0
        ADC.setup()

        samples_per_reading = int(SAMPLE_INTERVAL*SAMPLE_RATE)
        rest_time = 1/SAMPLE_RATE
        
        x_start = int( ( IMAGE_WIDTH - self.res*self.pixel_size )/ 2)
        x_end = int(IMAGE_WIDTH - ( IMAGE_WIDTH - self.res*self.pixel_size )/ 2)
        y_start = int( ( IMAGE_HEIGHT - self.res*self.pixel_size )/ 2)
        y_end = int(IMAGE_HEIGHT - ( IMAGE_HEIGHT - self.res*self.pixel_size )/ 2)

        patterns = ( np.random.randint(2, size=(N_iters,self.res**2)) * 2 )- 1

        # Data acquisition loop

        for pattern_index in range(N_iters):

            pattern = patterns[pattern_index].reshape((self.res,self.res))
            disp_pattern = (pattern + 1) / 2

            # display pattern
            system("i2cset -y 2 0x1b 0xa3 0x00 0x00 0x00 0x01 i") # freeze framebufffer
            fb[y_start:y_end, x_start:x_end] = np.repeat( np.repeat( disp_pattern * WHITE_PIX_VAL, self.pixel_size, axis=0), self.pixel_size, axis=1)
            system("i2cset -y 2 0x1b 0xa3 0x00 0x00 0x00 0x00 i") # unfreeze framebuffer

            # get readings from pattern
            time.sleep(waitTime)
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

        self.M = N_iters
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
        print(f"Number of patterns displayed: {self.M * 2}")
        print(f"Average framerate: {self.res**2 * 2 / self.time_taken: .2f}")

            
