import unittest
from unittest.mock import patch, MagicMock
from request_handler import RequestHandler
import subprocess

class TestRequestHandler(unittest.TestCase):

    @patch('whisper_gui.request_handler.subprocess.run')
    @patch('whisper_gui.request_handler.logger')
    def setUp(self, mock_logger, mock_subprocess):
        self.handler = RequestHandler()
        self.mock_subprocess = mock_subprocess
        self.mock_logger = mock_logger

    def test_initialization(self):
        self.assertEqual(self.handler.language, 'auto')
        self.assertEqual(self.handler.task, 'transcribe')
        self.assertEqual(self.handler.model, "/app/models/ggml-large-v2.bin")
        self.assertIsNone(self.handler.initial_prompt)
        self.assertEqual(self.handler.input_files, [])
        self.assertIsNone(self.handler.output_folder)
        self.assertEqual(self.handler.whoami, "jayan-sens")
        self.assertIn(self.handler.cluster, ["Local", "Rackham", "Snowy", "Bianca"])
        self.mock_logger.info.assert_called_once()

    @patch('whisper_gui.request_handler.Path.exists', return_value=False)
    @patch('whisper_gui.request_handler.os.mkdir')
    @patch('whisper_gui.request_handler.SlurmTemplate.submit')
    def test_submit_slurm_job(self, mock_submit, mock_mkdir, mock_path_exists):
        self.handler.input_files = ["/path/to/audio1.wav", "/path/to/audio2.wav"]
        self.mock_subprocess.return_value.stdout = "3600"
        self.handler._submit_slurm_job()
        mock_mkdir.assert_called_once()
        mock_submit.assert_called_once()

    @patch('whisper_gui.request_handler.subprocess.run')
    def test_submit_local_job(self, mock_subprocess):
        self.handler.input_files = ["/path/to/audio.mp4"]
        self.handler._run_whispercpp = MagicMock(return_value=b"audio data")
        self.handler._submit_local_job()
        self.handler._run_whispercpp.assert_called()

    @patch('whisper_gui.request_handler.subprocess.run')
    def test_run_whispercpp(self, mock_subprocess):
        mock_subprocess.return_value.stdout = "output"
        result = self.handler._run_whispercpp(mode="transcribe", input_file="/path/to/audio.wav", output_folder="/output", model_path="/model", use_gpu=True)
        self.assertEqual(result, "output")

    @patch('whisper_gui.request_handler.subprocess.run')
    def test_run_whispercpp_error(self, mock_subprocess):
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, 'cmd', stderr="error")
        result = self.handler._run_whispercpp(mode="transcribe", input_file="/path/to/audio.wav", output_folder="/output", model_path="/model", use_gpu=True)
        self.assertIsNone(result)

    @patch('whisper_gui.request_handler.RequestHandler._submit_slurm_job')
    @patch('whisper_gui.request_handler.RequestHandler._submit_local_job')
    def test_router(self, mock_submit_local_job, mock_submit_slurm_job):
        self.handler.router(language="English", task="transcribe", model="/model", diarize=False, initial_prompt=None, input_files=["/path/to/audio.wav"], output_folder="/output")
        if self.handler.cluster in ["Rackham", "Snowy", "Bianca"]:
            mock_submit_slurm_job.assert_called_once()
        else:
            mock_submit_local_job.assert_called_once()

if __name__ == '__main__':
    unittest.main()