import os
import ast
import sys
import time
import numpy as np
import random
import multiprocessing
import matplotlib.pyplot as plt

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QWidget, QTextEdit, QPushButton, QMessageBox, QLabel, QListWidget, QFileDialog
)
from PyQt5.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from M_UIv2_Supp import UniqueFunctionProcessor, Echo, FileManagerWidget, DynamicGraphWidget


class WindowManager(QMainWindow):
    def __init__(self):
        super().__init__()
        # Main window setting init _____________________________________________________________________________________________
        self.setWindowTitle("Realtime Feature Exstraction Manager")
        self.resize(1000, 400)

        # Main layout
        main_layout = QHBoxLayout()
        
        # Main layout for the window
        self.layout = QVBoxLayout(self)
        
        #___Dynamic Map initializer ___________________________________________________________________________________________
        self.graph_widget = DynamicGraphWidget()
        main_layout.addWidget(self.graph_widget)
        self.graph_widget.hide()
        
        # Button to toggle the visibility of the dynamic graph
        self.GraphButton = QPushButton("Hide Graph")
        self.GraphButton.clicked.connect(self.toggle_graph)
        main_layout.addWidget(self.GraphButton,alignment=Qt.AlignBottom | Qt.AlignRight)
        self.GraphButton.hide()
        
        # Terminal view Initializer ___________________________________________________________________________________________
        self.terminal_view = QTextEdit()
        self.terminal_view.setReadOnly(True)
        self.terminal_view.setStyleSheet("background-color: black; color: green;")
        self.terminal_view.setPlaceholderText("Python instance terminal view...")
        main_layout.addWidget(self.terminal_view)

        # **Store `side_layout` as an instance variable**
        self.side_layout = QVBoxLayout()

        # CPU info initializer _________________________________________________________________________________________________
        self.cpu_info_view = QTextEdit()
        self.cpu_info_view.setReadOnly(True)
        self.cpu_info_view.setStyleSheet("background-color: lightgray; color: black;")
        self.cpu_info_view.setFixedHeight(50)
        self.cpu_info_view.setText(f"Number of CPUs: {os.cpu_count()}")
        self.side_layout.addWidget(self.cpu_info_view)

        # Filie instance initializer ___________________________________________________________________________________________
        self.FeatureFiles = FileManagerWidget("Feature Scripts", self.terminal_view)
        self.side_layout.addWidget(self.FeatureFiles)

        self.CleaningFiles = FileManagerWidget("Cleaning Scripts", self.terminal_view)
        self.side_layout.addWidget(self.CleaningFiles)
        
        self.RoutingFiles = FileManagerWidget("Routing Scripts", self.terminal_view)
        self.side_layout.addWidget(self.RoutingFiles)

        main_layout.addLayout(self.side_layout)

        # Swap initializer ____________________________________________________________________________________________________
        self.swap_button = QPushButton("Beguin")
        self.swap_button.clicked.connect(self.SwapStage3)
        self.side_layout.addWidget(self.swap_button)  # Corrected placement

        # Set central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        
    def SwapStage2(self):
        """Hides all widgets except the terminal view"""
        self.graph_widget.show()
        self.GraphButton.show()
        for i in range(self.side_layout.count()):
            widget = self.side_layout.itemAt(i).widget()
            if widget:
                widget.setVisible(not widget.isVisible())  # Toggle visibility
        print(self.FeatureFiles.file_functions)
        self.Procescess()

    def SwapStage3(self):
        """Hides all widgets except the terminal view"""
        print("\n\n\n")
        print(self.RoutingFiles.user_file_functions)
        print(self.RoutingFiles.file_functions)
        print("\n\n\n")


        print(self.CleaningFiles.user_file_functions)
        print(self.CleaningFiles.file_functions)
        print("\n\n\n")
        print(self.FeatureFiles.user_file_functions)
        print(self.FeatureFiles.file_functions)

        self.graph_widget.show()
        self.GraphButton.show()
        for i in range(self.side_layout.count()):
            widget = self.side_layout.itemAt(i).widget()
            if widget:
                widget.setVisible(not widget.isVisible())  # Toggle visibility
        print(self.FeatureFiles.file_functions)

    def toggle_graph(self):
        # Check current visibility and toggle accordingly
        if self.graph_widget.isVisible():
            self.graph_widget.hide()
            self.GraphButton.setText("Show Graph")
        else:
            self.graph_widget.show()
            self.GraphButton.setText("Hide Graph")
    def Procescess(self):
        manager = multiprocessing.Manager()
        buffer = manager.list()  # Shared buffer
        result_queue = multiprocessing.Queue()
        lock = multiprocessing.Lock()
        flag = multiprocessing.Value('i', 0)  # Shared flag (starts with process 0)

        # Create processes
        processor_1 = UniqueFunctionProcessor(
            process_id=0,
            buffer=buffer,
            lock=lock,
            flag=flag,
            result_queue=result_queue
        )
        processor_2 = UniqueFunctionProcessor(
            process_id=1,
            buffer=buffer,
            lock=lock,
            flag=flag,
            result_queue=result_queue
        )
        echo = Echo(buffer=buffer, lock=lock, flag=flag)
        processes = [processor_1,processor_2, echo]
        try:
        # Start all processes
            for process in processes:
                process.start()

            # Wait for all processes to finish
            for process in processes:
                process.join()

        except KeyboardInterrupt:
            print("\nKeyboardInterrupt detected! Reclaiming resources...")
            self.cleanup_processes(processes)

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            self.cleanup_processes(processes)
        finally:
            # Display remaining buffer state and results
            print("Final buffer state:", list(buffer))
        while not result_queue.empty():
            process_id, result = result_queue.get()
            print(f"Result from Process {process_id}: {result}")
        print("Program terminated gracefully.")
    def cleanup_processes(self):
        """
        Terminates all active processes and ensures proper cleanup.
        """
        print("\nInitiating cleanup of processes...")
        for process in self.processes:
            if process.is_alive():
                process.terminate()
                process.join()
        print("All processes have been terminated successfully.")
        



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WindowManager()
    window.show()
    sys.exit(app.exec_())