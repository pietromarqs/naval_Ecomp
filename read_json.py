import json

# Leitura do json
class Read_json:
    def __init__(self, player, acao, tipo_navio, coordenadas):
        self.tipo_navio  = tipo_navio
        self.coordenadas = coordenadas
        self.acao        = acao
        self.player      = player

    def read_json(self, file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
            self.player      = data.get("player")
            self.acao        = data.get("acao")
            self.tipo_navio  = data.get("tipo_navio")
            self.coordenadas = data.get("coordenadas")
        return self

    def get_player(self):
        return self.player

    def get_acao(self):
        return self.acao

    def get_tipo_navio(self):
        return self.tipo_navio

    def get_coordenadas(self):
        return self.coordenadas
