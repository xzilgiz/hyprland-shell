from data import DataConfig

class Lang:
    def __init__(self, **kwargs):
        _params = DataConfig.getConfigBaseParams()
        self.language = _params['language']
        if self.language not in ['ru','en']:
            self.language = 'en'

        self.values = {}

    def set_text(self, language:str, key:str, value:str):
        if self.language == language:
            self.values.update({key: value})

    def get_text(self, key):
        return self.values.get(key)