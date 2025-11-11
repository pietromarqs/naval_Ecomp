import socket
import threading

HOST = '127.0.0.1'
PORT = 12345

clients = []

def main():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((HOST, PORT))
        server.listen()
    except:
        return print('\nNão foi possível iniciar o servidor! \n')

    while True:
        client, addr = server.accept()
        clients.append(client)


        thread = threading.Thread(target= messagesTreatment, args=[client])
        thread.start()



def messagesTreatment(client):
    while True:
        try:
            msg = client.recv(1024)
            broadcast(msg, client)
        except:
            deleteClient(client)
            break


def deleteClient(client):
    try:
        clients.remove(client)
    except ValueError:
        pass
    try:
        client.close()
    except:
        pass


def broadcast(msg, client):
    # iterate over the global clients list (not over the single client socket)
    for clientItem in clients:
        if clientItem != client:
            try:
                clientItem.send(msg)
            except:
                deleteClient(clientItem)
                




main()