class WeatherData:
    def __init__(self, temp, feels_like, temp_min, temp_max, pressure, humidity):
        self.temp = temp
        self.feels_like = feels_like
        self.temp_min = temp_min
        self.temp_max = temp_max
        self.pressure = pressure
        self.humidity = humidity

    @classmethod
    def from_dict(cls, data):
        return cls(
            temp=data.get("temp"),
            feels_like=data.get("feels_like"),
            temp_min=data.get("temp_min"),
            temp_max=data.get("temp_max"),
            pressure=data.get("pressure"),
            humidity=data.get("humidity")
        )

    def __str__(self):
        return (f"Temp: {self.temp}°C, Feels Like: {self.feels_like}°C, "
                f"Min: {self.temp_min}°C, Max: {self.temp_max}°C, "
                f"Pressure: {self.pressure} hPa, Humidity: {self.humidity}%")
