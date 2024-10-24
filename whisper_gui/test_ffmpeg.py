import ffmpeg
import os
from subprocess import CalledProcessError, run
import torch
import numpy as np
import subprocess
from datasets import load_dataset, Audio, Dataset
# from transformers import WhisperProcessor, WhisperForConditionalGeneration
# from transformers.pipelines.audio_utils import ffmpeg_read


def ffmpeg_read(bpayload: bytes, sampling_rate: int) -> np.array:
    """
    Helper function to read an audio file through ffmpeg.
    """
    ar = f"{sampling_rate}"
    ac = "1"
    format_for_conversion = "f32le"
    ffmpeg_command = [
        "/home/jayya931/UPPMAX/Whisper_project/Whisper-sens/ffmpeg/ffmpeg-git-20240524-amd64-static/ffmpeg",
        "-i",
        "pipe:0",
        "-ac",
        ac,
        "-ar",
        ar,
        "-f",
        format_for_conversion,
        "-hide_banner",
        "-loglevel",
        "quiet",
        "pipe:1",
    ]

    try:
        with subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE) as ffmpeg_process:
            output_stream = ffmpeg_process.communicate(bpayload)
    except FileNotFoundError as error:
        raise ValueError("ffmpeg was not found but is required to load audio files from filename") from error
    out_bytes = output_stream[0]
    audio = np.frombuffer(out_bytes, np.float32)
    if audio.shape[0] == 0:
        raise ValueError(
            "Soundfile is either not in the correct format or is malformed. Ensure that the soundfile has "
            "a valid audio file extension (e.g. wav, flac or mp3) and is not corrupted. If reading from a remote "
            "URL, ensure that the URL is the full address to **download** the audio file."
        )
    return audio


if __name__=="__main__":

    # if "FFMPEG_PATH" not in os.environ:
    # os.environ["FFMPEG_PATH"] = "../ffmpeg/ffmpeg-git-20240524-amd64-static/ffmpeg" 

    file = "/home/jayya931/Downloads/lex_clip.mp3"

    # data_path = ffmpeg.input(data_path)\                              
    #             .audio\
    #             .output("audio.mp3")\
    #             .run()
    # print(data_path)

    # cmd = "../ffmpeg/ffmpeg-git-20240524-amd64-static/ffmpeg "
    # cmd = [
    # "/home/jayya931/UPPMAX/Whisper_project/Whisper-sens/ffmpeg/ffmpeg-git-20240524-amd64-static/ffmpeg",
    # "-nostdin",
    # "-threads", "0",
    # "-i", file,
    # "-f", "s16le",
    # "-ac", "1",
    # "-acodec", "pcm_s16le",
    # "-ar", str(16000),
    # "-"
    # ]
    
    # try:
    #     out = run(cmd, capture_output=True, check=True).stdout
    # except CalledProcessError as e:
    #     raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e
    
    # audio_dataset = Dataset.from_dict(
    # {"audio": [file]}).cast_column("audio", Audio(sampling_rate=16000))

    # # numpy_audio =  np.frombuffer(out, np.int16).flatten().astype(np.float32) / 32768.0
    # # audio = torch.from_numpy(numpy_audio)

    # load as bytes
    with open(file, "rb") as f:
        inputs = f.read()

    # read bytes as array
    inputs = ffmpeg_read(inputs, sampling_rate=16000)
    

    # inputs = self.processor(audio["array"], sampling_rate=16000, return_tensors="pt")
    # inputs = inputs.to(device=self.device, dtype=self.torch_dtype) #half precision (float16) does not work. Use float32.
    
    # outputs = self.model.generate(**inputs, language="en", task="transcribe") #language="nl"
    # outputs = self.model.generate(**inputs, task="translate") 
    # output, gen_time = assisted_generate_with_time(model, inputs, language="nl", task="transcribe")
    # predictions.append(self.processor.batch_decode(outputs, skip_special_tokens=True, normalize=True)[0])

    print(inputs)


