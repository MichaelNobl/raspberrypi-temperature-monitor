class RoomData:
    def __init__(self, temp, humidity):
        self.temp = temp
        self.humidity = humidity

    @classmethod
    def from_dict(cls, data):
        return cls(
            temp=data.get("temp"),
            humidity=data.get("humidity")
        )