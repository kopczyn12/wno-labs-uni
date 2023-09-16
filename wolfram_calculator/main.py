from PyQt5.QtWidgets import QApplication, QPushButton, QGridLayout, QWidget, QLineEdit, QLabel, QTextEdit
from PyQt5.QtGui import QPixmap, QPalette, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import urllib.request


class Calculator():
    def __init__(self, equation):
        super().__init__()

        self.url = 'https://www.wolframalpha.com/'
        self.options = Options()
        self.options.add_argument("--headless")
        self.driver = webdriver.Chrome(
            '/Users/mkopczynski/Downloads/differential-equations-wolfram-main/chromedriver', chrome_options=self.options)
        self.equation = equation
        self.plot_error = 0

    def calculate(self):
        self.driver.get(self.url)
        self.input_field = self.driver.find_element(
            By.XPATH, '//*[@id="__next"]/div/div[1]/div/div/div[1]/section/form/div/div/input')
        self.input_field.send_keys(self.equation)
        self.input_field.send_keys(Keys.RETURN)
        time.sleep(5)

        try:
            self.header = self.driver.find_element(
                By.XPATH, '//*[contains(text(), "Differential equation solution")]')
            self.solution_image = self.header.find_element(
                By.XPATH, 'following::img[1]')
            self.solution = self.solution_image.get_attribute('alt')
            solution_url = self.solution_image.get_attribute('src')
            urllib.request.urlretrieve(solution_url, 'solution_img.png')
        except:
            print('No avaliable solution')

        try:
            self.plot1_header = self.driver.find_element(
                By.XPATH, '//*[contains(text(), "Slope field")]')
            self.plot1 = self.plot1_header.find_element(
                By.XPATH, 'following::img[1]')
            plot1_url = self.plot1.get_attribute('src')
            urllib.request.urlretrieve(plot1_url, 'plot1')
        except:
            print('There is no Slope field plot')
            self.plot_error = 1
        try:
            self.plot2_header = self.driver.find_element(
                By.XPATH, '//*[contains(text(), "Plots of sample individual solution")]')
            self.plot2 = self.plot2_header.find_element(
                By.XPATH, 'following::img[1]')
            plot2_url = self.plot2.get_attribute('src')
            urllib.request.urlretrieve(plot2_url, 'plot2')
        except:
            print('There is no Plots of sample individual solution')
            self.plot_error = 2
        try:
            self.plot3_header = self.driver.find_element(
                By.XPATH, '//*[contains(text(), "Sample solution family")]')
            self.plot3 = self.plot3_header.find_element(
                By.XPATH, 'following::img[1]')
            plot3_url = self.plot3.get_attribute('src')
            urllib.request.urlretrieve(plot3_url, 'plot3')
        except:
            print('There is no Sample solution family plot')
            self.plot_error = 3

        self.driver.quit()
        print(self.plot_error)
        return self.solution, self.plot_error
    
class Application(QWidget):
    def __init__(self):
        super().__init__()

        # Configure matplotlib
        plt.rcParams['figure.facecolor'] = '#333333'
        plt.rcParams['axes.facecolor'] = '#333333'
        plt.rcParams['savefig.facecolor'] = '#333333'
        plt.rcParams['text.color'] = 'white'
        plt.rcParams['xtick.color'] = 'white'
        plt.rcParams['ytick.color'] = 'white'
        plt.rcParams['axes.labelcolor'] = 'white'
        plt.rcParams['font.weight'] = 'bold'  # set font to bold in matplotlib

        # Create UI elements
        self.input_field = QLineEdit(self)
        self.button = QPushButton('Calculate', self)
        self.label = QLabel(self)
        self.textedit = QTextEdit(self)
        self.figure1 = Figure()
        self.canvas1 = FigureCanvas(self.figure1)
        self.figure2 = Figure()
        self.canvas2 = FigureCanvas(self.figure2)
        self.figure3 = Figure()
        self.canvas3 = FigureCanvas(self.figure3)

        self.plot1_label = QLabel(self)
        self.plot1_label.setText('Slope field')
        self.plot2_label = QLabel(self)
        self.plot2_label.setText('Plots of sample individual solution')
        self.plot3_label = QLabel(self)
        self.plot3_label.setText('Sample solution family')

        # Connect button to calculate method
        self.button.clicked.connect(self.calculate)

        # Create layout and add UI elements
        layout = QGridLayout()
        layout.addWidget(self.input_field, 0, 0)
        layout.addWidget(self.button, 0, 1)
        layout.addWidget(self.label, 1, 0, 1, 2)
        layout.addWidget(self.textedit, 2, 0, 1, 2)

        layout.addWidget(self.plot3_label, 3, 0)
        layout.addWidget(self.canvas3, 4, 0)

        layout.addWidget(self.plot1_label, 3, 1)
        layout.addWidget(self.canvas1, 4, 1)

        layout.addWidget(self.plot2_label, 3, 2)
        layout.addWidget(self.canvas2, 4, 2)

        self.setLayout(layout)

    def calculate(self):

        input_text = self.input_field.text()
        input_text = 'diff equation ' + input_text
        self.calculator = Calculator(input_text)
        self.output_text, self.plot_error = self.calculator.calculate()
        self.textedit.setText(
            f"Solution: {self.output_text}")

        try:
            if self.plot_error == 1:
                img1 = mpimg.imread('blank')
                ax1 = self.figure1.add_subplot(111)
                ax1.set_axis_off()
                ax1.imshow(img1)
                self.canvas1.draw()
            else:
                img1 = mpimg.imread('plot1')
                ax1 = self.figure1.add_subplot(111)
                ax1.set_axis_off()
                ax1.imshow(img1)
                self.canvas1.draw()
        except:
            print('There is no plot 1')

        try:
            if self.plot_error == 2:
                img2 = mpimg.imread('blank')
                ax2 = self.figure2.add_subplot(111)
                ax2.set_axis_off()
                ax2.imshow(img2)
                self.canvas2.draw()
            else:
                img2 = mpimg.imread('plot2')
                ax2 = self.figure2.add_subplot(111)
                ax2.set_axis_off()
                ax2.imshow(img2)
                self.canvas2.draw()
        except:
            print("There is no plot 2")

        try:
            if self.plot_error == 3:
                img3 = mpimg.imread('blank')
                ax3 = self.figure3.add_subplot(111)
                ax3.set_axis_off()
                ax3.imshow(img3)
                self.canvas3.draw()
            else:
                img3 = mpimg.imread('plot3')
                ax3 = self.figure3.add_subplot(111)
                ax3.set_axis_off()
                ax3.imshow(img3)
                self.canvas3.draw()
        except:
            print("There is no plot 3")

        pixmap = QPixmap('solution_img.png')
        self.label.setPixmap(pixmap)

def main() -> None:
    app = QApplication(sys.argv)

    # Set the dark theme palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
    palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)

    # Set the dark theme style sheet
    app.setStyleSheet(
        "QPushButton { background-color: #333333; color: #ffffff; font-weight: bold; }"
        "QLineEdit { background-color: #333333; color: #ffffff; font-weight: bold; }"
        "QTextEdit { background-color: #333333; color: #ffffff; font-weight: bold; }"
        "QLabel { font-weight: bold; }"
)

    window = Application()
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()