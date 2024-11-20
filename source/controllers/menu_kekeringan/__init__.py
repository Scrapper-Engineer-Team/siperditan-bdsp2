from controllers import Controllers

class KekeringanController(Controllers):
    def __init__(self, *args, **kwargs):
        super(KekeringanController, self).__init__(*args, **kwargs)

        self._url = "https://bdsp2.pertanian.go.id/siperditan/menu_kekeringan.php"