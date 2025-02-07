import sys
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QComboBox, QTextEdit, QPushButton, QFileDialog, QVBoxLayout, QWidget, QSpinBox, QHBoxLayout, QMessageBox
from  request_handler import RequestHandler
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Whisper Application")
        self.setGeometry(100, 100, 600, 400)

        main_layout = QVBoxLayout()
    

        # Language
        language_layout = QHBoxLayout()
        self.language_label = QLabel("Language used in recordings (leave blank for autodetection):")
        self.language_dropdown = QComboBox()
        self.language_dropdown.addItems(["Autodetect","English", "Spanish", "French", "German", "Chinese"])
        language_layout.addWidget(self.language_label)
        language_layout.addWidget(self.language_dropdown)
        main_layout.addLayout(language_layout)

        # Task
        task_layout = QHBoxLayout()
        self.task_label = QLabel("Select whether to transcribe or translate(english only):")
        self.task_dropdown = QComboBox()
        self.task_dropdown.addItems(["transcribe", "translate"])
        task_layout.addWidget(self.task_label)
        task_layout.addWidget(self.task_dropdown)
        main_layout.addLayout(task_layout)

        # Model
        model_layout = QHBoxLayout()
        self.model_label = QLabel("Model type:")
        self.model_dropdown = QComboBox()
        self.model_dropdown.addItems(["large-v2", "large-v3"])
        model_layout.addWidget(self.model_label)
        model_layout.addWidget(self.model_dropdown)
        main_layout.addLayout(model_layout)

        # Initial Prompt
        self.prompt_label = QLabel("Initial Prompt if any (max 80 words):")
        self.prompt_input = QTextEdit()
        self.prompt_input.setMaximumHeight(100)
        main_layout.addWidget(self.prompt_label)
        main_layout.addWidget(self.prompt_input)

        # Select Input File
        self.input_file_button = QPushButton("Select Input Files")
        self.input_file_button.clicked.connect(self.select_input_files)
        main_layout.addWidget(self.input_file_button)

        self.input_file_label = QLabel("No files selected")
        main_layout.addWidget(self.input_file_label)

        # Select Output Folder
        self.output_folder_button = QPushButton("Select Output Folder")
        self.output_folder_button.clicked.connect(self.select_output_folder)
        main_layout.addWidget(self.output_folder_button)

        self.output_folder_label = QLabel("No folder selected")
        main_layout.addWidget(self.output_folder_label)

        # OK and Cancel Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Submit")
        self.ok_button.clicked.connect(self.submit_form)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def select_input_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Input Files", "", "Audio/Video Files (*.mp3 *.mp4 *.mpeg *.mpga *.m4a *.wav *.webm *.wma)")
        if files:
            self.input_files = files
            self.input_file_label.setText(f"{len(self.input_files)} files selected")
        else:
            self.input_file_label.setText("No files selected")

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder = folder
            self.output_folder_label.setText(self.output_folder)
        else:
            self.output_folder_label.setText("No folder selected")

    def submit_form(self):

        language = self.language_dropdown.currentText()
        task = self.task_dropdown.currentText()
        model = self.model_dropdown.currentText()
        diarize = False
        initial_prompt = self.prompt_input.toPlainText()
        input_files = getattr(self, 'input_files', [])
        output_folder = getattr(self, 'output_folder', '')

        # Call the whisper function with collected data
        RequestHandler().router(language, task, model, diarize, initial_prompt, input_files, output_folder)

        # Show pop-up message
        QMessageBox.information(self, "Submission", "Your job has been submitted")

        # Clear input fields
        self.language_dropdown.setCurrentIndex(0)
        self.task_dropdown.setCurrentIndex(0)
        self.model_dropdown.setCurrentIndex(0)
        self.prompt_input.clear()
        self.input_files = []
        self.input_file_label.setText("No files selected")
        self.output_folder = ''
        self.output_folder_label.setText("No folder selected")

    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())