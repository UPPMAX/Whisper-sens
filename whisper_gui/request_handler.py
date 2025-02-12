# How to run Whispercpp script:
# FFMPEG : Whispercpp --ffmpeg /home/jayan/Downloads/Zoom_sample.mp4 /home/jayan/Downloads/Zoom_sample.wav
# FFPROBE : Whispercpp --ffprobe /home/jayan/Downloads/Zoom_sample.mp4
# Without GPU : Whispercpp -m /app/models/ggml-large-v2.bin -t 20 -f /home/jayan/Downloads/Zoom_sample.wav
# With GPU : Whispercpp --gpu -m /app/models/ggml-large-v2.bin -f /home/jayan/Downloads/Zoom_sample.wav

import subprocess
import io
import os
import logging
from slurm_template import SlurmTemplate
from pathlib import Path
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)

class RequestHandler:
    def __init__(self):
        self.language = 'auto'
        self.task = 'transcribe'
        self.model_path = "/app/models/ggml-large-v2.bin"
        self.initial_prompt = None
        self.input_files = []
        self.output_folder = None

        self.cluster = os.environ.get("CLUSTER") or "Local"
        self.whoami = subprocess.run("whoami", shell=True,capture_output=True, text=True).stdout.strip()
        logger.info(f"RequestHandler initialized for project: {self.whoami}")

    def _submit_slurm_job(self, mode=None, diarize=None, input_file=None, output_folder=None, model_path=None, use_gpu=False, threads=16):
        """For running on compute node"""

        if self.cluster in ["rackham", "snowy"]:
            script_dir = Path(f"/home/{self.whoami}/Desktop/Whisper_logs")
        elif self.cluster == "bianca":
            script_dir = Path(f"/home/{self.whoami}/Desktop/proj/Whisper_logs")

        print(script_dir)

        try:
            if not script_dir.exists():
                print("Creating Whisper_logs directory")
                script_dir.mkdir(parents=True, exist_ok=True)

            # subprocess.run(["module load FFmpeg"], shell=True, capture_output=True)

            audio_duration = 0.0
            for audio_path in self.input_files:
                print(audio_path)
                # result = subprocess.run([f"ffprobe", "-i" , audio_path, "-show_entries", "format=duration", "-v" "quiet", "-of", "csv='p=0'"], shell=True, capture_output=True, text=True)
                duration_str = subprocess.run([f"ffprobe -i {audio_path} -show_entries format=duration -v quiet -of csv='p=0'"], shell=True, capture_output=True, text=True).stdout.strip()
                if duration_str:
                    audio_duration += float(duration_str)
                else :
                    logger.error("Error occurred in ffprobe while processing {audio_path}")
                    exit(1)
            audio_duration = int(max((audio_duration//3600) + 1, 1)) # Minimum 1 hr 
            print(f"Audio duration: {audio_duration} hrs")

            if audio_duration > 120:
                logger.error("Audio duration exceeds 120 hrs (5 days)")
                exit(1)
            # subprocess.run(["module unload FFmpeg"], shell=True)
            
            command = self._run_whispercpp(mode="transcribe", input_file=audio_path, output_folder=output_folder, model_path=model_path, use_gpu=False, threads=16)

            slurm = SlurmTemplate(job_time=f"{audio_duration}:00", 
                                whisper_module="Whispercpp", 
                                commands=command,
                                whoami=self.whoami,
                                script_dir=script_dir)
            
            slurm.submit()

        except Exception as e:
            logger.exception("Error occurred in either ffprobe or submitting slurm job: ", e)

        return None

    def _submit_local_job(self, mode=None, diarize=None, output_folder=None, model_path=None, use_gpu=False, threads=16):
        """For running on login node"""
        
        for audio_path in self.input_files:  
            if diarize:
                pass
            else:
                if audio_path.endswith((".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".webm", ".wma")):
                    wav_output = self._run_whispercpp(mode="ffmpeg", input_file=audio_path)
                    with io.BytesIO(wav_output) as audio_stream:
                        # self._run_whispercpp(mode="transcribe", input_file=audio_stream, output_folder=output_folder, model_path=model_path, use_gpu=False, threads=16)
                        command = self._run_whispercpp(mode="transcribe", input_file=audio_stream, output_folder=output_folder, model_path=model_path, use_gpu=False, threads=16)
                elif audio_path.endswith(".wav"):
                    command = self._run_whispercpp(mode="transcribe", input_file=audio_path, output_folder=output_folder, model_path=model_path, use_gpu=False, threads=16)
                else:
                    print("Invalid file format")
                
                try:
                    result = subprocess.run(command, check=True, capture_output=True, text=True)
                    print("Command output:", result.stdout)
                    return result.stdout
                except subprocess.CalledProcessError as e:
                    print("Error occurred:", e.stderr)
                    return None

        return None


    def _run_whispercpp(self, mode=None, input_file=None, output_folder=None, model_path=None, use_gpu=False, threads=16):
        """For running on login node"""
        command = ["Whispercpp"]

        if mode == "ffmpeg":
            command.extend(["--ffmpeg", input_file, 'audio_file.wav'])
        elif mode == "ffprobe":
            command.extend(["--ffprobe", input_file])
        elif mode == "transcribe":
            if use_gpu:
                command.append("--gpu")
            else:
                command.extend(["-t", str(threads)])
            if self.task == "translate":
                command.append("--translate")

            command.extend(["-m", self.model_path, "--language", self.language , "-f", input_file, "--output-file", output_folder])

        else:
            raise ValueError("Invalid mode specified")

        return command
        # try:
        #     result = subprocess.run(command, check=True, capture_output=True, text=True)
        #     print("Command output:", result.stdout)
        #     return result.stdout
        # except subprocess.CalledProcessError as e:
        #     print("Error occurred:", e.stderr)
        #     return None
        
    def _run_whisperx(self, mode, input_file, model_path=None, use_gpu=False, threads=1):
        pass

    def router(self, language, task, model, diarize, initial_prompt, input_files, output_folder):
        
        print(f"Language: {language}")
        if language != "Autodetect":
            self.language = language
        print(f"Task: {task}")
        self.task = task or self.task
        print(f"Model: {model}")
        self.model_path = model or self.model_path
        print(f"Diarize: {diarize}")
        print(f"Initial Prompt: {initial_prompt}")
        print(f"Input Files: {input_files}")
        self.input_files = input_files
        print(f"Output Folder: {output_folder}")
        self.output_folder = output_folder
        print(f"Cluster: {self.cluster}")
        print(f"Whoami: {self.whoami}")

        if self.cluster in ["rackham", "snowy", "bianca"]:
            self._submit_slurm_job(diarize=False)
        elif self.cluster == "Local": 
            self._submit_local_job(diarize=False)

        
        return  None

# # Example usage
# if __name__ == "__main__":
#     handler = RequestHandler()
#     # Example: Run ffmpeg mode
#     handler.run_whispercpp("ffmpeg", "/home/jayan/Downloads/Zoom_sample.mp4", "/home/jayan/Downloads/Zoom_sample.wav")
#     # Example: Run ffprobe mode
#     handler.run_whispercpp("ffprobe", "/home/jayan/Downloads/Zoom_sample.mp4")
#     # Example: Run transcribe mode without GPU
#     handler.run_whispercpp("transcribe", "/home/jayan/Downloads/Zoom_sample.wav", model_path="/app/models/ggml-large-v2.bin", threads=20)
#     # Example: Run transcribe mode with GPU
#     handler.run_whispercpp("transcribe", "/home/jayan/Downloads/Zoom_sample.wav", model_path="/app/models/ggml-large-v2.bin", use_gpu=True)
