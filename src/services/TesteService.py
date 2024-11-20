from models.Teste import Teste

class TesteService():
    def __init__(self):
        pass

    def ola_mundo(self) -> Teste:
        return Teste(descricao='ola mundo')