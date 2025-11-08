class Matrix:
    matriz = {
        "A": [],
        "B": [],
        "C": [],
        "D": [],
        "E": [],
        "F": [],
        "G": [],
        "H": [],
        "I": [],
        "J": []
    }


class Edit_matrix:
    def __init__(self,
                 est_matrix,
                 limite_colunas,
                 ):
        
        self.est_matrix = Matrix # Aqui eu estancio meu dicionário
        self.limite_colunas = 10
    
    def ad_coordenada(self, linha, coluna, tipo_alocacao):
        try:
            if linha in self.est_matrix:
                if coluna < self.limite_colunas:
                    self.est_matrix[linha] [coluna] = tipo_alocacao
                else:
                    raise ValueError("valor fora dos inicies das colunas")
            else:
                raise ValueError("linha nao existente")
            
        except ValueError as e:
            print(f"arro {e}")
            
    def border_box(self, tuplas, tipo_alocacao):
        try:
            def verifica_ocupacao(linha, coluna):
                if len(self.est_matrix[linha]) > coluna and self.est_matrix[linha][coluna] is not None:
                    return False

                vizinhos = [
                    (linha, coluna - 1),  # Esquerda
                    (linha, coluna + 1),  # Direita
                    (chr(ord(linha) - 1), coluna),  # Acima
                    (chr(ord(linha) + 1), coluna),  # Abaixo
                    (chr(ord(linha) - 1), coluna - 1),  # Diagonal superior esquerda
                    (chr(ord(linha) - 1), coluna + 1),  # Diagonal superior direita
                    (chr(ord(linha) + 1), coluna - 1),  # Diagonal inferior esquerda
                    (chr(ord(linha) + 1), coluna + 1),  # Diagonal inferior direita
                ]
                for n_linha, n_coluna in vizinhos:
                    if n_linha in self.est_matrix and 0 <= n_coluna < self.limite_colunas:
                        if len(self.est_matrix[n_linha]) > n_coluna and self.est_matrix[n_linha][n_coluna] is not None:
                            return False
                return True   
            
            # Verifica se todas as posições na lista de tuplas são válidas
            for linha, coluna in tuplas:
                if not verifica_ocupacao(linha, coluna):
                    raise ValueError(f"Posição ({linha}, {coluna}) está ocupada ou colada a outro navio.")
            
            # Aloca o navio chamando ad_coordenada para cada posição
            for linha, coluna in tuplas:
                self.ad_coordenada(linha, coluna, tipo_alocacao)

        except ValueError as e:
            print(f"Erro: {e}")
    
    def explosao(self, linha, coluna):
        try:
            if linha in self.est_matrix:
                if coluna < self.limite_colunas:
                    if()
                else:
                    raise ValueError("valor fora dos inicies das colunas")
            else:
                raise ValueError("linha nao existente")
            
        except ValueError as e:
            print(f"arro {e}")
        
        


   