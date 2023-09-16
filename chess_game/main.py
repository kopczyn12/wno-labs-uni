import sys
import math
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import xml.etree.ElementTree as ET
import chess_resources
import json
from xml.dom import minidom
import sqlite3
import os
import socket
import threading
import re
import ast
import random
import chess
import chess.engine
import keras.models as models
import keras.layers as layers
import numpy as np
import time

# CONSTANTS at begginning
board = [['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
         ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
         ['', '', '', '', '', '', '', ''],
         ['', '', '', '', '', '', '', ''],
         ['', '', '', '', '', '', '', ''],
         ['', '', '', '', '', '', '', ''],
         ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
         ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']]

move = False

class ChessAI():
    def __init__(self):
        pass
        board3d = layers.Input(shape=(8,8,14))

        x = board3d
        for _ in range(4):
            x = layers.Conv2D(filters = 32, kernel_size=3, padding='same')(x)
        x = layers.Flatten()(x)
        x = layers.Dense(64, 'relu')(x)
        x = layers.Dense(1, 'sigmoid')(x)
        
        self.model = models.Model(inputs = board3d, outputs = x)
        self.model.load_weights('chess.h5')
        
        self.squares_index = {
            'a': 0,
            'b': 1,
            'c': 2,
            'd': 3,
            'e': 4,
            'f': 5,
            'g': 6,
            'h': 7
        }
        
        self.board = chess.Board()


    def square_to_index(self, square):
        letter = chess.square_name(square)
        return 8 - int(letter[1]), self.squares_index[letter[0]]

    def split_dims(self):
        board3d = np.zeros((14,8,8), dtype=np.int8)

        for piece in chess.PIECE_TYPES:
            for square in self.board.pieces(piece, chess.WHITE):
                idx = np.unravel_index(square, (8, 8))
                board3d[piece - 1][7 - idx[0]][idx[1]] = 1
            for square in self.board.pieces(piece, chess.BLACK):
                idx = np.unravel_index(square, (8, 8))
                board3d[piece + 5][7 - idx[0]][idx[1]] = 1 

        aux = self.board.turn
        self.board.turn = chess.WHITE
        for move in self.board.legal_moves:
            i, j = self.square_to_index(move.to_square)
            board3d[12][i][j] = 1
        self.board.turn = chess.BLACK
        for move in self.board.legal_moves:
            i, j = self.square_to_index(move.to_square)
            board3d[13][i][j] = 1
        self.board.turn = aux
        
        return board3d


    def minimax_eval(self):
        board3d = self.split_dims()
        board3d = np.transpose(board3d, (1,2,0))
        board3d = np.expand_dims(board3d, 0)
        return self.model.predict(board3d)[0][0]

    def minimax(self, depth, alpha, beta, maximizing_player):
        if depth == 0 or self.board.is_game_over():
            return self.minimax_eval()

        if maximizing_player:
            max_eval = -np.inf
            for move in self.board.legal_moves:
                self.board.push(move)
                eval = self.minimax(depth - 1, alpha, beta, False)
                self.board.pop()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  
            return max_eval
        else:
            min_eval = np.inf
            for move in self.board.legal_moves:
                self.board.push(move)
                eval = self.minimax(depth - 1, alpha, beta, True)
                self.board.pop()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval


    def get_ai_move(self, depth):
        max_move = None
        max_eval = -np.inf
        for move in self.board.legal_moves:
            self.board.push(move)
            eval = self.minimax(depth - 1, -np.inf, np.inf, False)
            self.board.pop()
            if eval > max_eval:
                max_eval = eval
                max_move = move
                
        return max_move
    
    def test(self):
        global board
        move = str(self.get_ai_move(1))
        print(move)
        start_pos = (ord(move[0]) - ord('a'), int(move[1]) - 1)  
        end_pos = (ord(move[2]) - ord('a'), int(move[3]) - 1)  
        st_y, st_x = start_pos
        ed_y, ed_x = end_pos
        print(st_x, st_y)
        print(ed_x, ed_y)
        fig = board[st_x][st_y]
        board[st_x][st_y] =  ''
        board[ed_x][ed_y] = fig
        window.scene.turn = -window.scene.turn
        window.scene.draw_board()
        window.scene.update()
        

class Client:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = int(port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.sock.connect((self.ip, self.port))
        print(f"Successfully connected to server at {self.ip}:{self.port}\n")

    def send_message(self):
        message = str(board)
        if message:
            self.sock.send(message.encode())

    def receive_message(self, message_received):
        while True:
            try:
                message = self.sock.recv(1024).decode()
                if not message:
                    break
                else:
                    message_received.emit(message)

            except:
                break

    def start(self):
        self.connect()

        send = threading.Thread(target=self.send_message)
        receive = threading.Thread(target=self.receive_message)

        receive.start()
        send.start()

        receive.join()
        send.join()

        self.sock.close()


class ClientThread(QThread):
    message_received = pyqtSignal(str)

    def __init__(self, client):
        QThread.__init__(self)
        self.client = client

    def run(self):
        self.client.connect()

        send = threading.Thread(target=self.client.send_message)
        receive = threading.Thread(target=self.client.receive_message, args=(self.message_received,))

        receive.start()
        send.start()

        receive.join()
        send.join()

        self.client.sock.close()


class ChessBoard(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setSceneRect(0, 0, 800, 800)
        self.skin = [QColor(255, 255, 240), QColor(139, 69, 19), QBrush(Qt.lightGray)]
        self.setBackgroundBrush(self.skin[2])
        self.selected_piece = None
        self.highlighted = [[]]
        self.turn = 1
        self.my_turn = 1
        self.draw_board()

        self.ppm_menu = QMenu()
        self.skin1_action = QAction("Skin 1", self)
        self.skin2_action = QAction("Skin 2", self)
        self.skin3_action = QAction("Skin 3", self)
        self.ppm_menu.addAction(self.skin1_action)
        self.ppm_menu.addAction(self.skin2_action)
        self.ppm_menu.addAction(self.skin3_action)

        self.skin1_action.triggered.connect(lambda: self.changeSkin(QColor(250, 250, 210),
                                                                    QColor(47, 79, 79),
                                                                    QBrush(QColor(189, 183, 107))))
        self.skin2_action.triggered.connect(lambda: self.changeSkin(QColor(255, 240, 245),
                                                                    QColor(199, 21, 133),
                                                                    QBrush(QColor(216, 191, 216))))
        self.skin3_action.triggered.connect(lambda: self.changeSkin(QColor(240, 255, 240),
                                                                    QColor(85, 107, 47),
                                                                    QBrush(QColor(152, 251, 152))))
        
    def draw_board(self):
        font = self.font()
        font.setPointSize(16)
        self.clear()
        self.setBackgroundBrush(self.skin[2])
        self.pieces_matrix = [[0 for x in range(8)] for y in range(8)]

        for row in range(8):
            for col in range(8):
                x = col * 100
                y = row * 100
                if (row + col) % 2 == 0:
                    chequer = Chequer(x, y, 100, self.skin[0])
                else:
                    chequer = Chequer(x, y, 100, self.skin[1])

                if [col, row] in self.highlighted:
                    chequer.color = Qt.green

                self.addItem(chequer)

                fig = board[row][col]
                if fig.isupper():
                    color = QColor(0, 0, 0)
                elif fig.islower():
                    color = QColor(255, 255, 255)
                else:
                    continue

                piece = Chessfig(x + 30, y + 30, 40, color, fig)
                self.pieces_matrix[col][row] = piece
                self.addItem(piece)

        # Creating labels with notat
        for row in range(8):
            value_label = QGraphicsTextItem(str(8 - row))
            value_label.setFont(font)
            value_label.setPos(-40, row * 100 + 20)
            self.addItem(value_label)
        for col in range(8):
            letter_label = QGraphicsTextItem(chr(65 + col))
            letter_label.setFont(font)
            letter_label.setPos(col * 100 + 40, 810)
            self.addItem(letter_label)

        # Adding the label to show self.turn
        if self.turn == 1:
            turn_label = QGraphicsTextItem("Player 1 (White)")
        else:
            turn_label = QGraphicsTextItem("Player 2 (Black)")

        if self.turn == self.my_turn:
            turn_label.setPlainText(turn_label.toPlainText() + " [YOU]")

        font = self.font()
        font.setPointSize(20)
        turn_label.setFont(font)
        turn_label.setPos(300, -50)
        self.addItem(turn_label)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.ppm_menu.exec(event.screenPos())

        super().mousePressEvent(event)

    def changeSkin(self, color1, color2, brush):
        self.skin = [color1, color2, brush]
        self.draw_board()

    def save_game_history_to_xml(self, game_id):
        xml_file = "game_history.xml"

        if not os.path.exists(xml_file) or os.stat(xml_file).st_size == 0:
            # Create a new XML tree if the file doesn't exist or is empty
            root = ET.Element("game_histories")
        else:
            # Load the existing XML tree if the file is not empty
            tree = ET.parse(xml_file)
            root = tree.getroot()

        # Create a new game_history element and add it to the root
        game_history_elem = ET.SubElement(root, "game_history", {"id": str(game_id)})

        for row_idx, row in enumerate(self.pieces_matrix):
            row_elem = ET.SubElement(game_history_elem, "row", {"id": str(row_idx)})

            for col_idx, piece in enumerate(row):
                piece_elem = ET.SubElement(row_elem, "piece", {"id": str(col_idx)})
                if piece != 0:
                    piece_elem.text = piece.fig
                    piece_elem.set("color", "white" if piece.color == QColor(255, 255, 255) else "black")
                else:
                    piece_elem.text = ""

        # Save the updated XML tree to the file
        xml_string = ET.tostring(root, encoding="utf-8")
        parsed_xml = minidom.parseString(xml_string)

        with open(xml_file, "w", encoding="utf-8") as xml_out:
            xml_out.write(parsed_xml.toprettyxml(indent="  "))


class Chequer(QGraphicsItem):
    def __init__(self, x, y, size, color, parent=None):
        super().__init__(parent)
        self.rect = QRectF(x, y, size, size)
        self.color = color
        self.piece = None
        self.highlighted = False

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget=None):
        painter.fillRect(self.rect, self.color)
        pen = QPen(Qt.black, 2)
        painter.setPen(pen)
        painter.drawRect(self.rect)

    def setHighlight(self, highlight):
        self.highlighted = highlight

    def getHighlighted(self):
        return self.highlighted


class Chessfig(QGraphicsItem):
    def __init__(self, x, y, size, color, fig, parent=None):
        super().__init__(parent)
        self.trueX = x - 30 + 50
        self.trueY = y - 30 + 50
        self.y = int((y - 30) / 100)
        self.x = int((x - 30) / 100)
        self.rect = QRectF(x, y, size, size)
        self.color = color
        self.fig = fig
        self.setZValue(1)
        self.setAcceptHoverEvents(True)

        # Loading chess from files qrc
        if fig.isupper():
            image_path = f":/chess_img/black_{fig}.png"
        elif fig.islower():
            image_path = f":/chess_img/white_{fig}.png"
        else:
            raise ValueError(f'Invalid figure: {fig}')
        self.img = QImage(image_path)

        # Resize image to fit bounding rectangle
        self.img = self.img.scaled(int(self.rect.width()), int(self.rect.height()),
                                   Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget=None):
        # Drawing image
        painter.drawImage(self.rect, self.img)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton \
                and ((window.scene.turn == 1 and self.fig.islower()) \
                     or (window.scene.turn == -1 and self.fig.isupper())):
            self.setCursor(Qt.ClosedHandCursor)
            self.offset = self.rect.center()

            window.scene.highlighted = [[]]

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton \
                and ((window.scene.turn == 1 and self.fig.islower()) \
                     or (window.scene.turn == -1 and self.fig.isupper())) \
                and window.scene.turn == window.scene.my_turn:
            self.setPos(event.scenePos() - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.OpenHandCursor)

            x, y = self.pos().x(), self.pos().y()
            x = int((x - (x + 50) % 100 + 50) / 100)
            y = int((y - (y + 50) % 100 + 50) / 100)

            self.setPos(x * 100, y * 100)
            self.setCoordinates(x, y)

            window.scene.draw_board()

    def hoverEnterEvent(self, event):
        if (window.scene.turn == 1 and self.fig.islower()) \
                or (window.scene.turn == -1 and self.fig.isupper()) \
                and window.scene.turn == window.scene.my_turn:
            self.setCursor(Qt.OpenHandCursor)
        else:
            self.unsetCursor()

    def hoverLeaveEvent(self, event):
        self.unsetCursor()

    def setCoordinates(self, moveX, moveY):
        piece_set = False
       
        wan_X = int(self.x + moveX)
        wan_Y = int(self.y + moveY)

        if wan_X == int(self.x) and wan_Y == int(self.y):
            self.highlightMoves(wan_X, wan_Y)

        else:

            self.highlightMoves(self.x, self.y)
            if self.chess_correctness_of_move(wan_X, wan_Y) and ([wan_X, wan_Y] in window.scene.highlighted):
                piece_set = True
                with open('configuration.json') as f:
                    config = json.load(f)
                    if config["ai_mode"] == True:
                        bot = ChessAI()
                        bot.test()                
                board[int(self.y)][int(self.x)] = ''
                self.x = self.x + moveX
                self.y = self.y + moveY
                board[int(self.y)][int(self.x)] = self.fig
                if window.client:
                    window.client.send_message()
                window.scene.turn = -window.scene.turn
                window.clock.time_start = QTime.currentTime()
                        
            window.scene.highlighted = [[]]
        return piece_set

    def chess_correctness_of_move(self, wan_X, wan_Y):

        if wan_X < 0 or wan_X > 7 or wan_Y < 0 or wan_Y > 7:
            return 0

        upper1 = board[int(self.y)][int(self.x)].isupper()
        upper2 = board[wan_Y][wan_X].isupper()
        lower1 = board[int(self.y)][int(self.x)].islower()
        lower2 = board[wan_Y][wan_X].islower()

        if upper1 and upper2 or lower1 and lower2:
            return 0

        elif board[wan_Y][wan_X] != '':
            return 1
        else:
            return 2

    def highlightMoves(self, wan_X, wan_Y):
        window.scene.highlighted = [[wan_X, wan_Y]]

        if self.fig == 'P':
            if self.y == 1:
                move_range = 2
            else:
                move_range = 1
            for i in range(move_range):
                if self.chess_correctness_of_move(wan_X, wan_Y + 1 + i) == 2:
                    window.scene.highlighted.append([wan_X, wan_Y + 1 + i])
                elif self.chess_correctness_of_move(wan_X, wan_Y + 1 + i) == 1:
                    break
            if self.chess_correctness_of_move(wan_X - 1, wan_Y + 1) == 1:
                window.scene.highlighted.append([wan_X - 1, wan_Y + 1])
            if self.chess_correctness_of_move(wan_X + 1, wan_Y + 1) == 1:
                window.scene.highlighted.append([wan_X + 1, wan_Y + 1])

        # Lower pawn
        elif self.fig == 'p':
            if self.y == 6:
                move_range = 2
            else:
                move_range = 1
            for i in range(move_range):
                if self.chess_correctness_of_move(wan_X, wan_Y - 1 - i) == 2:
                    window.scene.highlighted.append([wan_X, wan_Y - 1 - i])
                elif self.chess_correctness_of_move(wan_X, wan_Y - 1 - i) == 1:
                    break
            if self.chess_correctness_of_move(wan_X - 1, wan_Y - 1) == 1:
                window.scene.highlighted.append([wan_X - 1, wan_Y - 1])
            if self.chess_correctness_of_move(wan_X + 1, wan_Y - 1) == 1:
                window.scene.highlighted.append([wan_X + 1, wan_Y - 1])

        # Kings
        elif self.fig == 'K' or self.fig == 'k':
            if self.chess_correctness_of_move(wan_X + 1, wan_Y):
                window.scene.highlighted.append([wan_X + 1, wan_Y])
            if self.chess_correctness_of_move(wan_X, wan_Y + 1):
                window.scene.highlighted.append([wan_X, wan_Y + 1])
            if self.chess_correctness_of_move(wan_X + 1, wan_Y + 1):
                window.scene.highlighted.append([wan_X + 1, wan_Y + 1])
            if self.chess_correctness_of_move(wan_X - 1, wan_Y):
                window.scene.highlighted.append([wan_X - 1, wan_Y])
            if self.chess_correctness_of_move(wan_X, wan_Y - 1):
                window.scene.highlighted.append([wan_X, wan_Y - 1])
            if self.chess_correctness_of_move(wan_X - 1, wan_Y - 1):
                window.scene.highlighted.append([wan_X - 1, wan_Y - 1])
            if self.chess_correctness_of_move(wan_X - 1, wan_Y + 1):
                window.scene.highlighted.append([wan_X - 1, wan_Y + 1])
            if self.chess_correctness_of_move(wan_X + 1, wan_Y - 1):
                window.scene.highlighted.append([wan_X + 1, wan_Y - 1])

        # Queens
        elif self.fig == 'Q' or self.fig == 'q':
            for i in range(8):
                if self.chess_correctness_of_move(wan_X + 1 + i, wan_Y) == 2:
                    window.scene.highlighted.append([wan_X + 1 + i, wan_Y])
                elif self.chess_correctness_of_move(wan_X + 1 + i, wan_Y) == 1:
                    window.scene.highlighted.append([wan_X + 1 + i, wan_Y])
                    break
                else:
                    break
            for i in range(8):
                if self.chess_correctness_of_move(wan_X, wan_Y + 1 + i) == 2:
                    window.scene.highlighted.append([wan_X, wan_Y + 1 + i])
                elif self.chess_correctness_of_move(wan_X, wan_Y + 1 + i) == 1:
                    window.scene.highlighted.append([wan_X, wan_Y + 1 + i])
                    break
                else:
                    break
            for i in range(8):
                if self.chess_correctness_of_move(wan_X + 1 + i, wan_Y + 1 + i) == 2:
                    window.scene.highlighted.append([wan_X + 1 + i, wan_Y + 1 + i])
                elif self.chess_correctness_of_move(wan_X + 1 + i, wan_Y + 1 + i) == 1:
                    window.scene.highlighted.append([wan_X + 1 + i, wan_Y + 1 + i])
                    break
                else:
                    break
            for i in range(8):
                if self.chess_correctness_of_move(wan_X - 1 - i, wan_Y) == 2:
                    window.scene.highlighted.append([wan_X - 1 - i, wan_Y])
                elif self.chess_correctness_of_move(wan_X - 1 - i, wan_Y) == 1:
                    window.scene.highlighted.append([wan_X - 1 - i, wan_Y])
                    break
                else:
                    break
            for i in range(8):
                if self.chess_correctness_of_move(wan_X, wan_Y - 1 - i) == 2:
                    window.scene.highlighted.append([wan_X, wan_Y - 1 - i])
                elif self.chess_correctness_of_move(wan_X, wan_Y - 1 - i) == 1:
                    window.scene.highlighted.append([wan_X, wan_Y - 1 - i])
                    break
                else:
                    break
            for i in range(8):
                if self.chess_correctness_of_move(wan_X - 1 - i, wan_Y - 1 - i) == 2:
                    window.scene.highlighted.append([wan_X - 1 - i, wan_Y - 1 - i])
                elif self.chess_correctness_of_move(wan_X - 1 - i, wan_Y - 1 - i) == 1:
                    window.scene.highlighted.append([wan_X - 1 - i, wan_Y - 1 - i])
                    break
                else:
                    break
            for i in range(8):
                if self.chess_correctness_of_move(wan_X - 1 - i, wan_Y + 1 + i) == 2:
                    window.scene.highlighted.append([wan_X - 1 - i, wan_Y + 1 + i])
                elif self.chess_correctness_of_move(wan_X - 1 - i, wan_Y + 1 + i) == 1:
                    window.scene.highlighted.append([wan_X - 1 - i, wan_Y + 1 + i])
                    break
                else:
                    break
            for i in range(8):
                if self.chess_correctness_of_move(wan_X + 1 + i, wan_Y - 1 - i) == 2:
                    window.scene.highlighted.append([wan_X + 1 + i, wan_Y - 1 - i])
                elif self.chess_correctness_of_move(wan_X + 1 + i, wan_Y - 1 - i) == 1:
                    window.scene.highlighted.append([wan_X + 1 + i, wan_Y - 1 - i])
                    break
                else:
                    break

        # Bishops
        elif self.fig == 'B' or self.fig == 'b':
            for i in range(8):
                if self.chess_correctness_of_move(wan_X + 1 + i, wan_Y + 1 + i) == 2:
                    window.scene.highlighted.append([wan_X + 1 + i, wan_Y + 1 + i])
                elif self.chess_correctness_of_move(wan_X + 1 + i, wan_Y + 1 + i) == 1:
                    window.scene.highlighted.append([wan_X + 1 + i, wan_Y + 1 + i])
                    break
                else:
                    break
            for i in range(8):
                if self.chess_correctness_of_move(wan_X - 1 - i, wan_Y - 1 - i) == 2:
                    window.scene.highlighted.append([wan_X - 1 - i, wan_Y - 1 - i])
                elif self.chess_correctness_of_move(wan_X - 1 - i, wan_Y - 1 - i) == 1:
                    window.scene.highlighted.append([wan_X - 1 - i, wan_Y - 1 - i])
                    break
                else:
                    break
            for i in range(8):
                if self.chess_correctness_of_move(wan_X - 1 - i, wan_Y + 1 + i) == 2:
                    window.scene.highlighted.append([wan_X - 1 - i, wan_Y + 1 + i])
                elif self.chess_correctness_of_move(wan_X - 1 - i, wan_Y + 1 + i) == 1:
                    window.scene.highlighted.append([wan_X - 1 - i, wan_Y + 1 + i])
                    break
                else:
                    break
            for i in range(8):
                if self.chess_correctness_of_move(wan_X + 1 + i, wan_Y - 1 - i) == 2:
                    window.scene.highlighted.append([wan_X + 1 + i, wan_Y - 1 - i])
                elif self.chess_correctness_of_move(wan_X + 1 + i, wan_Y - 1 - i) == 1:
                    window.scene.highlighted.append([wan_X + 1 + i, wan_Y - 1 - i])
                    break
                else:
                    break

        # Rooks
        elif self.fig == 'R' or self.fig == 'r':
            for i in range(8):
                if self.chess_correctness_of_move(wan_X + 1 + i, wan_Y) == 2:
                    window.scene.highlighted.append([wan_X + 1 + i, wan_Y])
                elif self.chess_correctness_of_move(wan_X + 1 + i, wan_Y) == 1:
                    window.scene.highlighted.append([wan_X + 1 + i, wan_Y])
                    break
                else:
                    break
            for i in range(8):
                if self.chess_correctness_of_move(wan_X, wan_Y + 1 + i) == 2:
                    window.scene.highlighted.append([wan_X, wan_Y + 1 + i])
                elif self.chess_correctness_of_move(wan_X, wan_Y + 1 + i) == 1:
                    window.scene.highlighted.append([wan_X, wan_Y + 1 + i])
                    break
                else:
                    break
            for i in range(8):
                if self.chess_correctness_of_move(wan_X - 1 - i, wan_Y) == 2:
                    window.scene.highlighted.append([wan_X - 1 - i, wan_Y])
                elif self.chess_correctness_of_move(wan_X - 1 - i, wan_Y) == 1:
                    window.scene.highlighted.append([wan_X - 1 - i, wan_Y])
                    break
                else:
                    break
            for i in range(8):
                if self.chess_correctness_of_move(wan_X, wan_Y - 1 - i) == 2:
                    window.scene.highlighted.append([wan_X, wan_Y - 1 - i])
                elif self.chess_correctness_of_move(wan_X, wan_Y - 1 - i) == 1:
                    window.scene.highlighted.append([wan_X, wan_Y - 1 - i])
                    break
                else:
                    break

        # Knights
        elif self.fig == 'N' or self.fig == 'n':
            if self.chess_correctness_of_move(wan_X - 2, wan_Y + 1):
                window.scene.highlighted.append([wan_X - 2, wan_Y + 1])
            if self.chess_correctness_of_move(wan_X - 2, wan_Y - 1):
                window.scene.highlighted.append([wan_X - 2, wan_Y - 1])
            if self.chess_correctness_of_move(wan_X + 2, wan_Y + 1):
                window.scene.highlighted.append([wan_X + 2, wan_Y + 1])
            if self.chess_correctness_of_move(wan_X + 2, wan_Y - 1):
                window.scene.highlighted.append([wan_X + 2, wan_Y - 1])
            if self.chess_correctness_of_move(wan_X - 1, wan_Y - 2):
                window.scene.highlighted.append([wan_X - 1, wan_Y - 2])
            if self.chess_correctness_of_move(wan_X + 1, wan_Y - 2):
                window.scene.highlighted.append([wan_X + 1, wan_Y - 2])
            if self.chess_correctness_of_move(wan_X - 1, wan_Y + 2):
                window.scene.highlighted.append([wan_X - 1, wan_Y + 2])
            if self.chess_correctness_of_move(wan_X + 1, wan_Y + 2):
                window.scene.highlighted.append([wan_X + 1, wan_Y + 2])
        return window.scene.highlighted


class AnalogClock(QGraphicsItem):
    def __init__(self):
        super().__init__()
        self.time_start = QTime.currentTime()
        self.clock_size = 200
        self.seconds_hand = QGraphicsPolygonItem(self)
        self.milliseconds_hand = QGraphicsPolygonItem(self)
        self.seconds_hand.setBrush(QColor(0, 127, 127))
        self.milliseconds_hand.setBrush(QColor(127, 0, 127))
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_hands)
        self.timer.start(1)

        self.start_angle = 0
        self.reset_start_angle()

        self.seconds_hand.setPolygon(self.create_hand(self.start_angle, self.clock_size / 2))
        self.milliseconds_hand.setPolygon(self.create_hand(self.start_angle, self.clock_size / 2))

    def reset_start_angle(self):
        self.start_angle = 0

    def update_hands(self):
        time = QTime.currentTime()
        angle_sec = self.start_angle + 6 * (
                    (time.second() - self.time_start.second()) + (time.msec() - self.time_start.msec()) / 1000)
        angle_msec = self.start_angle + 3.6 * ((time.msec() - self.time_start.msec()) / 10)
        self.seconds_hand.setPolygon(self.create_hand(angle_sec, self.clock_size / 2))
        self.milliseconds_hand.setPolygon(self.create_hand(angle_msec, self.clock_size / 2))

        if self.start_angle is None:
            self.reset_start_angle()

    def boundingRect(self):
        return QRectF(-self.clock_size / 2, -self.clock_size / 2, self.clock_size, self.clock_size)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawEllipse(-self.clock_size / 2, -self.clock_size / 2, self.clock_size, self.clock_size)

        for i in range(60):
            painter.save()
            painter.rotate(i * 6)
            painter.drawLine(self.clock_size / 2 - 10, 0, self.clock_size / 2, 0)
            painter.restore()

    def create_hand(self, angle, length):
        rad_angle = math.radians(angle)
        end_point = QPointF(length * math.sin(rad_angle), -length * math.cos(rad_angle))
        points = [QPointF(0, 0), end_point]
        return QPolygonF(points)

    def reset_clock(self):
        self.time_start = QTime.currentTime()
        self.reset_start_angle()


class ConfigurationDialog(QDialog):
    def __init__(self, parent=None, game_id=0):
        super().__init__(parent)
        self.game_id = game_id
        self.setWindowTitle('Configuration')

        layout = QVBoxLayout()

        self.save_to_database_checkbox = QCheckBox("Save game history to database (SQLite3)")
        layout.addWidget(self.save_to_database_checkbox)

        self.xml_game_history_checkbox = QCheckBox("Save game history as XML")
        layout.addWidget(self.xml_game_history_checkbox)

        self.one_player_checkbox = QRadioButton("1 Player")
        layout.addWidget(self.one_player_checkbox)

        self.two_player_checkbox = QRadioButton("2 Players")
        layout.addWidget(self.two_player_checkbox)

        self.ai_checkbox = QRadioButton("Vs AI")
        layout.addWidget(self.ai_checkbox)

        self.save_game_button = QPushButton("Save Game")
        self.save_game_button.clicked.connect(self.save_game)
        layout.addWidget(self.save_game_button)

        self.save_configuration_button = QPushButton("Save Configuration")
        self.save_configuration_button.clicked.connect(self.save_configuration)
        layout.addWidget(self.save_configuration_button)

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect)
        layout.addWidget(self.connect_button)

        self.ip_address_label = QLabel("IP Address:")
        self.ip_address_input = QLineEdit()
        self.ip_address_input.setText(socket.gethostbyname(socket.gethostname()))
        layout.addWidget(self.ip_address_label)
        layout.addWidget(self.ip_address_input)

        self.port_label = QLabel("Port:")
        self.port_input = QLineEdit()

        layout.addWidget(self.port_label)
        layout.addWidget(self.port_input)

        self.load_configuration()

        self.setLayout(layout)

    def save_configuration(self):
        # Save the configuration options
        config_options = {
            "save_game_history_to_db": self.save_to_database_checkbox.isChecked(),
            "save_game_history_to_xml": self.xml_game_history_checkbox.isChecked(),
            "one_player_mode": self.one_player_checkbox.isChecked(),
            "two_players_mode": self.two_player_checkbox.isChecked(),
            "ai_mode": self.ai_checkbox.isChecked(),
            "ip_address": self.ip_address_input.text(),
            "port": self.port_input.text(),
        }
        with open("configuration.json", "w") as config_file:
            json.dump(config_options, config_file, indent=4)

    def load_configuration(self):
        try:
            with open("configuration.json", "r") as config_file:
                config_contents = config_file.read().strip()
                if not config_contents:
                    return

                config_options = json.loads(config_contents)

            self.save_to_database_checkbox.setChecked(config_options.get("save_game_history_to_db", False))
            self.xml_game_history_checkbox.setChecked(config_options.get("save_game_history_to_xml", False))
            self.one_player_checkbox.setChecked(config_options.get("one_player_mode", False))
            self.two_player_checkbox.setChecked(config_options.get("two_players_mode", False))
            self.ai_checkbox.setChecked(config_options.get("ai_mode", False))
            self.ip_address_input.setText(config_options.get("ip_address", ""))
            self.port_input.setText(config_options.get("port", ""))
        except FileNotFoundError:
            # If the configuration file doesn't exist, don't load any configuration
            pass

    def connect(self):
        ip = self.ip_address_input.text()
        port = self.port_input.text()
        window.client = Client(ip, port)
        window.client_thread = ClientThread(window.client)
        window.client_thread.message_received.connect(window.on_message_received)
        window.client_thread.start()

    def save_game(self):
        game_history = self.parent().get_game_history()

        if self.save_to_database_checkbox.isChecked():
            try:
                self.parent().save_game_history_to_database(self.parent().game_id, game_history)
                print("Game history saved to database.")
            except Exception as e:
                print("Error saving game history to database:", e)

        if self.xml_game_history_checkbox.isChecked():
            try:
                self.parent().scene.save_game_history_to_xml(self.parent().game_id)
                print("Game history saved to XML.")
            except Exception as e:
                print("Error saving game history to XML:", e)

        # Increment the game_id after saving the game
        self.parent().increment_game_id()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 1100, 1100)
        self.setWindowTitle("Chess WNO")
        self.game_id = 0
        self.client = None
        self.client_thread = None
        central_widget = QWidget(self)
        layout = QGridLayout(central_widget)
        self.view = QGraphicsView(self)
        self.scene = ChessBoard()
        self.view.setScene(self.scene)
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.clock_view = QGraphicsView(self)
        self.clock_scene = QGraphicsScene()
        self.clock = AnalogClock()
        self.clock_scene.addItem(self.clock)
        self.clock_view.setScene(self.clock_scene)
        self.clock_view.setRenderHint(QPainter.Antialiasing)
        self.clock_view.setFixedSize(300, 300)
        self.clock_view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.clock_scene.setBackgroundBrush(Qt.lightGray)
        self.start_stop_button = QPushButton("Reset: Second Player turn!")
        self.start_stop_button.clicked.connect(self.clock.reset_clock)
        
        self.config_button = QPushButton("Configuration")
        self.config_button.clicked.connect(self.open_configuration_dialog)

        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.close)

        self.chess_notat_input = QLineEdit()
        self.chess_notat_input.setFixedSize(200, 50)
        self.chess_notat_input.returnPressed.connect(self.chess_notat)

        self.chess_notat_label = QLabel("Chess notation input")
        font = QFont()
        font.setBold(True)
        font.setPointSize(22)
        self.chess_notat_label.setFont(font)

        layout.addWidget(self.chess_notat_label, 0, 0)
        layout.addWidget(self.chess_notat_input, 1, 0)
        layout.addWidget(self.view, 0, 1, 5, 1)
        layout.addWidget(self.clock_view, 0, 2)
        layout.addWidget(self.start_stop_button, 1, 2)
        layout.addWidget(self.quit_button, 3, 2)
        layout.addWidget(self.config_button, 2, 2)


        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.lightGray)
        self.setPalette(palette)

        self.setCentralWidget(central_widget)
        self.showFullScreen()

    def increment_game_id(self):
        self.game_id += 1

    def on_message_received(self, message):
        global board
        print(f"{message}")
        pattern = r"\[\[.*\]\]"
        result = re.search(pattern, message)
        if result:
            matrix_str = result.group()
            board = ast.literal_eval(matrix_str)
        else:
            pass

        self.scene.turn = -self.scene.turn
        self.clock.time_start = QTime.currentTime()
        self.scene.draw_board()
        self.scene.update()

    def chess_notat(self):
        notat = list(self.chess_notat_input.text().replace(' ', ''))

        if len(notat) == 2:
            notat.insert(0, 'p')

        if len(notat) == 4 and notat[0].upper() == 'N':
            fig = notat[0]
            x_dest, y_dest = ord(notat[1].upper()) - ord('A'), 7 - (ord(notat[2]) - ord('1'))
        elif len(notat) == 3:
            fig = notat[0].lower() if self.scene.turn == 1 else notat[0].upper()
            x_dest, y_dest = ord(notat[1].upper()) - ord('A'), 7 - (ord(notat[2]) - ord('1'))

            if fig in ('N', 'n'):
                n_idx = [(row_idx, col_idx) for row_idx, row in enumerate(board) for col_idx, val in enumerate(row) if
                         val == fig]

                knight1_able, knight2_able = False, False
                for idx, (n_x, n_y) in enumerate(n_idx):
                    self.scene.pieces_matrix[n_x][n_y].highlightMoves(n_x, n_y)

                    if self.scene.pieces_matrix[n_x][n_y].chess_correctness_of_move(x_dest, y_dest) and (
                            [x_dest, y_dest] in self.scene.highlighted):
                        if idx == 0:
                            knight1_able = True
                        else:
                            knight2_able = True

                    self.scene.highlighted = [[]]

                if knight1_able and knight2_able:
                    self.chess_notat_input.clear()
                    return

            idx = [(row_idx, col_idx) for row_idx, row in enumerate(board) for col_idx, val in enumerate(row) if
                   val == fig]

            for coords in idx:
                piece = self.scene.pieces_matrix[coords[1]][coords[0]]
                relativeX, relativeY = x_dest - piece.x, y_dest - piece.y
                if piece.setCoordinates(relativeX, relativeY):
                    self.scene.draw_board()
                    break

        self.chess_notat_input.clear()

    def open_configuration_dialog(self):
        config_dialog = ConfigurationDialog(parent=self, game_id=self.game_id)
        config_dialog.exec_()

    def get_game_history(self):
        history_string = ""

        # Iterate over the board and create the history string
        for row in range(8):
            for col in range(8):
                piece = self.scene.pieces_matrix[col][row]
                if piece != 0:
                    piece_type = piece.fig
                    if piece.color == QColor(255, 255, 255):
                        piece_type = piece_type.lower()
                    history_string += f"{piece_type} at ({col}, {row})\n"

        return history_string

    def save_game_history_to_database(self, game_id, game_history):
        # Connect to the database (or create it if it doesn't exist)
        connection = sqlite3.connect("game_history.db")
        cursor = connection.cursor()

        # Create the game_history table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id INTEGER,
        history TEXT
        )
        """)

        # Insert the game history into the table
        cursor.execute("INSERT INTO game_history (game_id, history) VALUES (?, ?)", (game_id, game_history))

        # Commit the changes and close the connection
        connection.commit()
        connection.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
