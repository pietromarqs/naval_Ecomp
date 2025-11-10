Dicionario = {
    0: "água",
    1: "navio",
    'V': "acerto",
    'X': "erro"
}

Navios = {
    "Encouraçado": 3,
    "Destroyer": 2,
    "Submarino": 1
}


class Matrix:
    def __init__(self):
        # cria o tabuleiro 10x10 com letras A–J e 10 colunas (0–9)
        self.matriz = {
            "A": [0] * 10,
            "B": [0] * 10,
            "C": [0] * 10,
            "D": [0] * 10,
            "E": [0] * 10,
            "F": [0] * 10,
            "G": [0] * 10,
            "H": [0] * 10,
            "I": [0] * 10,
            "J": [0] * 10
        }

    def mostrar(self):
        """Mostra o tabuleiro no terminal (debug)"""
        print("   " + " ".join([str(i) for i in range(1, 11)]))
        for linha, valores in self.matriz.items():
            print(f"{linha}  " + " ".join(str(v) for v in valores))


class Edit_matrix:
    def __init__(self, est_matrix, limite_colunas=10):
        # aqui é est_matrix.matriz — não .matriz isolado
        self.est_matrix = est_matrix.matriz
        self.limite_colunas = limite_colunas

    def ad_coordenada(self, linha, coluna, tipo_alocacao):
        """Adiciona um valor em uma coordenada se for válida"""
        if linha not in self.est_matrix:
            raise ValueError("Linha inválida")
        if not (0 <= coluna < self.limite_colunas):
            raise ValueError("Coluna fora do limite")
        if self.est_matrix[linha][coluna] != 0:
            raise ValueError("Posição já ocupada")

        self.est_matrix[linha][coluna] = tipo_alocacao

    def border_box(self, tuplas, tipo_alocacao):
        """
        Verifica se as posições são válidas e livres,
        sem encostar em outros navios.
        """
        def verifica_ocupacao(linha, coluna):
            # posição ocupada
            if self.est_matrix[linha][coluna] != 0:
                return False

            vizinhos = [
                (linha, coluna - 1), (linha, coluna + 1),
                (chr(ord(linha) - 1), coluna), (chr(ord(linha) + 1), coluna),
                (chr(ord(linha) - 1), coluna - 1), (chr(ord(linha) - 1), coluna + 1),
                (chr(ord(linha) + 1), coluna - 1), (chr(ord(linha) + 1), coluna + 1)
            ]

            for n_linha, n_coluna in vizinhos:
                if n_linha in self.est_matrix and 0 <= n_coluna < self.limite_colunas:
                    if self.est_matrix[n_linha][n_coluna] != 0:
                        return False
            return True

        # primeiro: verifica todas as posições
        for linha, coluna in tuplas:
            if not verifica_ocupacao(linha, coluna):
                raise ValueError(f"Posição {linha}{coluna+1} inválida ou encostando em outro navio.")

        # se todas válidas, aloca
        for linha, coluna in tuplas:
            self.ad_coordenada(linha, coluna, tipo_alocacao)

    def atirar(self, linha, coluna):
        """
        Simula o tiro no tabuleiro:
        retorna 'acerto', 'erro', 'repetido' ou 'invalido'
        """
        if linha not in self.est_matrix or not (1 <= coluna <= self.limite_colunas):
            return "invalido"

        idx = coluna - 1
        valor = self.est_matrix[linha][idx]

        if valor == 0:
            self.est_matrix[linha][idx] = 'X'
            return "erro"
        elif valor == 1:
            self.est_matrix[linha][idx] = 'V'
            return "acerto"
        elif valor in ('X', 'V'):
            return "repetido"
        else:
            return "erro"
