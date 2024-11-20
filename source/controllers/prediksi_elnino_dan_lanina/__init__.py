from controllers import Controllers

class PrediksiEllaController(Controllers):
    def __init__(self, *args, **kwargs):
        super(PrediksiEllaController, self).__init__(*args, **kwargs)

        self._url = "https://bdsp2.pertanian.go.id/siperditan/menu_enso.php"
        self.source = "siperditan"