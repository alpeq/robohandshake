# Last version on device!!
import sys
import json
import Adafruit_BBIO.ADC as ADC
import time 

ADC.setup()


def read_pins():
    ''' Function to read pins from the board '''
    value0 = ADC.read("P9_39") # AIN0
    #value = ADC.read_raw("P9_39") # AIN0
    value1 = ADC.read("P9_40") # AIN1
    #value = ADC.read_raw("P9_40") # AIN1
    value2 = ADC.read("P9_37") # AIN2
    
    return {"ain0":100*round(value0,2), "ain1":100*round(value1,2), "ain2":100*round(value2,2)}


def main_read_sensors(filename):
    ''' Loop to iterate through the readings and write '''
    try:
        with open(file_name, 'w') as file:
            while True:
                output = read_pins()
                out_dump =json.dumps(output)
                file.write(out_dump)
                #print(out_dump)
                time.sleep(0.1)

    except KeyboardInterrupt:
        pass
    
    return



if __name__ == "__main__":
    # Check if filename is provided as an argument
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <file_name>")
        sys.exit(1)

    file_name = sys.argv[1]  # Get the file name from command line arguments
    main_read_sensors(file_name)
