import threading
import socket

HOST = '127.0.0.1'
PORT = 12345

def main():

    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect((HOST, PORT))
    except:
        return print('\n Não foi possível se conectar ao servidor!')
    
    username = input("Usuário: ")
    print("\n Conectado")

    thread1 = threading.Thread(target=receiveMessages, args=[client])
    thread2 = threading.Thread(target=sendMessages, args=[client, username])

    thread1.start()
    thread2.start()


def receiveMessages(client):
    while True:
        try:
            msg = client.recv(1024).decode('utf-8')
            print(msg+'\n')
        except:
            print('\n Não foi possível permanecer conectado no servidor\n')
            print('Pressione <Enter> para continuar')
            client.close()
            break

def sendMessages(client, username):
    while True:
        try:
            msg = input('\n')
            client.send(f'<{username}> {msg}'.encode('utf-8'))
        except:
            return
        





main()