import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random as r
from matplotlib import style
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QApplication

from grid import Grid
from player import Player, find_start_of_optimal_solution

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(400, 200)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(20, 20, 20, 20)
        self.verticalLayout.setSpacing(20)
        self.verticalLayout.setAlignment(QtCore.Qt.AlignCenter)
        
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setText("Select the Size of the Grid (n) :")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.label)

        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setObjectName("comboBox")
        for i in range(2, 11):
            self.comboBox.addItem(str(i))
        self.verticalLayout.addWidget(self.comboBox)

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText("Continue")
        self.pushButton.clicked.connect(self.open_grid_window)
        self.verticalLayout.addWidget(self.pushButton)

        MainWindow.setCentralWidget(self.centralwidget)

    def open_grid_window(self):
        n = int(self.comboBox.currentText())
        self.window = QtWidgets.QMainWindow()
        self.ui = Ui_GridWindow(n)
        self.ui.setupUi(self.window)
        self.window.show()
        MainWindow.close()

class Ui_GridWindow(object):
    def __init__(self, n):
        self.n = n
        self.target_set = False
        self.start_set = False
        self.block_mode = False
        self.grid_buttons = []

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(30, 30, 30, 30)
        self.verticalLayout.setSpacing(20)

        self.label_n = QtWidgets.QLabel(self.centralwidget)
        self.label_n.setText(f"Grid Size: {self.n} x {self.n}")
        self.label_n.setAlignment(QtCore.Qt.AlignLeft)
        self.verticalLayout.addWidget(self.label_n)

        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(20, 20, 20, 20)
        self.gridLayout.setSpacing(20)
        self.gridLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayoutWidget.setLayout(self.gridLayout)
        self.verticalLayout.addWidget(self.gridLayoutWidget)

        # Set the grid layout based on n
        for i in range(self.n):
            row_buttons = []
            for j in range(self.n):
                button = QtWidgets.QPushButton(self.gridLayoutWidget)
                button.setFixedSize(50, 50)
                button.clicked.connect(lambda ch, x=i, y=j: self.grid_button_clicked(x, y))
                self.gridLayout.addWidget(button, i, j)
                row_buttons.append(button)
            self.grid_buttons.append(row_buttons)

        self.continueButton = QtWidgets.QPushButton(self.centralwidget)
        self.continueButton.setText("Set Target")
        self.continueButton.clicked.connect(self.set_target_mode)
        self.verticalLayout.addWidget(self.continueButton)

        MainWindow.setCentralWidget(self.centralwidget)
        
        # Calculate the window size
        gridSize = self.gridLayout.sizeHint()
        windowWidth = gridSize.width() + 100  # Increase padding
        windowHeight = gridSize.height() + 100  # Increase padding
        MainWindow.setGeometry(100, 100, windowWidth, windowHeight)

    def set_target_mode(self):
        self.target_set = True
        self.continueButton.setText("Set Start")
        self.continueButton.clicked.disconnect()
        self.continueButton.clicked.connect(self.set_start_mode)

    def set_start_mode(self):
        self.start_set = True
        self.continueButton.setText("Set Blocked and Finalize")
        self.continueButton.clicked.disconnect()
        self.continueButton.clicked.connect(self.finalize_grid)

    def grid_button_clicked(self, x, y):
        button = self.grid_buttons[x][y]
        if button.text() != "" and button.text() != "Blocked":  # Allow action only if the cell is empty
            return
        if not self.target_set:
            self.clear_previous("Target")
            button.setStyleSheet("background-color: red;")
            button.setText("Target")
        elif not self.start_set:
            self.clear_previous("Start")
            button.setStyleSheet("background-color: green;")
            button.setText("Start")
        elif not self.block_mode:
            if button.text() == "Blocked":
                button.setStyleSheet("")
                button.setText("")
            else:
                button.setStyleSheet("background-color: grey;")
                button.setText("Blocked")

    def clear_previous(self, text):
        for row in self.grid_buttons:
            for button in row:
                if button.text() == text:
                    button.setStyleSheet("")
                    button.setText("")

    def finalize_grid(self):
        grid_representation = []
        for i in range(self.n):
            row = []
            for j in range(self.n):
                row.append(self.grid_buttons[i][j].text() if self.grid_buttons[i][j].text() else "Empty")
            grid_representation.append(row)
        
        print("Final Grid Representation:")
        for row in grid_representation:
            print(row)

        self.open_algorithm_selection_window(grid_representation)

    def open_algorithm_selection_window(self, grid_representation):
        self.algorithm_window = QtWidgets.QMainWindow()
        self.algorithm_ui = Ui_AlgorithmSelectionWindow(self.n, grid_representation, self.grid_buttons)
        self.algorithm_ui.setupUi(self.algorithm_window)
        self.algorithm_window.show()

class Ui_AlgorithmSelectionWindow(object):

    def __init__(self, n, grid_representation, grid_buttons):
        self.n = n
        self.grid_representation = grid_representation
        self.grid_buttons = grid_buttons

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setAlignment(QtCore.Qt.AlignCenter)

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setText("Choose an Option")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.label)

        self.button_qlearning = QtWidgets.QPushButton(self.centralwidget)
        self.button_qlearning.setText("Q-learning")
        self.button_qlearning.clicked.connect(lambda: self.show_final_grid("Q-learning"))
        self.verticalLayout.addWidget(self.button_qlearning)

        self.button_dyna_q = QtWidgets.QPushButton(self.centralwidget)
        self.button_dyna_q.setText("DynaQ")
        self.button_dyna_q.clicked.connect(lambda: self.show_final_grid("DynaQ"))
        self.verticalLayout.addWidget(self.button_dyna_q)

        self.button_dyna_q_plus = QtWidgets.QPushButton(self.centralwidget)
        self.button_dyna_q_plus.setText("DynaQ+")
        self.button_dyna_q_plus.clicked.connect(lambda: self.show_final_grid("DynaQ+"))
        self.verticalLayout.addWidget(self.button_dyna_q_plus)

        self.button_compare = QtWidgets.QPushButton(self.centralwidget)
        self.button_compare.setText("Compare")
        self.button_compare.clicked.connect(lambda: self.show_final_grid("Compare"))
        self.verticalLayout.addWidget(self.button_compare)

        MainWindow.setCentralWidget(self.centralwidget)
        MainWindow.setGeometry(100, 100, 300, 250)

    def show_final_grid(self, algorithm):
        print(f"Selected Algorithm: {algorithm}")
        global start
        grid_representation = []
        blocked_tiles = []
        for i in range(self.n):
            row = []
            for j in range(self.n):
                if self.grid_buttons[i][j].text() == "Blocked":
                    blocked_tiles.append((i, j))
                row.append(self.grid_buttons[i][j].text() if self.grid_buttons[i][j].text() else "Empty")
            grid_representation.append(row)
        
        maze_env = Grid(self.n, blocked_tiles)
        global x_T, y_T, start # Declare global variables for the target position
        x_T, y_T = None, None
        for i in range(self.n):
            for j in range(self.n):
                if grid_representation[i][j] == "Start":
                    start = (i, j)
                elif grid_representation[i][j] == "Target":
                    x_T, y_T = i, j
        player = Player(maze_env, x_T, y_T, start)


        if (algorithm == "Q-learning"):
            player.train_Q()
            optimal_path = player.path(start)
            self.display_colored_grid(grid_representation, optimal_path)
            print("Optimal Path (Q-learning):", optimal_path)
            print("Number of steps taken by agent to reach target (Q-learning):", len(optimal_path) - 1)
            


        elif (algorithm == "DynaQ"):
            player.train_DynaQ()
            optimal_path = player.path(start)
            self.display_colored_grid(grid_representation, optimal_path)
            print("Optimal Path (Dyna-Q):", optimal_path)
            print("Number of steps taken by agent to reach target (Dyna-Q):", len(optimal_path) - 1)
            


        elif(algorithm == "DynaQ+"):
            player.train_DynaQPlus()
            optimal_path = player.path(start)
            self.display_colored_grid(grid_representation, optimal_path)
            print("Optimal Path (Dyna-Q+):", optimal_path)
            print("Number of steps taken by agent to reach target (Dyna-Q+):", len(optimal_path) - 1)
            

        else:
            player1 = Player(maze_env, x_T, y_T, start)
            player2 = Player(maze_env, x_T, y_T, start)
            player3 = Player(maze_env, x_T, y_T, start)

            player1.train_Q()
            Q_steps_per_ep = player1.Q_steps_per_ep

            # player.reset()
            player2.train_DynaQ()
            DynaQ_steps_per_ep = player2.dynaQ_steps_per_ep

            # player.reset()
            player3.train_DynaQPlus()
            DynaQPlus_steps_per_ep = player3.dynaQPlus_steps_per_ep

            # Plot the comparison graph
            plt.figure(figsize=(12, 6))
            plt.plot(Q_steps_per_ep, label='Q-learning', color='b')
            plt.plot(DynaQ_steps_per_ep, label='Dyna-Q', color='g')
            plt.plot(DynaQPlus_steps_per_ep, label='Dyna-Q+', color='r')
            plt.xlabel('Episodes')
            plt.ylabel('Number of Steps')
            plt.title('Comparison of Q-learning, Dyna-Q, and Dyna-Q+')
            plt.legend()
            plt.show()

    def display_colored_grid(self, grid_representation, optimal_path):
        self.color_window = QtWidgets.QMainWindow()
        self.color_centralwidget = QtWidgets.QWidget(self.color_window)
        self.color_gridLayout = QtWidgets.QGridLayout(self.color_centralwidget)
        self.color_centralwidget.setLayout(self.color_gridLayout)

        color_mapping = {
            "Empty": "white",
            "Start": "green",
            "Blocked": "black",
            "Target": "red",
            "Path": "yellow"
        }

        for i in range(self.n):
            for j in range(self.n):
                tile_type = grid_representation[i][j]
                tile_color = color_mapping[tile_type]
                tile_label = QtWidgets.QLabel(self.color_centralwidget)
                tile_label.setStyleSheet(f"background-color: {tile_color}; border: 1px solid black;")
                tile_label.setFixedSize(50, 50)
                if tile_type != "Empty":
                    tile_label.setText(tile_type)
                    tile_label.setAlignment(QtCore.Qt.AlignCenter)
                self.color_gridLayout.addWidget(tile_label, i, j)

        # Highlight the optimal path
        for x, y in optimal_path[1:-1]:
            tile_label = QtWidgets.QLabel(self.color_centralwidget)
            tile_label.setStyleSheet("background-color: yellow; border: 1px solid black;")
            tile_label.setFixedSize(50, 50)
            tile_label.setText("Path")
            tile_label.setAlignment(QtCore.Qt.AlignCenter)
            self.color_gridLayout.addWidget(tile_label, x, y)

        self.color_window.setCentralWidget(self.color_centralwidget)
        self.color_window.setGeometry(100, 100, self.n * 50 + 40, self.n * 50 + 40)
        self.color_window.show()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())