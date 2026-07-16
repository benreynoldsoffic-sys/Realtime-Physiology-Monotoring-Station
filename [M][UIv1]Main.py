import os
import ast
import sys
import time
import numpy as np
import random
import importlib.util
import multiprocessing
import matplotlib.pyplot as plt

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QWidget, QTextEdit, QPushButton, QMessageBox, QLabel, QListWidget, QFileDialog
)
from PyQt5.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class UniqueFunctionProcessor(multiprocessing.Process):
    """
    A process class that processes data from a buffer repeatedly, using a token-passing system.
    """
    def __init__(self, process_id, buffer, lock, flag, result_queue):
        super().__init__()
        self.process_id = process_id  # Unique ID for this process
        self.buffer = buffer  # Shared buffer
        self.lock = lock  # Mutex lock
        self.flag = flag  # Shared flag to control lock ownership
        self.result_queue = result_queue

    def run(self):
        while True:
            with self.lock:
                # Only proceed if it's this process's turn
                if self.flag.value == self.process_id:
                    if not self.buffer:
                        print(f"Process {self.process_id}: Buffer is empty. Exiting...")
                        break

                    # Consume a data chunk from the buffer
                    data_chunk = self.buffer.pop(0)
                    print(f"Process {self.process_id}: Processing data chunk: {data_chunk}")
                    
                    # Simulate processing and generate a result
                    result = sum(data_chunk)  # Example: Summing the chunk
                    self.result_queue.put((self.process_id, result))
                    print(f"Process {self.process_id}: Processed data chunk. Result: {result}")

                    # Pass control to the next process
                    self.flag.value = ((self.flag.value + 1) % 2)  # Assume 2 processes for simplicity
                    print(f"Set flag to {self.flag.value}")

            time.sleep(1)  # Simulate some delay to avoid tight loops


class Echo(multiprocessing.Process):
    """
    A process class responsible for adding new data to the buffer.
    """
    def __init__(self, buffer, lock, flag):
        super().__init__()
        self.buffer = buffer
        self.lock = lock
        self.flag = flag
    def run(self):
        while True:
            with self.lock:
                if len(self.buffer) < 10:  # Prevent buffer overflow
                    new_data = [random.randint(1, 20) for _ in range(3)]
                    print(f"Echo: Adding new data to buffer: {new_data}")
                    self.buffer.append(new_data)
                    self.flag.value = ((self.flag.value + 1) % 2)
                    print(f"Set flag to {self.flag.value}")
            time.sleep(1)  # Simulate delay between additions

class FileManagerWidget(QWidget):
    """Enhanced File Manager Component with Function Extraction"""
    def __init__(self, title, terminal_view):
        super().__init__()
        self.title = title
        self.terminal_view = terminal_view
        self.file_functions = {}  # Store file-function associations

        # Layout setup
        layout = QVBoxLayout()

        # Section label
        self.label = QLabel(self.title)
        layout.addWidget(self.label)

        # File list
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.display_functions)
        layout.addWidget(self.file_list)

        # Function list
        self.function_list = QListWidget()  # Display extracted functions
        self.function_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.function_list)

        # Add File Button
        self.add_file_button = QPushButton(f"Add {self.title}")
        self.add_file_button.clicked.connect(self.add_file)
        layout.addWidget(self.add_file_button)

        # Save Function Mapping Button
        self.save_button = QPushButton("Save Function Mapping")
        self.save_button.clicked.connect(self.save_mapping)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def add_file(self):
        """Select a file and extract its functions"""
        file_path, _ = QFileDialog.getOpenFileName(self, f"Select {self.title}")
        if file_path:
            functions = self.extract_functions(file_path)
            if functions is not None:
                # Prevent duplicates in file list
                if not self.file_list.findItems(file_path, Qt.MatchExactly):
                    self.file_list.addItem(file_path)
                    self.file_functions[file_path] = functions  # Initially store all extracted functions
                    self.function_list.clear()
                    self.function_list.addItems(functions)
                    self.terminal_view.append(f"[{self.title}_Added] {file_path}")
                else:
                    self.terminal_view.append(f"[File_Error] {self.title} Already included\n")
            else:
                self.terminal_view.append(f"\tNo Functions Found\n\tNo functions found in {file_path}")

    def display_functions(self, item):
        """Display functions associated with the selected file"""
        file_path = item.text()
        # If a mapping has already been saved, display only the saved functions,
        # otherwise show all extracted functions.
        associated_functions = self.file_functions.get(file_path, [])
        self.function_list.clear()
        if associated_functions:
            self.function_list.addItems(associated_functions)
        else:
            functions = self.extract_functions(file_path)
            self.function_list.addItems(functions)

    def save_mapping(self):
        """Save selected functions to the file mapping"""
        current_item = self.file_list.currentItem()
        if current_item:
            file_path = current_item.text()
            selected_functions = [item.text() for item in self.function_list.selectedItems()]
            # Update the mapping with the user-selected functions.
            self.file_functions[file_path] = selected_functions
            self.terminal_view.append(f"[Mapping Saved] {file_path} -> {selected_functions}")
        else:
            self.terminal_view.append(f"\tWarning\n\tNo {self.title} selected to save mapping!")
            
    @staticmethod
    def extract_functions(file_path):
        """Extract function names from the given Python file"""
        try:
            with open(file_path, "r") as file:
                tree = ast.parse(file.read())
            return [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        except Exception as e:
            return []

class DynamicGraphWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set up the widget layout
        self.layout = QVBoxLayout(self)
        
        # Set up Matplotlib figure and canvas
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        # Container to hold our data
        self.data = []

        # Create and start a QTimer for live updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_graph)
        self.timer.start(1000)  # Update every second

    def update_graph(self):
        # Simulate adding a new random value to the data array
        self.data.append(np.random.randint(0, 100))  # Random value between 0 and 100

        # Keep only the last 10 data points
        recent_data = self.data[-10:]
        
        # Clear the axis and plot the recent data
        self.ax.clear()
        self.ax.plot(recent_data, marker='o', label="Recent 10 Points")
        self.ax.legend()

        # Dynamically adjust y-axis based on the range of recent_data
        if recent_data:
            self.ax.set_ylim(min(recent_data) - 5, max(recent_data) + 5)

        # Redraw the canvas
        self.canvas.draw()
        
class MainWindow(QMainWindow):
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

    def SwapStage3(self):
        """Hides all widgets except the terminal view"""
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
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())