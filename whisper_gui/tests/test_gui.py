import sys
import unittest
from PyQt6.QtWidgets import QApplication
from whisper_gui.gui import MainWindow

class TestMainWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

    def setUp(self):
        self.window = MainWindow()

    def test_initial_ui_state(self):
        self.assertEqual(self.window.language_dropdown.currentText(), "Autodetect")
        self.assertEqual(self.window.task_dropdown.currentText(), "transcribe")
        self.assertEqual(self.window.model_dropdown.currentText(), "large-v2")
        self.assertEqual(self.window.prompt_input.toPlainText(), "")
        self.assertEqual(self.window.input_file_label.text(), "No files selected")
        self.assertEqual(self.window.output_folder_label.text(), "No folder selected")

    def test_select_input_files(self):
        # Simulate selecting input files
        self.window.input_files = ["file1.mp3", "file2.wav"]
        self.window.input_file_label.setText(f"{len(self.window.input_files)} files selected")
        self.assertEqual(self.window.input_file_label.text(), "2 files selected")

    def test_select_output_folder(self):
        # Simulate selecting output folder
        self.window.output_folder = "/path/to/output"
        self.window.output_folder_label.setText(self.window.output_folder)
        self.assertEqual(self.window.output_folder_label.text(), "/path/to/output")

    def test_submit_form(self):
        # Simulate form submission
        self.window.language_dropdown.setCurrentText("English")
        self.window.task_dropdown.setCurrentText("translate")
        self.window.model_dropdown.setCurrentText("large-v3")
        self.window.prompt_input.setPlainText("Test prompt")
        self.window.input_files = ["file1.mp3"]
        self.window.output_folder = "/path/to/output"

        self.window.submit_form()

        self.assertEqual(self.window.language_dropdown.currentText(), "Autodetect")
        self.assertEqual(self.window.task_dropdown.currentText(), "transcribe")
        self.assertEqual(self.window.model_dropdown.currentText(), "large-v2")
        self.assertEqual(self.window.prompt_input.toPlainText(), "")
        self.assertEqual(self.window.input_file_label.text(), "No files selected")
        self.assertEqual(self.window.output_folder_label.text(), "No folder selected")

if __name__ == "__main__":
    unittest.main()