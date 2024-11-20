from controllers import Controllers

class TanamanPanganController(Controllers):
    def __init__(self, *args, **kwargs):
        super(TanamanPanganController, self).__init__(*args, **kwargs)

        self._url = "https://bdsp2.pertanian.go.id/siperditan/menu_opt_tanamanpangan.php"
        self.tag = [
            "bdsp2.pertanian.go.id",
            "siperditan",
            "tanaman pangan"
        ]
        self.source = "siperditan"