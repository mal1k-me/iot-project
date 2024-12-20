import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any


class DataLogger:
    """
    Data logger for soil moisture sensor readings.
    
    Handles storing and retrieving sensor data in daily JSON files.
    
    :param log_dir: Directory path for storing log files
    :type log_dir: str or Path
    """

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

    def get_log_file(self, date: datetime) -> Path:
        """
        Generate log file path for a specific date.
        
        :param date: Date for the log file
        :type date: datetime
        :return: Path object for the log file
        :rtype: Path
        """
        return self.log_dir / f"moisture_{date.strftime('%Y-%m-%d')}.json"

    def log_data(self, data: Dict[str, Any]) -> None:
        """
        Log sensor data to daily JSON file.
        
        :param data: Sensor data dictionary containing timestamp and readings
        :type data: Dict[str, Any]
        """
        filepath = self.get_log_file(datetime.fromtimestamp(data['timestamp']))

        # Load existing data or create new
        daily_data = []
        if filepath.exists():
            daily_data = json.loads(filepath.read_text())

        daily_data.append(data)
        filepath.write_text(json.dumps(daily_data, indent=2))

    def get_data_range(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Retrieve sensor data for a date range.
        
        :param start_date: Start date for data retrieval
        :type start_date: datetime
        :param end_date: End date for data retrieval
        :type end_date: datetime
        :return: List of sensor readings within the date range
        :rtype: List[Dict[str, Any]]
        """
        data = []
        current_date = start_date

        while current_date <= end_date:
            filepath = self.get_log_file(current_date)
            if filepath.exists():
                data.extend(json.loads(filepath.read_text()))
            current_date += timedelta(days=1)

        return data
