import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QComboBox, QTextEdit, QPushButton, QFileDialog, QVBoxLayout, QWidget, QSpinBox, QHBoxLayout, QMessageBox

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Whisper Application")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        # Audio Length
        self.audio_length_label = QLabel("Total Audio Length in hrs (rounded up):")
        self.audio_length_input = QSpinBox()
        self.audio_length_input.setRange(1, 50)
        layout.addWidget(self.audio_length_label)
        layout.addWidget(self.audio_length_input)

        # Language
        self.language_label = QLabel("Language used in recordings (leave blank for autodetection):")
        self.language_dropdown = QComboBox()
        self.language_dropdown.addItems(["Autodetect","English", "Spanish", "French", "German", "Chinese"])
        layout.addWidget(self.language_label)
        layout.addWidget(self.language_dropdown)

        # Task
        self.task_label = QLabel("Select whether to transcribe or translate(english only):")
        self.task_dropdown = QComboBox()
        self.task_dropdown.addItems(["transcribe", "translate"])
        layout.addWidget(self.task_label)
        layout.addWidget(self.task_dropdown)

        # Model
        self.model_label = QLabel("Model type:")
        self.model_dropdown = QComboBox()
        self.model_dropdown.addItems(["large-v2", "large-v3"])
        layout.addWidget(self.model_label)
        layout.addWidget(self.model_dropdown)

        # Initial Prompt
        self.prompt_label = QLabel("Initial Prompt if any (max 80 words):")
        self.prompt_input = QTextEdit()
        self.prompt_input.setMaximumHeight(100)
        layout.addWidget(self.prompt_label)
        layout.addWidget(self.prompt_input)

        # Select Input File
        self.input_file_button = QPushButton("Select Input Files")
        self.input_file_button.clicked.connect(self.select_input_files)
        layout.addWidget(self.input_file_button)

        # Select Output Folder
        self.output_folder_button = QPushButton("Select Output Folder")
        self.output_folder_button.clicked.connect(self.select_output_folder)
        layout.addWidget(self.output_folder_button)

        # OK and Cancel Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Submit")
        self.ok_button.clicked.connect(self.submit_form)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def select_input_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Input Files", "", "Audio/Video Files (*.mp3 *.mp4 *.mpeg *.mpga *.m4a *.wav *.webm *.wma)")
        if files:
            self.input_files = files

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder = folder

    def submit_form(self):
        audio_length = self.audio_length_input.value()
        language = self.language_dropdown.currentText()
        task = self.task_dropdown.currentText()
        model = self.model_dropdown.currentText()
        initial_prompt = self.prompt_input.toPlainText()
        input_files = getattr(self, 'input_files', [])
        output_folder = getattr(self, 'output_folder', '')

        # Call the foobar function with collected data
        self.foobar(audio_length, language, task, model, initial_prompt, input_files, output_folder)

        # Show pop-up message
        QMessageBox.information(self, "Submission", "Your job has been submitted")

        # Clear input fields
        self.audio_length_input.setValue(1)
        self.language_dropdown.setCurrentIndex(0)
        self.task_dropdown.setCurrentIndex(0)
        self.model_dropdown.setCurrentIndex(0)
        self.prompt_input.clear()
        self.input_files = []
        self.output_folder = ''


    def foobar(self, audio_length, language, task, model, initial_prompt, input_files, output_folder):
        # Implement the foobar function logic here
        print(f"Audio Length: {audio_length}")
        print(f"Language: {language}")
        print(f"Task: {task}")
        print(f"Model: {model}")
        print(f"Initial Prompt: {initial_prompt}")
        print(f"Input Files: {input_files}")
        print(f"Output Folder: {output_folder}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())