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


class ProcessingManeger:
    """
    This class encapsulates all process-related operations.
    It uses shared resources (via multiprocessing.Manager) to set up and run processes,
    and it takes care of cleaning up in case of errors or interrupts.
    """
    def __init__(self):
        self.processes = []
        self.manager = None
        self.buffer = None
        self.result_queue = None
        self.lock = None
        self.flag = None
        print("ProcessingManeger initialized")

    def setup_processes(self):
        """Set up shared resources and instantiate your processes."""
        self.manager = multiprocessing.Manager()
        self.buffer = self.manager.list()  # shared buffer for inter-process communication
        self.result_queue = multiprocessing.Queue()
        self.lock = multiprocessing.Lock()
        self.flag = multiprocessing.Value('i', 0)  # shared flag

        # Create process instances using classes imported from M_UIv2_Supp
        processor_1 = UniqueFunctionProcessor(
            process_id=0,
            buffer=self.buffer,
            lock=self.lock,
            flag=self.flag,
            result_queue=self.result_queue
        )
        processor_2 = UniqueFunctionProcessor(
            process_id=1,
            buffer=self.buffer,
            lock=self.lock,
            flag=self.flag,
            result_queue=self.result_queue
        )
        echo = Echo(
            buffer=self.buffer,
            lock=self.lock,
            flag=self.flag
        )
        self.processes = [processor_1, processor_2, echo]

    def run_processes(self):
        """Start and join all processes, handling errors independently of the UI."""
        self.setup_processes()
        try:
            # Start each process
            for process in self.processes:
                process.start()

            # Wait for the processes to finish
            for process in self.processes:
                process.join()

        except KeyboardInterrupt:
            print("\nKeyboardInterrupt detected! Cleaning up processes...")
            self.cleanup_processes()

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            self.cleanup_processes()

        finally:
            # Show the final state of the shared buffer
            print("Final buffer state:", list(self.buffer))

        # Process any remaining results
        while not self.result_queue.empty():
            process_id, result = self.result_queue.get()
            print(f"Result from Process {process_id}: {result}")

        print("Processing completed gracefully.")

    def cleanup_processes(self):
        """
        Terminates all running processes and ensures proper cleanup.
        This helps keep your main window safe from process termination glitches.
        """
        print("\nInitiating cleanup of processes...")
        for process in self.processes:
            if process.is_alive():
                process.terminate()
                process.join()
        print("All processes have been terminated successfully.")
        
    @staticmethod
    def check_process_running(process_name):
        """
        Check if a process with the given name is running.
        Useful for verifying that no rogue processes are still active.
        """
        import psutil
        for proc in psutil.process_iter(attrs=["name"]):
            if proc.info["name"].lower() == process_name.lower():
                return True
        return False


class Support:
    """
    A helper class that provides utilitarian functions used throughout
    the application. This can include logging, configuration reading, and
    other miscellaneous tasks.
    """
    def __init__(self):
        self.log_file = "support_log.txt"
        self.log("Support initialized.", level="DEBUG")

    def log(self, message, level="INFO"):
        """
        Logs a message with a timestamp and a severity level.
        This can help you trace errors or events later on.
        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        with open(self.log_file, "a") as log_file:
            log_file.write(log_message + "\n")
        print(log_message)

    @staticmethod
    def read_config(file_path):
        """
        Reads and parses a configuration file.
        Supports files containing a dictionary literal.
        """
        if not os.path.exists(file_path):
            print(f"Configuration file {file_path} not found.")
            return None
        try:
            with open(file_path, 'r') as f:
                data = f.read()
                config = ast.literal_eval(data)
            return config
        except Exception as e:
            print(f"Error reading configuration: {e}")
            return None


class WindowManager(QMainWindow):
    """
    The main window class handles UI elements.
    All process manipulation has been offloaded to the ProcessingManeger,
    so issues arising in the main UI are less likely to disrupt critical backend functionality.
    """
    def __init__(self):
        super().__init__()

        # Main window settings
        self.setWindowTitle("Realtime Feature Exstraction Manager")
        self.resize(1000, 400)
        # Create an instance of the processing manager
        self.processing_manager = ProcessingManeger()
        # Main layout container
        main_layout = QHBoxLayout()

        # Layout for the main window's content
        self.layout = QVBoxLayout(self)

        # Initialize the dynamic graph widget (hidden by default)
        self.graph_widget = DynamicGraphWidget()
        main_layout.addWidget(self.graph_widget)
        self.graph_widget.hide()

        # Button to toggle dynamic graph visibility
        self.GraphButton = QPushButton("Hide Graph")
        self.GraphButton.clicked.connect(self.toggle_graph)
        main_layout.addWidget(self.GraphButton, alignment=Qt.AlignBottom | Qt.AlignRight)
        self.GraphButton.hide()

        # Terminal view configuration
        self.terminal_view = QTextEdit()
        self.terminal_view.setReadOnly(True)
        self.terminal_view.setStyleSheet("background-color: black; color: green;")
        self.terminal_view.setPlaceholderText("Python instance terminal view...")
        main_layout.addWidget(self.terminal_view)

        # Side layout holds CPU info and file managers
        self.side_layout = QVBoxLayout()

        # CPU info widget
        self.cpu_info_view = QTextEdit()
        self.cpu_info_view.setReadOnly(True)
        self.cpu_info_view.setStyleSheet("background-color: lightgray; color: black;")
        self.cpu_info_view.setFixedHeight(50)
        self.cpu_info_view.setText(f"Number of CPUs: {os.cpu_count()}")
        self.side_layout.addWidget(self.cpu_info_view)

        # File management widgets
        self.FeatureFiles = FileManagerWidget("Feature Scripts", self.terminal_view)
        self.side_layout.addWidget(self.FeatureFiles)
        self.CleaningFiles = FileManagerWidget("Cleaning Scripts", self.terminal_view)
        self.side_layout.addWidget(self.CleaningFiles)
        self.RoutingFiles = FileManagerWidget("Routing Scripts", self.terminal_view)
        self.side_layout.addWidget(self.RoutingFiles)

        main_layout.addLayout(self.side_layout)

        # Swap button to toggle visibility of UI components
        self.swap_button = QPushButton("Begin")
        self.swap_button.clicked.connect(self.SwapStage3)
        self.side_layout.addWidget(self.swap_button)

        # A dedicated button to initiate process management
        self.process_button = QPushButton("Start Processing")
        self.process_button.clicked.connect(self.start_processing)
        self.side_layout.addWidget(self.process_button)

        # Set the main container widget for the window
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def SwapStage2(self):
        """Toggle visibility for side widgets while ensuring the graph remains visible."""
        self.graph_widget.show()
        self.GraphButton.show()
        for i in range(self.side_layout.count()):
            widget = self.side_layout.itemAt(i).widget()
            if widget:
                widget.setVisible(not widget.isVisible())
        print(self.FeatureFiles.file_functions)

    def SwapStage3(self):
        """Toggle visibility for side widgets while ensuring the graph remains visible."""
        self.graph_widget.show()
        self.GraphButton.show()
        for i in range(self.side_layout.count()):
            widget = self.side_layout.itemAt(i).widget()
            if widget:
                widget.setVisible(not widget.isVisible())
        print(self.FeatureFiles.file_functions)

    def toggle_graph(self):
        """
        Check the current visibility of the graph widget and toggle it.
        Updates the GraphButton text accordingly.
        """
        if self.graph_widget.isVisible():
            self.graph_widget.hide()
            self.GraphButton.setText("Show Graph")
        else:
            self.graph_widget.show()
            self.GraphButton.setText("Hide Graph")

    def start_processing(self):
        """
        Trigger the process management.
        This delegates the process manipulation to the ProcessingManeger,
        keeping the main window logic as lean as possible.
        """
        self.processing_manager.run_processes()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WindowManager()
    window.show()
    sys.exit(app.exec_())