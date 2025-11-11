import tkinter as tk
from tkinter import messagebox
from matriz import Matrix, Edit_matrix, Navios
import threading
import clientTCP

class MenuPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("Batalha Naval - Menu Principal")
        self.tela_inicial()

    def limpar(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def tela_inicial(self):
        self.limpar()
        tk.Label(self.root, text="Batalha Naval", font=("Arial", 20)).pack(pady=24)

        tk.Button(self.root, text="Multiplayer local", width=25, height=2,
                  command=self.iniciar_local).pack(pady=10)
        tk.Button(self.root, text="Multiplayer online", width=25, height=2,
                  command=self.menu_online).pack(pady=10)

    def iniciar_local(self):
        self.limpar()
        # Crie o jogo local normalmente
        BatalhaNaval(self.root)

    def menu_online(self):
        self.limpar()
        tk.Label(self.root, text="Multiplayer online", font=("Arial", 16)).pack(pady=18)
        tk.Button(self.root, text="Entrar em jogo existente", width=25, height=2,
                  command=self.listar_salas).pack(pady=10)
        tk.Button(self.root, text="Criar sala", width=25, height=2,
                  command=self.criar_sala).pack(pady=10)
        tk.Button(self.root, text="Voltar", width=15,
                  command=self.tela_inicial).pack(pady=15)

    def listar_salas(self):
        self.limpar()
        tk.Label(self.root, text="Salas disponíveis:", font=("Arial", 14)).pack(pady=14)
        tk.Label(self.root, text="Conectando ao servidor...", fg="gray", font=("Arial", 10)).pack(pady=10)
        
        # Conectar ao servidor em thread separada e depois listar
        thread = threading.Thread(target=self.conectar_e_listar_salas, daemon=True)
        thread.start()
        
        tk.Button(self.root, text="Voltar", width=15,
                  command=self.voltar_e_desconectar).pack(pady=15)
    
    def conectar_e_listar_salas(self):
        """Conecta ao servidor e lista salas."""
        try:
            # SEMPRE cria nova conexão se não existir
            if clientTCP.client is None:
                print("[MENU] Criando nova conexão com servidor...")
                clientTCP.main(start_send_thread=False, start_receive_thread=True)
                print("[MENU] Conexão estabelecida com sucesso")
            
            # registrar callback para quando a sala iniciar
            clientTCP.on_sala_iniciada = self._on_sala_iniciada
            # Requisita a lista de salas (chamada síncrona com timeout interno)
            clientTCP.listar_salas_servidor()
            # Atualiza a UI no thread principal
            self.root.after(0, self.atualizar_salas)
        except Exception as e:
            print(f"Erro ao conectar: {e}")
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Não foi possível conectar ao servidor: {e}"))
    
    def atualizar_salas(self):
        """Atualiza a lista de salas disponíveis e cria botões dinamicamente."""
        try:
            salas = clientTCP.listar_salas_servidor()
            print(f"[DEBUG] Salas recebidas: {salas}")
            
            # Limpar labels anteriores (exceto o title e o Voltar)
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.Button) and "Voltar" not in widget.cget("text"):
                    widget.destroy()
                elif isinstance(widget, tk.Label) and "Conectando" in widget.cget("text"):
                    widget.destroy()
            
            if salas and len(salas) > 0:
                print(f"[DEBUG] Criando {len(salas)} botões de sala")
                for sala_info in salas:
                    try:
                        sala_id, criador = sala_info.split('|')
                        tk.Button(self.root, text=f"Sala de {criador} (ID: {sala_id})", 
                                  width=30, height=1,
                                  command=lambda sid=sala_id: self.entrar_na_sala(sid)).pack(pady=5)
                    except ValueError as e:
                        print(f"Erro ao processar sala: {sala_info} - {e}")
                        pass
            else:
                tk.Label(self.root, text="Nenhuma sala disponível", fg="gray").pack(pady=10)
        except Exception as e:
            print(f"Erro ao atualizar salas: {e}")
            import traceback
            traceback.print_exc()
            tk.Label(self.root, text=f"Erro: {e}", fg="red").pack(pady=10)

    def entrar_na_sala(self, sala_id):
        # Tenta entrar na sala sem bloquear a UI
        self.limpar()
        tk.Label(self.root, text=f"Entrando na sala {sala_id}...", font=("Arial", 16)).pack(pady=60)
        tk.Button(self.root, text="Voltar", width=15,
                  command=self.voltar_e_desconectar).pack(pady=15)

        def _join():
            try:
                # A conexão e callback já foram configurados em conectar_e_listar_salas
                ok = clientTCP.entrar_sala_no_servidor(sala_id)
                if not ok:
                    self.root.after(0, lambda: messagebox.showerror("Erro", "Falha ao entrar na sala"))
                    # voltar ao menu online
                    self.root.after(0, self.menu_online)
            except Exception as e:
                print(f"Erro ao entrar na sala: {e}")
                self.root.after(0, lambda: messagebox.showerror("Erro", str(e)))

        threading.Thread(target=_join, daemon=True).start()


    def criar_sala(self):
        self.limpar()
        tk.Label(self.root, text="Criando sala...", font=("Arial", 16)).pack(pady=60)
        tk.Button(self.root, text="Cancelar", width=15,
                  command=self.voltar_e_desconectar).pack(pady=15)
        # Conectar em uma thread separada para não bloquear a UI
        thread = threading.Thread(target=self.conectar_e_criar_sala, daemon=True)
        thread.start()
    
    def conectar_e_criar_sala(self):
        """Conecta ao servidor e cria uma sala."""
        try:
            # SEMPRE cria nova conexão se não existir (após disconnect, client será None)
            if clientTCP.client is None:
                print("[MENU] Criando nova conexão com servidor...")
                clientTCP.main(start_send_thread=False, start_receive_thread=True)
                print("[MENU] Conexão estabelecida com sucesso")
            
            # registrar callback para quando a sala iniciar
            clientTCP.on_sala_iniciada = self._on_sala_iniciada
            print("[MENU] Criando sala no servidor...")
            
            # Cria sala de forma síncrona (usa timeout interno)
            resultado = clientTCP.criar_sala_no_servidor()
            print(f"[MENU] Sala criada: {resultado}")
            
            # Atualiza a label na thread principal
            self.root.after(0, lambda: self.atualizar_label_criada())
        except Exception as e:
            print(f"[ERRO] Erro ao criar sala: {e}")
            import traceback
            traceback.print_exc()
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro ao criar sala: {e}"))

    def _on_sala_iniciada(self, sala_id, role):
        """Callback chamado quando o servidor notifica que a sala iniciou.
        Troca para a aba/jogo (usuário implementará a aba personalizada)."""
        try:
            # aqui trocamos a UI para a tela do jogo multiplayer online
            self.limpar()
            # instanciar o jogo multiplayer com uma única matriz
            BatalhaNavalMultiplayer(self.root)
        except Exception as e:
            print(f"Erro ao abrir jogo: {e}")
    
    def atualizar_label_criada(self):
        """Atualiza a label mostrando que a sala foi criada."""
        try:
            sala_id = clientTCP.sala_criada
            if sala_id:
                for widget in self.root.winfo_children():
                    if isinstance(widget, tk.Label):
                        widget.destroy()
                tk.Label(self.root, text=f"Sala criada! ID: {sala_id}", font=("Arial", 16)).pack(pady=20)
                tk.Label(self.root, text="Esperando outro jogador...", font=("Arial", 12), fg="gray").pack(pady=10)
                tk.Button(self.root, text="Cancelar", width=15,
                          command=self.voltar_e_desconectar).pack(pady=15)
            else:
                messagebox.showerror("Erro", "Falha ao criar sala")
                self.menu_online()
        except Exception as e:
            print(f"Erro ao atualizar label: {e}")


    def voltar_e_desconectar(self):
        # Desconecta do servidor (se conectado) e volta ao menu
        try:
            clientTCP.disconnect()
        except Exception:
            pass
        self.menu_online()

class BatalhaNavalMultiplayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Batalha Naval - Multiplayer")
        self.root.configure(bg="#1e1e2f")

        # estado do jogo local (uma única matriz compartilhada pela interface)
        self.orientacao = "direita"
        self.navio_selecionado = None
        self.navios_restantes = {"Encouraçado": 2, "Destroyer": 2, "Submarino": 2}
        self.batalha_iniciada = False  # flag para saber se a batalha já começou
        self.minha_vez = False  # flag para saber se é a vez do jogador
        # total de células com navios: Encouraçado(3) x 2 + Destroyer(2) x 2 + Submarino(1) x 2 = 6+4+2 = 12
        self.total_pecas_navios = 12
        self.pecas_atingidas = 0  # contador de peças de navios atingidas
        self.meus_tiros = {}  # guarda os tiros que eu dei: {(linha, coluna): "acerto" ou "erro"}

        # matriz local que representa nosso tabuleiro (0 vazio, 1 navio, 'X' marcado)
        self.tabuleiro = Matrix()
        self.editor = Edit_matrix(self.tabuleiro)
        self.botoes = {}

        # callbacks de rede (defina por quem usar a tela online)
        # deve ser func(linha, coluna) -> None que envia o movimento ao servidor
        self.on_send_move = None

        # registrar callback para quando a batalha iniciar no servidor
        clientTCP.on_batalha_iniciar = self._on_batalha_iniciar_servidor
        clientTCP.on_receber_tiro = self._on_receber_tiro
        clientTCP.on_resultado_tiro = self._on_resultado_tiro
        clientTCP.on_sua_vez = self._on_sua_vez
        clientTCP.on_vez_oponente = self._on_vez_oponente
        clientTCP.on_vitoria = self._on_vitoria
        clientTCP.on_derrota = self._on_derrota

        # cria interface
        self.criar_interface()

    def criar_interface(self):
        frame_top = tk.Frame(self.root, bg="#1e1e2f")
        frame_top.pack(pady=10, padx=30)

        tk.Label(frame_top, text="Batalha Naval - Multiplayer", fg="white", bg="#1e1e2f", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=12)

        for j in range(10):
            tk.Label(frame_top, text=str(j + 1), fg="white", bg="#1e1e2f").grid(row=1, column=j + 1)

        letras = list(self.tabuleiro.matriz.keys())
        for i, letra in enumerate(letras):
            tk.Label(frame_top, text=letra, fg="white", bg="#1e1e2f").grid(row=i + 2, column=0)
            for j in range(10):
                b = tk.Button(frame_top, width=2, height=1, bg="#29304a",
                              command=lambda l=letra, c=j: self.botao_clicado(l, c))
                b.grid(row=i + 2, column=j + 1)
                self.botoes[(letra, j)] = b

        frame_controls = tk.Frame(self.root, bg="#1e1e2f")
        frame_controls.pack(pady=10)

        self.info_label = tk.Label(frame_controls, text="Posicione seus navios", fg="white", bg="#1e1e2f", font=("Arial", 12))
        self.info_label.grid(row=0, column=0, columnspan=4)

        tk.Button(frame_controls, text="Encouraçado (3)", command=lambda: self.selecionar_navio("Encouraçado")).grid(row=1, column=0, padx=5)
        tk.Button(frame_controls, text="Destroyer (2)", command=lambda: self.selecionar_navio("Destroyer")).grid(row=1, column=1, padx=5)
        tk.Button(frame_controls, text="Submarino (1)", command=lambda: self.selecionar_navio("Submarino")).grid(row=1, column=2, padx=5)

        self.orientacao_btn = tk.Button(frame_controls, text="Direita →", command=self.trocar_orientacao)
        self.orientacao_btn.grid(row=1, column=3, padx=5)

        # botão para finalizar posicionamento e começar a batalha
        tk.Button(self.root, text="Iniciar batalha", command=self.iniciar_batalha, width=20).pack(pady=8)

    def selecionar_navio(self, tipo):
        self.navio_selecionado = tipo
        self.info_label.config(text=f"Coloque o {tipo}")

    def trocar_orientacao(self):
        self.orientacao = "baixo" if self.orientacao == "direita" else "direita"
        self.orientacao_btn.config(text="Baixo ↓" if self.orientacao == "baixo" else "Direita →")

    def botao_clicado(self, linha, coluna):
        # duas fases: posicionamento (ainda tem navios) e batalha
        if any(v > 0 for v in self.navios_restantes.values()):
            self.posicionar_navio(linha, coluna)
        else:
            # durante a batalha, clicar envia tiro
            self.realizar_tiro(linha, coluna)

    def posicionar_navio(self, linha, coluna):
        if not self.navio_selecionado:
            messagebox.showinfo("Selecione um navio", "Escolha um navio antes de posicionar")
            return

        if self.navios_restantes[self.navio_selecionado] == 0:
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
                if nova_linha not in self.tabuleiro.matriz:
                    messagebox.showerror("Erro", "Navio fora do limite vertical!")
                    return
                posicoes.append((nova_linha, coluna))

        try:
            self.editor.border_box(posicoes, 1)
            self.navios_restantes[self.navio_selecionado] -= 1
            for (l, c) in posicoes:
                self.botoes[(l, c)].config(bg="#3498db")
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
            return

        if all(v == 0 for v in self.navios_restantes.values()):
            self.info_label.config(text="Posicionamento concluído. Aguarde o outro jogador.")

    def iniciar_batalha(self):
        # verifica se todos os navios foram posicionados
        if any(v > 0 for v in self.navios_restantes.values()):
            messagebox.showwarning("Aviso", "Posicione todos os navios antes de iniciar!")
            return
        
        # envia ao servidor que está pronto
        clientTCP.enviar_pronto()
        self.info_label.config(text="Aguardando o outro jogador ficar pronto...")
    
    def _on_batalha_iniciar_servidor(self, sala_id):
        """Callback chamado quando o servidor notifica que ambos estão prontos."""
        try:
            def _iniciar():
                # oculta os navios posicionados (volta cor padrão)
                for (l, c), botao in self.botoes.items():
                    if self.tabuleiro.matriz[l][c] == 1:
                        botao.config(bg="#29304a")  # volta para cor padrão
                
                self.batalha_iniciada = True
                # muda status para permitir tiros — os botões agora enviarão disparos
                self.info_label.config(text="Batalha iniciada! Aguarde sua vez...", fg="white")
                print("[DEBUG] Batalha iniciada na UI")
            
            self.root.after(0, _iniciar)
        except Exception as e:
            print(f"Erro ao iniciar batalha: {e}")
    
    def _on_sua_vez(self):
        """Callback quando é a vez do jogador."""
        try:
            self.minha_vez = True
            self.root.after(0, lambda: self.info_label.config(text="SUA VEZ! Clique para atirar.", fg="#2ecc71"))
            print("[DEBUG] Agora é minha vez")
        except Exception as e:
            print(f"Erro em _on_sua_vez: {e}")
    
    def _on_vez_oponente(self):
        """Callback quando é a vez do oponente."""
        try:
            self.minha_vez = False
            self.root.after(0, lambda: self.info_label.config(text="Aguarde a vez do oponente...", fg="#e74c3c"))
            print("[DEBUG] Agora é a vez do oponente")
        except Exception as e:
            print(f"Erro em _on_vez_oponente: {e}")
    
    def _on_receber_tiro(self, linha, coluna):
        """Callback quando recebe um tiro do oponente."""
        try:
            def _processar():
                # processa o tiro no tabuleiro local (internamente)
                resultado = self.editor.atirar(linha, coluna + 1)
                
                # NÃO marca visualmente na sua matriz (que é de ataque)
                # Apenas processa internamente e envia resultado
                
                if resultado == "erro":
                    clientTCP.enviar_resultado_tiro("erro")
                elif resultado == "acerto":
                    self.pecas_atingidas += 1
                    print(f"[DEBUG] Pecas atingidas: {self.pecas_atingidas}/{self.total_pecas_navios}")
                    
                    # verifica se perdeu (todos navios afundados)
                    if self.pecas_atingidas >= self.total_pecas_navios:
                        clientTCP.enviar_resultado_tiro("vitoria")  # oponente venceu
                        print("[DEBUG] Todos navios destruidos! Enviando vitoria para oponente")
                    else:
                        clientTCP.enviar_resultado_tiro("acerto")
                elif resultado == "repetido":
                    clientTCP.enviar_resultado_tiro("erro")
                
                print(f"[DEBUG] Tiro recebido em {linha}{coluna}: {resultado}")
            
            self.root.after(0, _processar)
        except Exception as e:
            print(f"Erro ao processar tiro recebido: {e}")
    
    def _on_resultado_tiro(self, resultado):
        """Callback com o resultado do tiro que você deu."""
        try:
            def _atualizar():
                # encontra o último tiro que você deu (aguardando)
                posicao_tiro = None
                for pos, status in self.meus_tiros.items():
                    if status == "aguardando":
                        posicao_tiro = pos
                        break
                
                if posicao_tiro:
                    linha, coluna = posicao_tiro
                    btn = self.botoes.get((linha, coluna))
                    
                    if resultado == "acerto" or resultado == "vitoria":
                        # Marca em VERDE na SUA matriz (você acertou o oponente)
                        if btn:
                            btn.config(bg="#2ecc71")
                        self.meus_tiros[posicao_tiro] = "acerto"
                        self.info_label.config(text=f"ACERTOU em {linha}{coluna}! Jogue novamente!", fg="#2ecc71")
                        
                        if resultado == "vitoria":
                            self.info_label.config(text="VITORIA! Você afundou todos os navios!", fg="#2ecc71")
                    elif resultado == "erro":
                        # Marca em VERMELHO na SUA matriz (você errou)
                        if btn:
                            btn.config(bg="#ff4d4d")
                        self.meus_tiros[posicao_tiro] = "erro"
                        self.info_label.config(text=f"ERROU em {linha}{coluna}! Vez do oponente.", fg="#e74c3c")
                
                print(f"[DEBUG] Resultado do tiro que você deu: {resultado}")
            
            self.root.after(0, _atualizar)
        except Exception as e:
            print(f"Erro ao processar resultado: {e}")
    
    def _on_vitoria(self):
        """Callback quando você vence."""
        def _mostrar_vitoria():
            self.batalha_iniciada = False
            # limpa a tela
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # tela de vitória
            tk.Label(self.root, text="VITORIA!", font=("Arial", 32, "bold"), fg="#2ecc71", bg="#1e1e2f").pack(pady=50)
            tk.Label(self.root, text="Você afundou todos os navios do oponente!", font=("Arial", 14), fg="white", bg="#1e1e2f").pack(pady=20)
            tk.Button(self.root, text="Voltar ao Menu", width=20, height=2, command=self.voltar_menu).pack(pady=20)
        
        self.root.after(0, _mostrar_vitoria)
    
    def _on_derrota(self):
        """Callback quando você perde."""
        def _mostrar_derrota():
            self.batalha_iniciada = False
            # limpa a tela
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # tela de derrota
            tk.Label(self.root, text="DERROTA!", font=("Arial", 32, "bold"), fg="#e74c3c", bg="#1e1e2f").pack(pady=50)
            tk.Label(self.root, text="Todos os seus navios foram afundados!", font=("Arial", 14), fg="white", bg="#1e1e2f").pack(pady=20)
            tk.Button(self.root, text="Voltar ao Menu", width=20, height=2, command=self.voltar_menu).pack(pady=20)
        
        self.root.after(0, _mostrar_derrota)
    
    def voltar_menu(self):
        """Volta ao menu principal."""
        try:
            clientTCP.disconnect()
        except Exception:
            pass
        # limpa a tela e volta ao menu
        for widget in self.root.winfo_children():
            widget.destroy()
        # importa MenuPrincipal aqui para evitar imports circulares
        menu = MenuPrincipal(self.root)
        menu.tela_inicial()

    def realizar_tiro(self, linha, coluna):
        # verifica se a batalha já começou
        if not self.batalha_iniciada:
            messagebox.showwarning("Aviso", "Aguarde a batalha iniciar!")
            return
        
        # VERIFICA SE É A VEZ DO JOGADOR (ANTES DE FAZER QUALQUER COISA)
        if not self.minha_vez:
            # Não faz nada se não for sua vez - nem mostra aviso para não ficar chato
            return
        
        # verifica se já atirou nesta posição
        if (linha, coluna) in self.meus_tiros:
            messagebox.showinfo("Aviso", "Você já atirou nesta posição!")
            return
        
        # Desativa a flag de vez IMEDIATAMENTE para evitar duplo clique
        self.minha_vez = False
        self.info_label.config(text="Tiro enviado! Aguardando resposta...", fg="#f39c12")
        
        # marca temporariamente em amarelo até receber resposta
        btn = self.botoes.get((linha, coluna))
        if btn:
            btn.config(bg="#f1c40f")
        
        # salva que atirou aqui (ainda sem resultado)
        self.meus_tiros[(linha, coluna)] = "aguardando"
        
        # envia o tiro
        clientTCP.enviar_tiro(linha, coluna)
        print(f"[DEBUG] Tiro enviado para {linha}{coluna}")

    def receber_tiro_oponente(self, linha, coluna):
        # chamado quando chegarem dados do servidor informando que o oponente atirou
        # atualiza o tabuleiro local e a UI
        resultado = self.editor.atirar(linha, coluna + 1)
        btn = self.botoes.get((linha, coluna))
        if resultado == "erro":
            if btn:
                btn.config(bg="#ff4d4d")
        elif resultado == "acerto":
            if btn:
                btn.config(bg="#2ecc71")
        elif resultado == "repetido":
            if btn:
                btn.config(bg="#95a5a6")
        return resultado

    def set_send_callback(self, func):
        """Define a função que será chamada para enviar um movimento ao servidor.
        Assinatura: func(linha, coluna)
        """
        self.on_send_move = func





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
    app = MenuPrincipal(root)
    root.mainloop()
