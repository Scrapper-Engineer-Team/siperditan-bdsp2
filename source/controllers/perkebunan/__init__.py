from controllers import Controllers

class Perkebunancontroller(Controllers):
    def __init__(self, *args, **kwargs):
        super(Perkebunancontroller, self).__init__(*args, **kwargs)

        self._url = "https://bdsp2.pertanian.go.id/siperditan/menu_opt_perkebunan.php"
        self.tags = [
            "bdsp2.pertanian.go.id",
            "siperditan", 
            "perkebunan"
        ]
        self.source = "siperditan"  