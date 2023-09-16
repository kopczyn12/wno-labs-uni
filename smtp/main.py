import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton
from email.message import EmailMessage
from utils import send_email_mech, receive_mail_mech
import re
from model import calculate_similarity
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

EMAIL_REGEX = r'[\w\.-]+@[\w\.-]+'

class EmailClient(QMainWindow):
    def __init__(self):
        super().__init__()

        self.autorespond = False
        self.setWindowTitle('Email Client')
        self.showMaximized()
        # Create UI widgets
        self.inbox_widget = QTextEdit()
        self.compose_widget = QWidget()
        self.to_label = QLabel("To:")
        self.to_input = QLineEdit()
        self.subject_label = QLabel("Subject:")
        self.subject_input = QLineEdit()
        self.body_label = QLabel("Body:")
        self.label_box = QLabel('Enter a number of mail you want to read:')
        self.input_box = QLineEdit()
        self.label_filter_box= QLabel('Enter a keyword that you want to filter mails: ')
        self.input_filter_box = QLineEdit()

        self.content_of_mail_label =  QLabel('Content of chosen mail:')
        self.content_of_mail_input = QTextEdit()
        self.body_input = QTextEdit()
        self.send_button = QPushButton("Send")
        self.auto_respond_button = QPushButton("Autorespond ON/OFF")
        self.autorespond_box = QLineEdit()
        self.show_email_button = QPushButton("Show the content of chosen mail")
        self.receive_mails_button = QPushButton("Receive mails")
        self.filter_mails_on_keyword = QPushButton("Filter mails on the keyword in the subject and update the inbox")

        # Create layouts
        self.compose_layout = QVBoxLayout()
        self.to_layout = QHBoxLayout()
        self.subject_layout = QHBoxLayout()
        self.body_layout = QVBoxLayout()
        # Create a horizontal layout to hold the label and input box
        self.input_layout = QHBoxLayout()
        self.input_layout.addWidget(self.label_box)
        self.input_layout.addWidget(self.input_box)
        self.content_of_mail_layout = QVBoxLayout()
        self.main_layout = QHBoxLayout()

        # Add widgets to layouts
        self.to_layout.addWidget(self.to_label)
        self.to_layout.addWidget(self.to_input)
        self.subject_layout.addWidget(self.subject_label)
        self.subject_layout.addWidget(self.subject_input)
        self.body_layout.addWidget(self.body_label)
        self.body_layout.addWidget(self.body_input)
        self.content_of_mail_layout.addWidget(self.content_of_mail_label)
        self.content_of_mail_layout.addWidget(self.content_of_mail_input)
        self.compose_layout.addWidget(self.receive_mails_button)
        self.compose_layout.addLayout(self.to_layout)
        self.compose_layout.addLayout(self.subject_layout)
        self.compose_layout.addLayout(self.body_layout)
        self.compose_layout.addWidget(self.send_button)
        self.compose_layout.addLayout(self.input_layout)
        self.compose_layout.addWidget(self.show_email_button)        
        self.compose_layout.addLayout(self.content_of_mail_layout)
        self.compose_layout.addWidget(self.auto_respond_button)
        self.compose_layout.addWidget(self.autorespond_box)
        self.compose_layout.addWidget(self.label_filter_box)
        self.compose_layout.addWidget(self.input_filter_box)
        self.compose_layout.addWidget(self.filter_mails_on_keyword)
        self.compose_widget.setLayout(self.compose_layout)
        self.main_layout.addWidget(self.inbox_widget)
        self.main_layout.addWidget(self.compose_widget)
        self.autorespond_box.setText("Autoresponder disabled - you send mail for received mails by yourself.")

        # Set the main layout
        main_widget = QWidget()
        main_widget.setLayout(self.main_layout)
        self.setCentralWidget(main_widget)

        # Connect signals and slots
        self.send_button.clicked.connect(self.send_email)
        self.auto_respond_button.clicked.connect(self.auto_respond)
        self.show_email_button.clicked.connect(self.show_chosen_mail)
        self.receive_mails_button.clicked.connect(self.reveive_mail)
        self.filter_mails_on_keyword.clicked.connect(self.filter_inbox)
    
    def send_email(self):
        send_email_mech(email_receiver=self.to_input.text(), email=self.body_input.toPlainText(), subject=self.subject_input.text())

    def reveive_mail(self):
        self.inbox_widget.clear()
        self.sender, self.subject, self.content, self.counter = receive_mail_mech()
        match_adress = []
        match_group = []
        for x in range(self.counter):
            match_adress.append(re.search(EMAIL_REGEX, self.sender[x]))
            match_group.append(match_adress[x].group())
        for x in range(self.counter):
            if self.subject[x] == None:
                self.subject[x] = 'None'
            else:
                self.inbox_widget.append("Index of mail: " + str(x+1) + "\n")
                self.inbox_widget.append('\n')
                mess = "Sender: " + match_group[x] +"\n" +"Subject: " + self.subject[x] + "\n" 
                self.inbox_widget.append(mess)
                self.inbox_widget.append('\n') 
        if self.autorespond:
            self.inbox_widget.clear()
            match_adress = []
            match_group = []
            print('Sending autorespond mails to all contacts...')
            for x in range(self.counter):
                match_adress.append(re.search(EMAIL_REGEX, self.sender[x]))
                match_group.append(match_adress[x].group())
                msg = "I am on the vacation!"
                send_email_mech(match_group[x], msg , 'debug of the at feature')
                print(f'Autorespond to {match_group[x]} has been sent.')
            print('Sending autorespond mails finished.')
            print("Reloading the inbox...")
            # time.sleep(4)
            self.sender, self.subject, self.content, self.counter = receive_mail_mech()  
            for x in range(self.counter):
                match_adress.append(re.search(EMAIL_REGEX, self.sender[x]))
                match_group.append(match_adress[x].group())
            for x in range(self.counter):
                if self.subject[x] == None:
                    self.subject[x] = 'None'
                else:
                    self.inbox_widget.append("Index of mail: " + str(x+1) + "\n")
                    self.inbox_widget.append('\n')
                    mess = "Sender: " + match_group[x] +"\n" +"Subject: " + self.subject[x] + "\n" 
                    self.inbox_widget.append(mess)
                    self.inbox_widget.append('\n')  

    def auto_respond(self):
        # self.sender, self.subject, self.content, self.counter = receive_mail_mech()
        # idx = int(self.input_box.text())
        # for x in range(self.counter):
        #     if x == (idx - 1):
        #         msg = "I am on the vacation!"
        #         match_adress = re.search(EMAIL_REGEX, self.sender[x])
        #         match_group = match_adress.group()
        #         send_email_mech(match_group, msg , 'Autorespond due to holiday')
        #         print(f'Autorespond to {match_group} has been sent.')
        if not self.autorespond:          
            self.autorespond = True
            self.autorespond_box.setText("Autoresponder enabled - automatically send mail for received mails.")
        else:
            self.autorespond = False
            self.autorespond_box.setText("Autoresponder disabled - you send mail for received mails by yourself.")




    def show_chosen_mail(self):
        self.sender, self.subject, self.content, self.counter = receive_mail_mech()
        idx = int(self.input_box.text())
        for x in range(self.counter):
            if x == (idx-1):
                self.content_of_mail_input.setText(self.content[x])
                mess = f"Mail number {idx} has been already seen\n"
                self.inbox_widget.append(mess)

    def filter_inbox(self):
        self.inbox_widget.clear()       
        self.sender, self.subject, self.content, self.counter = receive_mail_mech()
        match_adress = []
        match_group = []
        for x in range(self.counter):
            match_adress.append(re.search(EMAIL_REGEX, self.sender[x]))
            match_group.append(match_adress[x].group()) 

        self.keyword = self.input_filter_box.text()
        for x in range(self.counter):
            sim = calculate_similarity(self.subject[x], self.keyword)
            if sim >0.28:
                if self.subject[x] == None:
                    self.subject[x] = 'None'
                else:
                    self.inbox_widget.append("Index of mail: " + str(x+1) + "\n")
                    self.inbox_widget.append('\n')
                    mess = "Sender: " + match_group[x] +"\n" +"Subject: " + self.subject[x] + "\n" 
                    self.inbox_widget.append(mess)
                    self.inbox_widget.append('\n')              
                    
    def create_an_account(self):
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = EmailClient()
    client.show()
    sys.exit(app.exec())