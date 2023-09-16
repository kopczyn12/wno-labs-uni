import socket
import threading
import PIL
from PIL import Image
from PySide6.QtGui import QFont, QCloseEvent,QAction, QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QToolBar, QStatusBar, QWidget, QVBoxLayout, QTextEdit, QHBoxLayout, QLineEdit, QPushButton
import sys
from PySide6 import QtGui

class MainWindow(QMainWindow):

    def __init__(self, user):
        super().__init__()
        self.user = user
        
        self.setWindowTitle(f"Communicator - {self.user} user")
        self.setGeometry(100, 100, 1000, 500)

        toolbar = QToolBar("My main toolbar")
        self.addToolBar(toolbar)

        button_action = QAction("Disconnect", self)
        button_action.setStatusTip("This is your button")
        button_action.triggered.connect(self.onMyToolBarButtonClick)
        toolbar.addAction(button_action)

        self.setStatusBar(QStatusBar(self))


    def onMyToolBarButtonClick(self):
        self.close()

text_chars = ["@", "0", "#", "S", "%", "?", "*", "+", "=", ";", ":", "-", ",", "."]
received_file = "rf"

#"Logging users"
print("Log in to the app")
user = input("Your username: ")

#Connection of client
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 5000))


#preprocessing data for ASCII art
def gray_it_out(image):
    gray_image = image.convert("L")
    return gray_image


def resize_image(image, updated_width=100):
    width, height = image.size
    ratio = height / width * 0.5
    updated_height = int(updated_width * ratio)
    resized_image = image.resize((updated_width, updated_height))
    return resized_image


def pixels_to_text(image):
    pixels = image.getdata()
    characters = "".join([text_chars[pixel // 25] for pixel in pixels])
    return characters


def convert(client_socket, image, updated_width=100):
    new_data = pixels_to_text(gray_it_out(resize_image(image)))
    new_data_lines = [new_data[i:i + updated_width] for i in range(0, len(new_data), updated_width)]
    msg = "\n".join(new_data_lines) + "\n"

    while msg:
        sent = client_socket.send(msg.encode())
        msg = msg[sent:]


def send_msg(client_socket):
    msg = input_box.text()
    if msg[:8] == "!sendimg":
        try:
            path = msg[9:]
            image = PIL.Image.open(path)
            convert(client_socket, image)
        except:
            messages_box.append(f"{path} img is incorrect.\n")
    elif msg[:9] == "!sendfile":
        try:
            path = msg[10:]
            file = open(path, "rb")
            parts = path.split(".")
            file_to_send = f"{received_file}.{parts[1]}"
            client_socket.send(file_to_send.encode())
            data = file.read()
            client_socket.sendall(data)
            client_socket.send(b" ")
            file.close()
        except:
            messages_box.append(f"{path} file is incorrect.\n")
    elif msg == "" or msg == "rf":
        pass
    else:
        full_msg = f"{user}: " + msg
        client_socket.send(full_msg.encode())


def receive_msg(client_socket):
    buff_size = 16
    full_msg = ''
    while True:
        try:
            msg = client_socket.recv(buff_size).decode()
            if msg[:2] == received_file:
                parts = msg.split(".")
                file_name = f"received.{parts[1]}"
                file = open(file_name, "wb")
                file_bytes = b""
                done = False
                data = client_socket.recv(buff_size)
                while not done:
                    if len(data) == buff_size:
                        file_bytes += data
                        data = client_socket.recv(buff_size)
                    else:
                        file_bytes += data[:-1]
                        done = True

                file.write(file_bytes)
                file.close()
            elif len(msg) == buff_size:
                full_msg += msg
            else:
                full_msg += msg
                messages_box.append(full_msg)
                full_msg = ''
        except:
            break


def handle_msg():
    send_thread = threading.Thread(target=send_msg, args=(client_socket,))
    send_thread.start()
    send_thread.join()
    input_box.clear()

# Setting the main window
app = QApplication([])
window = MainWindow(user)


# Main Widget
main_widget = QWidget()
window.setCentralWidget(main_widget)
main_layout = QVBoxLayout()
main_widget.setLayout(main_layout)

#Info - toolbar
messages_box = QTextEdit()
messages_box.setReadOnly(True)
messages_box.toMarkdown()
font = QFont("Arial", 20)
messages_box.setFont(font)
main_layout.addWidget(messages_box)
messages_box.append("                                           HOW TO USE THE APP                      ")
messages_box.append("If you want to send a normal message to the other user, just type this message in line box and click send button.")
messages_box.append("If you want to send a jpg as an ASCII art, type: !sendimg example.jpg.")
messages_box.append("If you want to transfer a docx file, type: !sendfile example.docx.")


# Message box
messages_box = QTextEdit()
messages_box.setReadOnly(True)
font = QFont("Arial", 13)
messages_box.setFont(font)
main_layout.addWidget(messages_box)

# Added layouts
input_layout = QHBoxLayout()
main_layout.addLayout(input_layout)

# Space where you can write your messages
input_box = QLineEdit()
input_layout.addWidget(input_box)

# send button
send_button = QPushButton("Send")
send_button.clicked.connect(handle_msg)
input_layout.addWidget(send_button)


receive_thread = threading.Thread(target=receive_msg, args=(client_socket,))
receive_thread.start()

window.show()
app.exec()
client_socket.close()
