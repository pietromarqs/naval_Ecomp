import socket
import threading
import uuid

HOST = '127.0.0.1'
PORT = 12345

clients = []
player_count = 0
lock = threading.Lock()
salas = {}  # dict: {sala_id: {"creator": player_name, "player1": client1, "player2": None}}

def main():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((HOST, PORT))
        server.listen()
        print("\nServer esperando conexão")
    except Exception as e:
        print('\nNão foi possível iniciar o servidor! \n', e)
        return

    while True:
        client, addr = server.accept()
        print("\nConectado")

        # Incrementa contador global para dar números únicos aos jogadores
        with lock:
            global player_count
            player_count += 1
            player_number = player_count

        # Envia número do jogador (sem limite, cada sala terá seu próprio controle)
        client.send(str(player_number).encode("utf-8"))
        
        player_name = f"Player {player_number}"
        clients.append((client, player_name))
        print(f"\n{player_name} conectado! Total de jogadores conectados: {len(clients)}")

        thread = threading.Thread(target=messagesTreatment, args=[client, player_name])
        thread.start()


def messagesTreatment(client, player_name):
    sala_id = None
    while True:
        try:
            msg_bytes = client.recv(1024)
            if not msg_bytes:
                # conexão fechada
                deleteClient(client, player_name)
                break
            try:
                msg = msg_bytes.decode('utf-8')
            except Exception:
                msg = None

            # tratar comando de criar sala
            if isinstance(msg, str) and msg.startswith('/criar_sala'):
                sala_id = criar_sala(client, player_name)
                resposta = f"SALA_CRIADA:{sala_id}".encode('utf-8')
                client.send(resposta)
                print(f"[INFO] Total de salas ativas: {len(salas)}")
                print(f"[INFO] Salas: {list(salas.keys())}")
                continue

            # tratar comando de listar salas
            if isinstance(msg, str) and msg.startswith('/listar_salas'):
                salas_lista = listar_salas_disponiveis()
                resposta = f"SALAS:{','.join(salas_lista)}".encode('utf-8')
                client.send(resposta)
                continue

            # tratar comando de entrar em sala: /entrar_sala:<id>
            if isinstance(msg, str) and msg.startswith('/entrar_sala'):
                try:
                    parts = msg.split(':', 1)
                    sala_to_join = parts[1] if len(parts) > 1 else ''
                except Exception:
                    sala_to_join = ''
                if not sala_to_join:
                    client.send(b"SALA_ENTRADA:ERROR:ID_INVALIDO")
                    continue

                # verificar existência e disponibilidade
                info = salas.get(sala_to_join)
                if not info:
                    client.send(b"SALA_ENTRADA:ERROR:NAO_ENCONTRADA")
                    continue
                if info.get('player2_client') is not None:
                    client.send(b"SALA_ENTRADA:ERROR:CHEIA")
                    continue

                # associar player2
                info['player2'] = player_name
                info['player2_client'] = client
                print(f"\n[SALA] Player {player_name} entrou na sala {sala_to_join}")
                print(f"[SALA] {sala_to_join}: {info['player1']} vs {info['player2']}")
                # envia confirmação imediata ao que entrou
                client.send(b"SALA_ENTRADA:OK")

                # notificar ambos jogadores que a sala pode iniciar
                p1_client = info.get('player1_client')
                p2_client = info.get('player2_client')
                try:
                    if p1_client:
                        p1_client.send(f"SALA_INICIAR:{sala_to_join}|player1".encode('utf-8'))
                        print(f"[SALA] Notificado {info['player1']} (player1)")
                    if p2_client:
                        p2_client.send(f"SALA_INICIAR:{sala_to_join}|player2".encode('utf-8'))
                        print(f"[SALA] Notificado {info['player2']} (player2)")
                except Exception as e:
                    print(f"[ERRO] Falha ao notificar jogadores: {e}")
                continue

            # tratar comando de jogador pronto: /pronto:<sala_id>
            if isinstance(msg, str) and msg.startswith('/pronto:'):
                try:
                    sala_pronto = msg.split(':', 1)[1]
                    info = salas.get(sala_pronto)
                    if info:
                        print(f"\n[DEBUG] Recebido /pronto de {player_name} na sala {sala_pronto}")
                        print(f"[DEBUG] Player1: {info.get('player1')}, Player2: {info.get('player2')}")
                        print(f"[DEBUG] Status: P1_pronto={info.get('player1_pronto')}, P2_pronto={info.get('player2_pronto')}")
                        print(f"[DEBUG] Socket cliente atual: {id(client)}")
                        print(f"[DEBUG] Socket player1_client: {id(info.get('player1_client'))}")
                        print(f"[DEBUG] Socket player2_client: {id(info.get('player2_client')) if info.get('player2_client') else 'None'}")
                        
                        # marca qual jogador ficou pronto
                        if client == info.get('player1_client'):
                            info['player1_pronto'] = True
                            print(f"\n✓ Player 1 ({info.get('player1')}) pronto na sala {sala_pronto}")
                        elif client == info.get('player2_client'):
                            info['player2_pronto'] = True
                            print(f"\n✓ Player 2 ({info.get('player2')}) pronto na sala {sala_pronto}")
                        else:
                            print(f"\n⚠ AVISO: Cliente {player_name} não encontrado na sala {sala_pronto}!")
                            print(f"[DEBUG] Comparação P1: {client == info.get('player1_client')}")
                            print(f"[DEBUG] Comparação P2: {client == info.get('player2_client')}")
                        
                        # se ambos estão prontos, notifica ambos para iniciar a batalha
                        if info['player1_pronto'] and info['player2_pronto']:
                            print(f"\n[BATALHA] Ambos jogadores prontos na sala {sala_pronto}! Iniciando batalha...")
                            print(f"[BATALHA] {info['player1']} vs {info['player2']}")
                            try:
                                if info['player1_client']:
                                    info['player1_client'].send(f"BATALHA_INICIAR:{sala_pronto}".encode('utf-8'))
                                    info['player1_client'].send(b"SUA_VEZ")  # player1 começa
                                    print(f"  → Notificado {info['player1']} (SUA VEZ)")
                                if info['player2_client']:
                                    info['player2_client'].send(f"BATALHA_INICIAR:{sala_pronto}".encode('utf-8'))
                                    info['player2_client'].send(b"VEZ_OPONENTE")  # player2 espera
                                    print(f"  → Notificado {info['player2']} (AGUARDE)")
                            except Exception as e:
                                print(f"[ERRO] Erro ao notificar início da batalha: {e}")
                    else:
                        print(f"\n⚠ Sala {sala_pronto} não encontrada!")
                except Exception as e:
                    print(f"Erro ao processar comando /pronto: {e}")
                    import traceback
                    traceback.print_exc()
                continue

            # tratar comando de tiro: /tiro:<sala_id>:<linha>:<coluna>
            if isinstance(msg, str) and msg.startswith('/tiro:'):
                try:
                    parts = msg.split(':', 3)
                    sala_tiro = parts[1]
                    linha = parts[2]
                    coluna = int(parts[3])
                    
                    info = salas.get(sala_tiro)
                    if info:
                        # verificar de quem é a vez
                        eh_player1 = (client == info.get('player1_client'))
                        eh_player2 = (client == info.get('player2_client'))
                        
                        if eh_player1 and info['vez_de'] == 'player1':
                            # player1 atirando - envia para player2
                            oponente = info.get('player2_client')
                            if oponente:
                                oponente.send(f"RECEBER_TIRO:{linha}:{coluna}".encode('utf-8'))
                                print(f"\n[TIRO] Sala {sala_tiro}: {info['player1']} → {info['player2']}: {linha}{coluna}")
                        elif eh_player2 and info['vez_de'] == 'player2':
                            # player2 atirando - envia para player1
                            oponente = info.get('player1_client')
                            if oponente:
                                oponente.send(f"RECEBER_TIRO:{linha}:{coluna}".encode('utf-8'))
                                print(f"\n[TIRO] Sala {sala_tiro}: {info['player2']} → {info['player1']}: {linha}{coluna}")
                        else:
                            # não é a vez deste jogador
                            client.send(b"ERRO:NAO_SUA_VEZ")
                            print(f"\n[TIRO] Sala {sala_tiro}: Tentativa fora da vez de {player_name} (vez de: {info['vez_de']})")
                    else:
                        print(f"\n[ERRO] Sala {sala_tiro} não encontrada para tiro de {player_name}")
                except Exception as e:
                    print(f"[ERRO] Erro ao processar tiro: {e}")
                    import traceback
                    traceback.print_exc()
                continue

            # tratar resposta de tiro: /resultado_tiro:<sala_id>:<resultado>
            if isinstance(msg, str) and msg.startswith('/resultado_tiro:'):
                try:
                    parts = msg.split(':', 2)
                    sala_resultado = parts[1]
                    resultado = parts[2]  # "acerto", "erro", "vitoria"
                    
                    info = salas.get(sala_resultado)
                    if info:
                        # identifica quem enviou o resultado (quem recebeu o tiro)
                        if client == info.get('player1_client'):
                            # player1 foi atacado, então era vez de player2
                            atacante = info.get('player2_client')
                            
                            if resultado == "vitoria":
                                # player2 venceu (afundou todos os navios de player1)
                                print(f"\n[VITORIA] Player 2 venceu na sala {sala_resultado}!")
                                if atacante:
                                    atacante.send(f"RESULTADO_TIRO:{resultado}".encode('utf-8'))
                                    atacante.send(b"VITORIA")
                                if client:
                                    client.send(b"DERROTA")
                            else:
                                if atacante:
                                    atacante.send(f"RESULTADO_TIRO:{resultado}".encode('utf-8'))
                                # troca turno apenas se erro
                                if resultado == "erro":
                                    info['vez_de'] = 'player1'
                                    info['player1_client'].send(b"SUA_VEZ")
                                    info['player2_client'].send(b"VEZ_OPONENTE")
                                elif resultado == "acerto":
                                    # se acerto, player2 continua - envia SUA_VEZ novamente
                                    info['player2_client'].send(b"SUA_VEZ")
                                print(f"\n[RESULTADO] Sala {sala_resultado}: {info['player1']} responde '{resultado}' ao tiro de {info['player2']}, próxima vez: {info['vez_de']}")
                        elif client == info.get('player2_client'):
                            # player2 foi atacado, então era vez de player1
                            atacante = info.get('player1_client')
                            
                            if resultado == "vitoria":
                                # player1 venceu (afundou todos os navios de player2)
                                print(f"\n[VITORIA] Sala {sala_resultado}: {info['player1']} venceu contra {info['player2']}!")
                                if atacante:
                                    atacante.send(f"RESULTADO_TIRO:{resultado}".encode('utf-8'))
                                    atacante.send(b"VITORIA")
                                if client:
                                    client.send(b"DERROTA")
                            else:
                                if atacante:
                                    atacante.send(f"RESULTADO_TIRO:{resultado}".encode('utf-8'))
                                # troca turno apenas se erro
                                if resultado == "erro":
                                    info['vez_de'] = 'player2'
                                    info['player1_client'].send(b"VEZ_OPONENTE")
                                    info['player2_client'].send(b"SUA_VEZ")
                                elif resultado == "acerto":
                                    # se acerto, player1 continua - envia SUA_VEZ novamente
                                    info['player1_client'].send(b"SUA_VEZ")
                                # se acerto, player1 continua
                                print(f"\n[RESULTADO] Sala {sala_resultado}: {info['player2']} responde '{resultado}' ao tiro de {info['player1']}, próxima vez: {info['vez_de']}")
                except Exception as e:
                    print(f"Erro ao processar resultado: {e}")
                    import traceback
                    traceback.print_exc()
                continue

            # tratar mensagem de desconexão voluntária
            if isinstance(msg, str) and '/quit' in msg:
                # remover da lista sem fechar a conexão
                removeFromList(client, player_name)
                aviso = f"{player_name} saiu da sala.".encode('utf-8')
                broadcast(aviso, client)
                break

            # caso normal: retransmitir os bytes recebidos
            broadcast(msg_bytes, client)
        except:
            deleteClient(client, player_name)
            break


def deleteClient(client, player_name):
    try:
        clients.remove((client, player_name))
        print(f"\n{player_name} desconectado! Total de jogadores: {len(clients)}")
    except ValueError:
        pass
    try:
        client.close()
    except:
        pass

def removeFromList(client, player_name):
    """Remove cliente da lista sem fechar a conexão."""
    try:
        clients.remove((client, player_name))
        print(f"\n{player_name} removido da lista! Total de jogadores ativos: {len(clients)}")
    except ValueError:
        pass

""""
def salaCriada(player_name, salaID):
    try:
        salas.append((salaID, player_name))

    except:
        pass
"""

def broadcast(msg, client):
    # iterate over the global clients list (not over the single client socket)
    for clientItem, player_name in clients:
        if clientItem != client:
            try:
                clientItem.send(msg)
            except:
                deleteClient(clientItem, player_name)

def criar_sala(client, player_name):
    """Cria uma nova sala e retorna o ID. Armazena também o socket do player1."""
    global salas
    sala_id = str(uuid.uuid4())[:8]  # ID curto de 8 caracteres
    salas[sala_id] = {
        "creator": player_name,
        "player1": player_name,  # Quem criou é o player1
        "player1_client": client,
        "player2": None,
        "player2_client": None,
        "player1_pronto": False,
        "player2_pronto": False,
        "vez_de": "player1"  # controla de quem é a vez (player1 começa)
    }
    print(f"\nSala criada: {sala_id} por {player_name}")
    return sala_id

def listar_salas_disponiveis():
    """Retorna lista de salas disponíveis (com apenas 1 player)."""
    global salas
    salas_disponiveis = []
    for sala_id, info in salas.items():
        if info["player1"] is not None and info["player2"] is None:
            salas_disponiveis.append(f"{sala_id}|{info['creator']}")
    return salas_disponiveis

main()