import socket
import threading


def handle_client(conn, addr):
    """Handling with client - connection, receiving data, disconnecting"""
    print(f"New user has been {addr} connected.")
    print(f"Number of active users: {threading.active_count() - 1}")

    connected = True
    while connected:
        try:
            msg = conn.recv(1024)
            if msg:
                broadcast(msg, conn)
                conn.sendall(msg)
        except:
            connected = False

    print(f"User has been {addr} disconnected.")
    conn.close()

#Sending the message to other clietn
def broadcast(msg, sender):
    for client in clients:
        if client != sender:
            client.send(msg)
    

def start_server():
    
    print("Starting new server on PORT: 5000...")

    #Creating TCP/IP socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    #Binding socket to the port
    server.bind(('localhost', 5000))

    #Listening for incoming connections
    server.listen()
    print(f"Server is listening on localhost:5000")

    while True:

        #waiting for connections
        conn, addr = server.accept()
        #adding users to queue
        clients.append(conn)

        #each user working on the thread
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

clients = []
start_server()
