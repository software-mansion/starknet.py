from src.net import Client


class TestClient(Client):
    def __init__(self, *args, **kwargs):
        super().__init__("http://localhost:5000", *args, **kwargs)
