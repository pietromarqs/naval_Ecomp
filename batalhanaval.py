import tkinter as tk
from tkinter import messagebox
from matrix import Matrix, Edit_matrix, Navios

class BatalhaNaval:
    def __init__(self, root):
        self.root = root
        self.root.title("Batalha Naval")
        self.root.configure(bg="#1e1e2f")

        self.jogador_atual = 1
        self.orientacao = "direita"
        self.navio_selecionado = None
        self.navios_restantes = {
            1: {"Encouraçado": 2, "Destroyer": 2, "Submarino": 2},
            2: {"Encouraçado": 2, "Destroyer": 2, "Submarino": 2}
        }

        self.tabuleiros = {1: Matrix(), 2: Matrix()}
        self.editors = {1: Edit_matrix(self.tabuleiros[1]), 2: Edit_matrix(self.tabuleiros[2])}
        self.botoes = {1: {}, 2: {}}
        self.navios_destruidos = {1: 0, 2: 0}

        self.criar_interface()

    # ------------------------------------------------------
    # INTERFACE
    # ------------------------------------------------------
    def criar_interface(self):
        frame_top = tk.Frame(self.root, bg="#1e1e2f")
        frame_top.pack(pady=10, padx=30)

        separator = tk.Label(frame_top, text="", width=10, bg="#1e1e2f")
        separator.grid(row=0, column=11, rowspan=12)

        tk.Label(frame_top, text="Jogador 1", fg="white", bg="#1e1e2f", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=11)
        tk.Label(frame_top, text="Jogador 2", fg="white", bg="#1e1e2f", font=("Arial", 14, "bold")).grid(row=0, column=12, columnspan=11)

        for j in range(10):
            tk.Label(frame_top, text=str(j + 1), fg="white", bg="#1e1e2f").grid(row=1, column=j + 1)
            tk.Label(frame_top, text=str(j + 1), fg="white", bg="#1e1e2f").grid(row=1, column=j + 13)

        letras = list(self.tabuleiros[1].matriz.keys())
        for i, letra in enumerate(letras):
            tk.Label(frame_top, text=letra, fg="white", bg="#1e1e2f").grid(row=i + 2, column=0)
            tk.Label(frame_top, text=letra, fg="white", bg="#1e1e2f").grid(row=i + 2, column=12)

            for j in range(10):
                b1 = tk.Button(frame_top, width=2, height=1, bg="#29304a",
                               command=lambda l=letra, c=j: self.posicionar_navio(1, l, c))
                b1.grid(row=i + 2, column=j + 1)
                self.botoes[1][(letra, j)] = b1

                b2 = tk.Button(frame_top, width=2, height=1, bg="#29304a",
                               command=lambda l=letra, c=j: self.posicionar_navio(2, l, c))
                b2.grid(row=i + 2, column=j + 13)
                self.botoes[2][(letra, j)] = b2

        frame_controls = tk.Frame(self.root, bg="#1e1e2f")
        frame_controls.pack(pady=10)

        self.info_label = tk.Label(frame_controls, text="Jogador 1: Posicione seus navios",
                                   fg="white", bg="#1e1e2f", font=("Arial", 12))
        self.info_label.grid(row=0, column=0, columnspan=4)

        tk.Button(frame_controls, text="Encouraçado (3)", command=lambda: self.selecionar_navio("Encouraçado")).grid(row=1, column=0, padx=5)
        tk.Button(frame_controls, text="Destroyer (2)", command=lambda: self.selecionar_navio("Destroyer")).grid(row=1, column=1, padx=5)
        tk.Button(frame_controls, text="Submarino (1)", command=lambda: self.selecionar_navio("Submarino")).grid(row=1, column=2, padx=5)

        self.orientacao_btn = tk.Button(frame_controls, text="Direita →", command=self.trocar_orientacao)
        self.orientacao_btn.grid(row=1, column=3, padx=5)

    # ------------------------------------------------------
    # POSICIONAMENTO DE NAVIOS
    # ------------------------------------------------------
    def selecionar_navio(self, tipo):
        self.navio_selecionado = tipo
        self.info_label.config(text=f"{'Jogador 1' if self.jogador_atual == 1 else 'Jogador 2'}: Coloque o {tipo}")

    def trocar_orientacao(self):
        self.orientacao = "baixo" if self.orientacao == "direita" else "direita"
        self.orientacao_btn.config(text="Baixo ↓" if self.orientacao == "baixo" else "Direita →")

    def posicionar_navio(self, jogador, linha, coluna):
        if jogador != self.jogador_atual or not self.navio_selecionado:
            return

        if self.navios_restantes[jogador][self.navio_selecionado] == 0:
            messagebox.showinfo("Limite atingido", f"Você já colocou todos os {self.navio_selecionado}s.")
            return

        tamanho = Navios[self.navio_selecionado]
        posicoes = []

        for i in range(tamanho):
            if self.orientacao == "direita":
                nova_col = coluna + i
                if nova_col >= 10:
                    messagebox.showerror("Erro", "Navio fora do limite horizontal!")
                    return
                posicoes.append((linha, nova_col))
            else:
                nova_linha = chr(ord(linha) + i)
                if nova_linha not in self.tabuleiros[jogador].matriz:
                    messagebox.showerror("Erro", "Navio fora do limite vertical!")
                    return
                posicoes.append((nova_linha, coluna))

        try:
            self.editors[jogador].border_box(posicoes, 1)
            self.navios_restantes[jogador][self.navio_selecionado] -= 1
            for (l, c) in posicoes:
                self.botoes[jogador][(l, c)].config(bg="#3498db")
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
            return

        if all(v == 0 for v in self.navios_restantes[jogador].values()):
            if self.jogador_atual == 1:
                self.jogador_atual = 2
                self.info_label.config(text="Jogador 2: Posicione seus navios")
            else:
                self.iniciar_batalha()

    # ------------------------------------------------------
    # BATALHA
    # ------------------------------------------------------
    def iniciar_batalha(self):
        for j in [1, 2]:
            for (l, c), b in self.botoes[j].items():
                if self.tabuleiros[j].matriz[l][c] == 1:
                    b.config(bg="#29304a")
                if j == 1:
                    b.config(command=lambda linha=l, col=c: self.realizar_tiro(2, linha, col))
                else:
                    b.config(command=lambda linha=l, col=c: self.realizar_tiro(1, linha, col))

        self.jogador_atual = 1
        self.info_label.config(text="Batalha iniciada! Jogador 1 começa!")

    def realizar_tiro(self, jogador, linha, coluna):
        oponente = 2 if jogador == 1 else 1
        if jogador != self.jogador_atual:
            return

        resultado = self.editors[oponente].atirar(linha, coluna + 1)
        botao_alvo = self.botoes[oponente][(linha, coluna)]

        if resultado == "erro":
            botao_alvo.config(bg="#ff4d4d")
            self.jogador_atual = oponente
            self.info_label.config(text=f"Errou! Agora é a vez do Jogador {oponente}.")
        elif resultado == "acerto":
            botao_alvo.config(bg="#2ecc71")

            if self.navio_afundado(oponente, linha, coluna):
                self.marcar_navio_afundado(oponente, linha, coluna)
                self.navios_destruidos[jogador] += 1
                self.info_label.config(text=f"Jogador {jogador} afundou um navio!")

                if self.verificar_vitoria(jogador):
                    messagebox.showinfo("🏆 Vitória!", f"Jogador {jogador} venceu a batalha!")
                    self.desativar_tabuleiros()
                    return
            else:
                self.info_label.config(text=f"Jogador {jogador} acertou! Jogue novamente!")
                return
        elif resultado == "repetido":
            messagebox.showinfo("Aviso", "Você já atirou aqui.")
            return
        else:
            messagebox.showerror("Erro", "Tiro inválido.")

        self.info_label.config(text=f"Vez do Jogador {self.jogador_atual}.")

    # ------------------------------------------------------
    # LÓGICA DE AFUNDAMENTO E VITÓRIA
    # ------------------------------------------------------
    def verificar_vitoria(self, jogador):
        total_navios = sum(len(Navios) * 2 for _ in range(1))  # 6 navios no total
        if self.navios_destruidos[jogador] == total_navios:
            oponente = 2 if jogador == 1 else 1
            for (l, c), botao in self.botoes[oponente].items():
                if self.tabuleiros[oponente].matriz[l][c] == 1:
                    botao.config(bg="#dbd834")  # marca navios não atingidos
            return True
        return False

    def desativar_tabuleiros(self):
        for j in [1, 2]:
            for b in self.botoes[j].values():
                b.config(state="disabled")

    def navio_afundado(self, oponente, linha, coluna):
        partes = self.collect_ship_parts(oponente, linha, coluna)
        if not partes:
            return False
        for (l, c) in partes:
            if self.tabuleiros[oponente].matriz[l][c] == 1:
                return False
        return True

    def collect_ship_parts(self, oponente, linha, coluna):
        matriz = self.tabuleiros[oponente].matriz
        if linha not in matriz:
            return []

        visit, partes = set(), []
        stack = [(linha, coluna)]
        while stack:
            l, c = stack.pop()
            if (l, c) in visit:
                continue
            visit.add((l, c))
            partes.append((l, c))
            for dl, dc in [(0,1),(1,0),(-1,0),(0,-1)]:
                nl, nc = chr(ord(l) + dl), c + dc
                if nl in matriz and 0 <= nc < 10:
                    if matriz[nl][nc] in (1, 'V') and (nl, nc) not in visit:
                        stack.append((nl, nc))
        return partes

    def marcar_navio_afundado(self, oponente, linha, coluna):
        partes = self.collect_ship_parts(oponente, linha, coluna)
        if not partes:
            return

        for (l, c) in partes:
            self.botoes[oponente][(l, c)].config(bg="#1f4d7a")

        matriz = self.tabuleiros[oponente].matriz
        for (l, c) in partes:
            for dl in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    nl, nc = chr(ord(l) + dl), c + dc
                    if nl in matriz and 0 <= nc < 10:
                        if matriz[nl][nc] == 0:
                            matriz[nl][nc] = 'X'
                            self.botoes[oponente][(nl, nc)].config(bg="#ff4d4d")

if __name__ == "__main__":
    root = tk.Tk()
    BatalhaNaval(root)
    root.mainloop()
