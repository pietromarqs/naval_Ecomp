import socket

HOST = '127.0.0.1'  # localhost
PORT = 12345        # porta arbitrária

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Servidor TCP escutando em {HOST}:{PORT}...")
    conn, addr = s.accept()
    with conn:
        print(f"Conectado por {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f"Recebido: {data.decode()}")
            data2 = b'Ola, Cliente!'
            conn.sendall(data2)