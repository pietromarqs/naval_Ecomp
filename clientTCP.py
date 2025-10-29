import socket

HOST = '127.0.0.1'  # endereço do servidor
PORT = 12345        # mesma porta do servidor

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'Hello, servidor TCP!')
    data = s.recv(1024)

print(f"Resposta do servidor: {data.decode()}")