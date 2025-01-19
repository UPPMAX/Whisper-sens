# How to run Whispercpp script:
# FFMPEG : Whispercpp --ffmpeg /home/jayan/Downloads/Zoom_sample.mp4 /home/jayan/Downloads/Zoom_sample.wav
# FFPROBE : Whispercpp --ffprobe /home/jayan/Downloads/Zoom_sample.mp4
# Without GPU : Whispercpp -m /app/models/ggml-large-v2.bin -t 20 -f /home/jayan/Downloads/Zoom_sample.wav
# With GPU : Whispercpp --gpu -m /app/models/ggml-large-v2.bin -f /home/jayan/Downloads/Zoom_sample.wav

import subprocess

class RequestHandler:
    def __init__(self):
        self.audio_length = None
        self.language = None
        self.task = None
        self.model = None
        self.initial_prompt = None
        self.input_files = []
        self.output_folder = None

    def run_whispercpp(self, mode, input_file, output_file=None, model_path=None, use_gpu=False, threads=1):
        command = ["Whispercpp"]

        if mode == "ffmpeg":
            command.extend(["--ffmpeg", input_file, output_file])
        elif mode == "ffprobe":
            command.extend(["--ffprobe", input_file])
        elif mode == "transcribe":
            if use_gpu:
                command.append("--gpu")
            if model_path:
                command.extend(["-m", model_path])
            command.extend(["-t", str(threads), "-f", input_file])
        else:
            raise ValueError("Invalid mode specified")

        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print("Command output:", result.stdout)
            return result.stdout
        except subprocess.CalledProcessError as e:
            print("Error occurred:", e.stderr)
            return None
        
    def run_whisperx(self, mode, input_file, output_file=None, model_path=None, use_gpu=False, threads=1):
        pass

    def router(self, audio_length, language, task, model, initial_prompt, input_files, output_folder):
        # Implement the foobar function logic here
        print(f"Audio Length: {audio_length}")
        print(f"Language: {language}")
        print(f"Task: {task}")
        print(f"Model: {model}")
        print(f"Initial Prompt: {initial_prompt}")
        print(f"Input Files: {input_files}")
        print(f"Output Folder: {output_folder}")


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
