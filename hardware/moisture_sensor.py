import time
from typing import Tuple

from Adafruit_ADS1x15 import ADS1115


class MoistureSensor:
    """
    Soil moisture sensor using ADS1115 ADC.
    
    :param channel: ADC channel number (0-3)
    :param air_voltage: Voltage when sensor is in air (typically 2.3V)
    :param optimal_voltage: Voltage for optimal moisture (typically 1.0V)
    """

    def __init__(self, channel: int = 0, air_voltage: float = 2.3, optimal_voltage: float = 1.0) -> None:
        self.adc = ADS1115()
        self.channel = channel
        self.gain = 1  # For voltage range 0-4.096V 
        self.air_voltage = air_voltage
        self.optimal_voltage = optimal_voltage
        self.max_valid_voltage = 2.4  # Anything above this suggests sensor isn't in soil

    def read_values(self) -> Tuple[int, float]:
        """
        Read raw ADC value and converted voltage.
        
        :return: Tuple of (raw value, voltage)
        :rtype: Tuple[int, float]
        """
        value = self.adc.read_adc(self.channel, gain=self.gain)
        voltage = value * (4.096 / 32767)  # Convert to voltage
        return value, voltage

    def get_moisture_status(self) -> Tuple[float, str]:
        """
        Get moisture percentage and status with validation.
        
        :return: Tuple of (moisture percentage, status string)
        :rtype: Tuple[float, str]
        :raises: ValueError if sensor appears to be in air
        """
        _, voltage = self.read_values()

        # Validate sensor placement
        if voltage >= self.max_valid_voltage:
            return 0, "SENSOR NOT IN SOIL"

        # Convert to percentage (0% = air reading, 100% = optimal)
        moisture = ((self.air_voltage - voltage) /
                    (self.air_voltage - self.optimal_voltage) * 100)
        moisture = max(0, min(100, moisture))

        # Determine status based on voltage ranges
        if voltage > self.air_voltage:
            status = "ERROR: READING TOO HIGH"
        elif voltage < 0.5:  # Extremely wet or short circuit
            status = "ERROR: READING TOO LOW"
        elif voltage > 2.0:
            status = "VERY DRY"
        elif voltage > 1.5:
            status = "DRY"
        elif voltage > 0.8:
            status = "OPTIMAL"
        else:
            status = "TOO WET"

        return moisture, status


if __name__ == "__main__":
    sensor = MoistureSensor(channel=3)

    try:
        print("Starting soil moisture monitoring...")
        while True:
            raw, voltage = sensor.read_values()
            moisture, status = sensor.get_moisture_status()
            print(f"Raw: {raw} | Voltage: {voltage:.2f}V | Moisture: {moisture:.1f}% | Status: {status}")
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nProgram terminated by user")
