import threading
import socket

HOST = '127.0.0.1'
PORT = 12345

client = None
player_number = None
player_name_global = None
salaId = None
running = True  # flag para parar threads
sala_criada = None  # armazena ID da sala criada
salas_disponiveis = []  # lista de salas para conexão
on_sala_iniciada = None  # callback quando sala inicia: func(sala_id, role)
on_batalha_iniciar = None  # callback quando ambos jogadores estão prontos: func(sala_id)
_receive_thread_started = False
_sala_entrada_response = None  # resposta de entrada na sala
_salas_list_response = None  # resposta de listagem de salas
sala_atual = None  # ID da sala em que o jogador está

def main(start_send_thread: bool = True, start_receive_thread: bool = True):
    """
    Conecta ao servidor.
    - start_send_thread: se True, inicia a thread que lê do stdin e envia (útil para modo console)
    - start_receive_thread: se True, inicia a thread que lê mensagens do socket de forma assíncrona
    Para uso pela GUI, chame: main(start_send_thread=False, start_receive_thread=False)
    """
    global client, player_number, running
    running = True

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((HOST, PORT))
    except Exception as e:
        print('\n Não foi possível se conectar ao servidor!')
        raise

    # Receber o número do player do servidor
    try:
        player_number = client.recv(1024).decode("utf-8")
    except Exception as e:
        print('\n Não foi possível receber o número do player!')
        raise

    player_name = f"Player {player_number}"
    # armazenar nome globalmente para uso em disconnect
    global player_name_global
    player_name_global = player_name
    print(f"\n Conectado como {player_name}")

    if start_receive_thread:
        thread1 = threading.Thread(target=receiveMessages, args=[client], daemon=True)
        thread1.start()
        global _receive_thread_started
        _receive_thread_started = True

    if start_send_thread:
        thread2 = threading.Thread(target=sendMessages, args=[client, player_name], daemon=True)
        thread2.start()


on_receber_tiro = None  # callback para processar tiro recebido: func(linha, coluna)
on_resultado_tiro = None  # callback para processar resultado: func(resultado)
on_sua_vez = None  # callback quando é a vez do jogador: func()
on_vez_oponente = None  # callback quando é a vez do oponente: func()
on_vitoria = None  # callback quando jogador vence: func()
on_derrota = None  # callback quando jogador perde: func()

def receiveMessages(client):
    global running, sala_criada, sala_atual, _salas_list_response, _sala_entrada_response, on_sala_iniciada, on_batalha_iniciar, on_receber_tiro, on_resultado_tiro, on_sua_vez, on_vez_oponente, on_vitoria, on_derrota
    print("[DEBUG] Thread de recebimento iniciada")
    while running:
        try:
            msg = client.recv(1024).decode('utf-8')
            if msg:
                print(f"[DEBUG] Mensagem recebida: {msg[:50]}...")  # primeiros 50 caracteres
                # tratar mensagens de protocolo
                if msg.startswith('SALA_CRIADA:'):
                    # recebido quando cria sala
                    sid = msg.split(':', 1)[1]
                    sala_criada = sid
                    sala_atual = sid  # define sala atual para o criador
                    print(f"\n[THREAD] Sala criada com ID: {sid}")
                    print(f"[THREAD] sala_criada atualizada para: {sala_criada}")
                    continue
                if msg.startswith('SALAS:'):
                    # resposta de listagem
                    _salas_list_response = msg
                    print(f"\nResposta lista salas: {msg}")
                    continue
                if msg.startswith('SALA_ENTRADA:'):
                    # resposta de entrada na sala
                    _sala_entrada_response = msg
                    print(f"\nResposta entrada sala: {msg}")
                    continue
                if msg.startswith('SALA_INICIAR:'):
                    # Notificação de que a sala está pronta
                    payload = msg.split(':', 1)[1]
                    try:
                        sala_id, role = payload.split('|', 1)
                    except Exception:
                        sala_id, role = payload, None
                    print(f"\nSala iniciada {sala_id} como {role}")
                    sala_atual = sala_id  # armazena sala atual
                    try:
                        on_sala_iniciada and on_sala_iniciada(sala_id, role)
                    except Exception:
                        pass
                    continue
                if msg.startswith('BATALHA_INICIAR:'):
                    # Notificação de que ambos jogadores estão prontos
                    sala_id = msg.split(':', 1)[1]
                    print(f"\nBatalha iniciando na sala {sala_id}!")
                    try:
                        on_batalha_iniciar and on_batalha_iniciar(sala_id)
                    except Exception:
                        pass
                    continue
                if msg == 'SUA_VEZ':
                    print("\nSUA VEZ de jogar!")
                    try:
                        on_sua_vez and on_sua_vez()
                    except Exception:
                        pass
                    continue
                if msg == 'VEZ_OPONENTE':
                    print("\nAguarde a vez do oponente...")
                    try:
                        on_vez_oponente and on_vez_oponente()
                    except Exception:
                        pass
                    continue
                if msg.startswith('RECEBER_TIRO:'):
                    # recebeu um tiro do oponente
                    parts = msg.split(':', 2)
                    linha = parts[1]
                    coluna = int(parts[2])
                    print(f"\nOponente atirou em {linha}{coluna}")
                    try:
                        on_receber_tiro and on_receber_tiro(linha, coluna)
                    except Exception:
                        pass
                    continue
                if msg.startswith('RESULTADO_TIRO:'):
                    # resultado do tiro que você deu
                    resultado = msg.split(':', 1)[1]
                    print(f"\nResultado do seu tiro: {resultado}")
                    try:
                        on_resultado_tiro and on_resultado_tiro(resultado)
                    except Exception:
                        pass
                    continue
                if msg == 'VITORIA':
                    print("\nVOCE VENCEU!")
                    try:
                        on_vitoria and on_vitoria()
                    except Exception:
                        pass
                    continue
                if msg == 'DERROTA':
                    print("\nVOCE PERDEU!")
                    try:
                        on_derrota and on_derrota()
                    except Exception:
                        pass
                    continue
                # mensagens normais: imprimir
                print(msg+'\n')
        except Exception as e:
            if running:
                print(f'\n[ERRO] Erro ao receber mensagem: {e}\n')
            break
    
    # Thread está saindo - resetar flag para permitir reiniciar
    global _receive_thread_started
    _receive_thread_started = False
    print("[DEBUG] Thread de recebimento encerrada")


def start_receive_thread(force_restart=False):
    """Inicia a thread de recebimento se ainda não iniciada.
    Útil quando a conexão foi feita sem thread e precisamos de notificações do servidor.
    
    Args:
        force_restart: Se True, força reiniciar a thread mesmo que a flag diga que já está rodando
    """
    global _receive_thread_started, client, running
    print(f"[DEBUG] start_receive_thread - já iniciada: {_receive_thread_started}, client existe: {client is not None}, running: {running}, force: {force_restart}")
    
    # Se force_restart, ignora a flag e inicia de novo
    if force_restart:
        print("[DEBUG] Forçando reinício da thread de recebimento...")
        _receive_thread_started = False
    
    if not _receive_thread_started and client:
        print("[DEBUG] Iniciando nova thread de recebimento...")
        running = True  # Garante que está True
        thread = threading.Thread(target=receiveMessages, args=[client], daemon=True)
        thread.start()
        _receive_thread_started = True
        print("[DEBUG] Thread de recebimento iniciada com sucesso")
    elif _receive_thread_started and not force_restart:
        print("[DEBUG] Thread de recebimento já estava rodando (use force_restart=True para reiniciar)")
    elif not client:
        print("[DEBUG] Cliente não existe, não pode iniciar thread")


def sendMessages(client, player_name):
    global running
    while running:
        try:
            msg = input()
            if msg and running:
                client.send(f'<{player_name}> {msg}'.encode('utf-8'))
        except:
            break
"""
def criaSalas():
    global client, salaId

    try: 
        cria_msg = f"<Criador da Sala {player_name_global}>"
        client.send(cria_msg.encode('utf-8'))
    except:
        pass
"""
def disconnect():
    """Desconecta completamente do servidor e reseta todo o estado."""
    global client, player_name_global, running, sala_atual, sala_criada, _sala_entrada_response, _salas_list_response, _receive_thread_started, player_number
    
    print('\n[DISCONNECT] Desconectando do servidor...')
    
    # Para a thread de recebimento
    running = False
    
    # Fecha o socket
    if client:
        try:
            # Tenta enviar mensagem de saída
            quit_msg = f'<{player_name_global}> /quit'
            client.send(quit_msg.encode('utf-8'))
        except Exception:
            pass
        
        try:
            client.close()
            print('[DISCONNECT] Socket fechado')
        except Exception:
            pass
    
    # Reseta TODAS as variáveis globais
    client = None
    sala_atual = None
    sala_criada = None
    _sala_entrada_response = None
    _salas_list_response = None
    _receive_thread_started = False
    
    print('[DISCONNECT] Estado completamente resetado - pronto para nova conexão')
    print('[DISCONNECT] Próxima conexão será completamente nova\n')

def criar_sala_no_servidor():
    """Envia comando ao servidor para criar uma sala."""
    global client, sala_criada, running, _receive_thread_started
    try:
        print(f"[DEBUG] criar_sala_no_servidor - client existe: {client is not None}")
        print(f"[DEBUG] criar_sala_no_servidor - running: {running}")
        print(f"[DEBUG] criar_sala_no_servidor - thread iniciada: {_receive_thread_started}")
        
        if client:
            sala_criada = None  # reseta antes de criar
            print("[DEBUG] Enviando comando /criar_sala ao servidor...")
            client.send('/criar_sala'.encode('utf-8'))
            
            # aguarda resposta via polling (a thread de receive vai preencher sala_criada)
            import time
            start_time = time.time()
            timeout = 5
            
            print("[DEBUG] Aguardando resposta do servidor (timeout: 5s)...")
            while sala_criada is None and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if sala_criada:
                print(f"\n[SUCESSO] Sala criada com ID: {sala_criada}")
                return sala_criada
            else:
                print("\n[ERRO] Timeout ao criar sala - servidor não respondeu")
                print(f"[DEBUG] sala_criada ainda é None após {timeout}s")
        else:
            print("[ERRO] Cliente não está conectado!")
    except Exception as e:
        print(f"[ERRO] Erro ao criar sala: {e}")
        import traceback
        traceback.print_exc()
    return None

def listar_salas_servidor():
    """Requisita lista de salas disponíveis do servidor."""
    global client, salas_disponiveis, _salas_list_response
    try:
        if client:
            # Envia comando e aguarda resposta via polling
            _salas_list_response = None
            client.send('/listar_salas'.encode('utf-8'))
            
            import time
            start_time = time.time()
            timeout = 3
            
            while _salas_list_response is None and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            resposta = _salas_list_response
            
            if resposta and resposta.startswith('SALAS:'):
                salas_str = resposta.split(':', 1)[1]
                if salas_str:
                    salas_disponiveis = salas_str.split(',')
                    print(f"\nSalas disponíveis: {salas_disponiveis}")
                else:
                    salas_disponiveis = []
                    print("\nNenhuma sala disponível")
                return salas_disponiveis
            else:
                print(f"Resposta inesperada: {resposta}")
                return []
    except Exception as e:
        print(f"Erro ao listar salas: {e}")
        import traceback
        traceback.print_exc()
    return []


def entrar_sala_no_servidor(sala_id, timeout=5):
    """Envia comando para entrar em uma sala. Retorna True se aceito, False caso contrário."""
    global client, _sala_entrada_response, _receive_thread_started
    try:
        if client:
            # ensure receive thread is running so notifications arrive
            start_receive_thread()
            _sala_entrada_response = None
            client.send(f"/entrar_sala:{sala_id}".encode('utf-8'))
            
            # aguarda resposta via polling da variável global (thread de receive vai preencher)
            import time
            start_time = time.time()
            while _sala_entrada_response is None and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if _sala_entrada_response and _sala_entrada_response.startswith('SALA_ENTRADA:OK'):
                return True
            return False
    except Exception as e:
        print(f"Erro ao entrar na sala: {e}")
    return False


def enviar_pronto():
    """Envia ao servidor que o jogador está pronto para iniciar a batalha."""
    global client, sala_atual
    try:
        if client and sala_atual:
            client.send(f"/pronto:{sala_atual}".encode('utf-8'))
            print(f"\nEnviado sinal de pronto para sala {sala_atual}")
            return True
    except Exception as e:
        print(f"Erro ao enviar pronto: {e}")
    return False

def enviar_tiro(linha, coluna):
    """Envia um tiro ao servidor."""
    global client, sala_atual
    try:
        if client and sala_atual:
            client.send(f"/tiro:{sala_atual}:{linha}:{coluna}".encode('utf-8'))
            print(f"\nEnviado tiro: {linha}{coluna}")
            return True
    except Exception as e:
        print(f"Erro ao enviar tiro: {e}")
    return False

def enviar_resultado_tiro(resultado):
    """Envia o resultado de um tiro recebido ao servidor."""
    global client, sala_atual
    try:
        if client and sala_atual:
            client.send(f"/resultado_tiro:{sala_atual}:{resultado}".encode('utf-8'))
            print(f"\nEnviado resultado: {resultado}")
            return True
    except Exception as e:
        print(f"Erro ao enviar resultado: {e}")
    return False

def _recv_response(timeout=2):
    """Recebe uma resposta síncrona do servidor aplicando timeout temporário.
    Retorna a string recebida ou None em caso de timeout/erro.
    """
    global client
    if not client:
        return None
    try:
        client.settimeout(timeout)
        data = client.recv(4096).decode('utf-8')
        return data
    except socket.timeout:
        return None
    except Exception as e:
        print(f"Erro ao receber resposta: {e}")
        return None
    finally:
        try:
            client.settimeout(None)
        except Exception:
            pass
