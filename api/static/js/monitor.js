class MoistureMonitor {
  constructor() {
    this.socket = io();
    this.setupSocketListeners();
  }

  setupSocketListeners() {
    this.socket.on("sensor_update", (data) => {
      this.updateSensorData(data);
      this.updatePlot(data.plot);
    });
  }

  updateSensorData(data) {
    // Update sensor values
    document.getElementById("raw-value").textContent = data.raw;
    document.getElementById("voltage-value").textContent = data.voltage;
    document.getElementById("timestamp").textContent = new Date(
      data.timestamp * 1000,
    ).toLocaleTimeString();
  }

  updatePlot(plotData) {
    if (plotData) {
      document.getElementById("plot").src = "data:image/png;base64," + plotData;
    }
  }

  async downloadHistoricalPlot() {
    const timeRange = this.getTimeRange();
    if (!timeRange) return;

    window.location.href = `/api/historical?start=${timeRange.start}&end=${timeRange.end}&format=plot&download=true`;
  }

  async downloadData() {
    const timeRange = this.getTimeRange();
    if (!timeRange) return;

    const response = await fetch(
      `/api/historical?start=${timeRange.start}&end=${timeRange.end}`,
    );
    const data = await response.json();

    this.downloadJson(
      data,
      `moisture_data_${timeRange.start}_${timeRange.end}.json`,
    );
  }

  getTimeRange() {
    const start =
      new Date(document.getElementById("start-date").value).getTime() / 1000;
    const end =
      new Date(document.getElementById("end-date").value).getTime() / 1000;

    if (isNaN(start) || isNaN(end)) {
      alert("Please select valid date range");
      return null;
    }

    return { start, end };
  }

  downloadJson(data, filename) {
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: "application/json",
    });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
  }
}

// Initialize on page load
window.moistureMonitor = new MoistureMonitor();
