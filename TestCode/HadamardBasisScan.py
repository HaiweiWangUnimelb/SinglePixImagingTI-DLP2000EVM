import Adafruit_BBIO.ADC as ADC
import numpy as np
from scipy.linalg import hadamard
import time
from os import system

PIN_IN = "AIN0"
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 360

SAMPLE_RATE = 200
SAMPLE_INTERVAL = 0.01

class HadamardBasisScan:

    def __init__(self,resolution,pixel_size):

        self.res = resolution
        self.pixel_size = pixel_size

        if IMAGE_WIDTH % pixel_size != 0 or IMAGE_HEIGHT % pixel_size != 0:
            print("Pixel size does not divide both image height and width")

        self.result = np.zeros((self.res,self.res))
                
    def run(self,waitTime = 0.07, benchmark = False):
        
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

        patterns = hadamard(self.res*self.res)

        # Data acquisition loop

        for pattern_index in range(self.res**2):

            pattern = patterns[pattern_index].reshape((self.res,self.res))
            disp_pattern = (pattern + 1) / 2

            # display pattern
            system("i2cset -y 2 0x1b 0xa3 0x00 0x00 0x00 0x01 i") # freeze framebufffer
            for k in range(self.pixel_size):
                for m in range(self.pixel_size):
                    fb[y_start+k:y_end+k:self.pixel_size, x_start+m:x_end+m:self.pixel_size] = disp_pattern * 4294967295
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
            for k in range(self.pixel_size):
                for m in range(self.pixel_size):
                    fb[y_start+k:y_end+k:self.pixel_size, x_start+m:x_end+m:self.pixel_size] = disp_pattern * 4294967295
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

    def printResultAsList(self):

        print(list(self.result.flatten()))

    def resultToCSV(self, filename):
        
        if filename.split('.')[-1] != "csv":
            print("Error: output file format name is not csv")
            return None

        np.savetxt(filename, self.result.flatten(), delimiter=',', fmt='%s')
