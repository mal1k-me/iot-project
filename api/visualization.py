import base64
import io
from collections import deque
from datetime import datetime

import matplotlib.pyplot as plt
import seaborn as sns


class SensorVisualizer:
    """
    Visualization handler for soil moisture sensor data.
    
    Generates time series plots of moisture and voltage data with 
    Material Design themed styling.
    
    :param max_points: Maximum number of points to show in plots
    :type max_points: int
    """

    def __init__(self, max_points=100):
        self.max_points = max_points
        self.timestamps = deque(maxlen=max_points)
        self.moisture_values = deque(maxlen=max_points)
        self.voltage_values = deque(maxlen=max_points)

        # Set style
        plt.style.use('dark_background')
        sns.set_style("darkgrid", {"axes.facecolor": "#1e1e1e"})

        # Update thresholds based on real moisture values
        self.optimal_low = 20  # Below 20% is too dry
        self.optimal_high = 80  # Above 80% is too wet

        # Update voltage thresholds
        self.error_high = 2.4  # Not in soil
        self.very_dry = 2.0
        self.dry = 1.5
        self.optimal = 0.8
        self.too_wet = 0.5

    def add_datapoint(self, data):
        self.timestamps.append(datetime.fromtimestamp(data['timestamp']))
        self.moisture_values.append(data['moisture'])
        self.voltage_values.append(data['voltage'])

    def save_plot(self, buffer) -> None:
        """
        Save current plot to a buffer.
        
        :param buffer: BytesIO buffer to save the plot to
        :type buffer: io.BytesIO
        """
        fig = self._generate_figure()
        fig.savefig(buffer, format='png', facecolor='#121212')
        plt.close(fig)

    def _generate_figure(self):
        """
        Generate the plot figure.
        
        :return: Matplotlib figure object
        :rtype: matplotlib.figure.Figure
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        fig.patch.set_facecolor('#121212')

        # Moisture plot with thresholds
        timestamps = list(self.timestamps)
        if timestamps:  # Only if we have data
            # Create threshold lines across full time range
            xmin, xmax = min(timestamps), max(timestamps)

            # Fill zones (only showing valid ranges)
            ax1.fill_between(timestamps, 0, 20,
                             color='#cf6679', alpha=0.2)  # Too wet
            ax1.fill_between(timestamps, 20, 40,
                             color='#ff7b00', alpha=0.2)  # Wet
            ax1.fill_between(timestamps, 40, 60,
                             color='#03dac6', alpha=0.2)  # Optimal
            ax1.fill_between(timestamps, 60, 80,
                             color='#ff7b00', alpha=0.2)  # Dry
            ax1.fill_between(timestamps, 80, 100,
                             color='#cf6679', alpha=0.2)  # Very dry

            # Add threshold lines
            ax1.axhline(y=self.optimal_low, color='#cf6679', linestyle='--', alpha=0.8)
            ax1.axhline(y=self.optimal_high, color='#ff7b00', linestyle='--', alpha=0.8)

            # Update zone labels
            ax1.text(xmax, self.optimal_low / 2, 'Too Dry',
                     color='#cf6679', ha='right', va='center')
            ax1.text(xmax, (self.optimal_high + self.optimal_low) / 2, 'Optimal Range',
                     color='#03dac6', ha='right', va='center')
            ax1.text(xmax, (100 + self.optimal_high) / 2, 'Too Wet',
                     color='#ff7b00', ha='right', va='center')

            # Add threshold lines for voltage reference
            ax2.axhline(y=self.error_high, color='#cf6679', linestyle=':', alpha=0.5)
            ax2.axhline(y=self.very_dry, color='#ff7b00', linestyle='--', alpha=0.5)
            ax2.axhline(y=self.optimal, color='#03dac6', linestyle='--', alpha=0.5)
            ax2.text(xmax, self.error_high, 'Sensor not in soil',
                     color='#cf6679', ha='right', va='bottom')

            # Filter out invalid readings from the plot
            valid_indices = [i for i, v in enumerate(self.voltage_values)
                             if v < self.error_high]
            valid_timestamps = [timestamps[i] for i in valid_indices]
            valid_moisture = [list(self.moisture_values)[i] for i in valid_indices]

            # Plot only valid readings
            sns.lineplot(x=valid_timestamps, y=valid_moisture,
                         color='#bb86fc', ax=ax1, linewidth=2)

        # Main moisture line
        sns.lineplot(x=timestamps, y=list(self.moisture_values),
                     color='#bb86fc', ax=ax1, linewidth=2)

        ax1.set_title('Moisture Level Over Time', color='#ffffff')
        ax1.set_ylabel('Moisture %', color='#ffffff')
        ax1.set_ylim(0, 100)  # Fix y-axis range
        ax1.grid(True, alpha=0.2)

        # Voltage plot
        sns.lineplot(x=list(self.timestamps), y=list(self.voltage_values),
                     color='#03dac6', ax=ax2)
        ax2.set_title('Voltage Reading Over Time', color='#ffffff')
        ax2.set_ylabel('Voltage (V)', color='#ffffff')
        ax2.grid(True, alpha=0.2)

        # Format
        for ax in [ax1, ax2]:
            ax.tick_params(colors='#ffffff')
            ax.set_xlabel('Time', color='#ffffff')

        plt.tight_layout()
        return fig

    def generate_plot(self) -> str:
        """
        Generate base64 encoded plot string.
        
        :return: Base64 encoded PNG image
        :rtype: str
        """
        buffer = io.BytesIO()
        self.save_plot(buffer)
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
