from controllers import Controllers

class HukumController(Controllers):
    def __init__(self, *args, **kwargs):
        super(HukumController, self).__init__(*args, **kwargs)

        self._url = "https://bdsp2.pertanian.go.id/siperditan/nav_hukum.php"
        self.tags = [
            "bdsp2.pertanian.go.id",
            "Hukum",
            "siperditan",
        ]
        self.source = "siperditan"