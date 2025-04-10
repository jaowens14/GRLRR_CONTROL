import smbus2
import time

MCP4728_ADDRESS = 0x60
ADS1115_ADDRESS = 0x48

bus = smbus2.SMBus(1)

def set_dac_voltage(channel, voltage):
    dac_value = int((voltage / 5.0) * 4095)
    bus.write_i2c_block_data(MCP4728_ADDRESS, channel, [dac_value >> 8, dac_value & 0xFF])

def read_adc(channel):
    config = 0x8483 | (channel << 12)
    bus.write_i2c_block_data(ADS1115_ADDRESS, 0x01, [config >> 8, config & 0xFF])
    time.sleep(0.1)
    data = bus.read_i2c_block_data(ADS1115_ADDRESS, 0x00, 2)
    adc_value = (data[0] << 8) | data[1]
    return adc_value

set_dac_voltage(0,2.5)
time.sleep(1)
feedback = read_adc(0)
print("Feedback value:", feedback)