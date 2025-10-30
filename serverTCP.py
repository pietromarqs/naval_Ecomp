import socket

HOST = '127.0.0.1'
PORT = 12345

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print('Aguardando Conexão de um cliente')
    conn, addr = s.accept()
    
    print('Conectado em', addr)

    while True:
        data = conn.recv(1024)
        if 
