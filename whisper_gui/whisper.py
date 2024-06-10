import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, AutoModelForCausalLM
import time
from tqdm import tqdm
from datasets import load_dataset, Audio, Dataset
from evaluate import load
import os
import subprocess
import ffmpeg
import numpy as np

def generate_with_time(model, inputs, **kwargs):
    start_time = time.time()
    outputs = model.generate(**inputs, **kwargs)
    generation_time = time.time() - start_time
    return outputs, generation_time

def assisted_generate_with_time(model, inputs, **kwargs):
    start_time = time.time()
    outputs = model.generate(**inputs, assistant_model=assistant_model, **kwargs)
    generation_time = time.time() - start_time
    return outputs, generation_time

class Whisper:
    def __init__(self):
        self.cache_dir = None # download the model
        # self.data_path = './' # same dir as app
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        # self.model_id = "openai/whisper-tiny"
        self.model_id = "openai/whisper-large-v2"
        # self.assistant_model_id = "openai/whisper-tiny"
        self.model = None
        self.processor = None
        
    def __from_pretrained__(self, model_id, cache_dir, torch_dtype):
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
        self.model_id, # chnage to pretrained_model_name_or_path = '../models/'
        cache_dir = self.cache_dir,
        torch_dtype= self.torch_dtype,
        low_cpu_mem_usage=True,
        use_safetensors=True,
        attn_implementation="sdpa",
        )
        self.model.to(self.device)

        self.processor = AutoProcessor.from_pretrained(model_id)
    
    def load_models(self, model_path):
        self.cache_dir = model_path

    def __ffmpeg_read__(self, bpayload: bytes, sampling_rate: int) -> np.array:
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

    def __dataloader__(self, file):
        self.data_path = file

        # if "FFMPEG_PATH" not in os.environ:
        #     os.environ["FFMPEG_PATH"] = "../ffmpeg/ffmpeg-git-20240524-amd64-static/ffmpeg"    
        
        # data_path = ffmpeg.input(data_path)\
        #             .audio\
        #             .output("audio.mp3")\
        #             .run()
        # print(self.data_path)
        # cmd = [
        #     "/home/jayya931/UPPMAX/Whisper_project/Whisper-sens/ffmpeg/ffmpeg-git-20240524-amd64-static/ffmpeg",
        #     "-nostdin",
        #     "-threads", "0",
        #     "-i", file,
        #     "-f", "s16le",
        #     "-ac", "1",
        #     "-acodec", "pcm_s16le",
        #     "-ar", str(16000),
        #     "/home/jayya931/UPPMAX/Whisper_project/Whisper-sens/whisper_gui/output.wav"
        # ]
        
        # try:
        #     out = run(cmd, capture_output=True, check=True).stdout
        # except CalledProcessError as e:
        #     raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e
            # load as bytes
        # file = "/home/jayya931/Downloads/sample_audio.mp3"
        with open(file, "rb") as f:
            inputs = f.read()

        # read bytes as array
        # inputs = self.__ffmpeg_read__(inputs, sampling_rate=16000)
        inputs = file
        audio_dataset = Dataset.from_dict(
            {"audio": [inputs]}).cast_column("audio", Audio(sampling_rate=16000))
        # return inputs
        return audio_dataset

    def encoder(self, ):
        pass

    def decoder(self,):
        pass

    def pipeline(self, data_path):

        self.__from_pretrained__(self.model_id, self.cache_dir, self.torch_dtype)
        dataset = self.__dataloader__(data_path)

        predictions = []
        # dataset = load_dataset("sanchit-gandhi/voxpopuli_dummy", "nl", split="validation")
        for sample in tqdm(dataset): #TODO: convert ffmpeg_read output to audio_dataset
            audio = sample["audio"]
            # audio = dataset
            inputs = self.processor(audio["array"], sampling_rate=16000, return_tensors="pt")
            # inputs = self.processor(audio, sampling_rate=16000, return_tensors="pt")
            inputs = inputs.to(device=self.device, dtype=self.torch_dtype) #half precision (float16) does not work. Use float32.
            
            # outputs = self.model.generate(**inputs, language="en", task="transcribe") #language="nl"
            outputs = self.model.generate(**inputs, task="transcribe") 
            # output, gen_time = assisted_generate_with_time(model, inputs, language="nl", task="transcribe")
            predictions.append(self.processor.batch_decode(outputs, skip_special_tokens=True, normalize=True)[0])
            #BUG: whisper only works for 30 sec of the clip!
        return predictions




if __name__ == "__main__":
    
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    model_id = "openai/whisper-tiny"
    # model_id = "openai/whisper-large-v2"
    # model_id = "../models/models--openai--whisper-large-v2"

    # model_id = "openai/whisper-tiny"
    # assistant_model_id = "distil-whisper/distil-large-v2"
    assistant_model_id = "openai/whisper-tiny"

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, # chnage to pretrained_model_name_or_path = '../models/'
        cache_dir = "./models/",
        torch_dtype=torch_dtype,
        low_cpu_mem_usage=True,
        use_safetensors=True,
        attn_implementation="sdpa",
        
    )
    model.to(device)

    # Use AutoModelForCausalLM in case the encoder is same like distil-large-v2
    assistant_model = AutoModelForSpeechSeq2Seq.from_pretrained( 
        assistant_model_id,
        cache_dir = "./models/",
        torch_dtype=torch_dtype,
        low_cpu_mem_usage=True,
        use_safetensors=True,
        attn_implementation="sdpa",
    )
    assistant_model.to(device)

    processor = AutoProcessor.from_pretrained(model_id)


    # dataset = load_dataset("hf-internal-testing/librispeech_asr_dummy", "clean", split="validation")
    dataset = load_dataset("sanchit-gandhi/voxpopuli_dummy", "nl", split="validation")


    all_time = 0
    predictions = []
    references = []

    for sample in tqdm(dataset):
        audio = sample["audio"]
        inputs = processor(audio["array"], sampling_rate=audio["sampling_rate"], return_tensors="pt")
        inputs = inputs.to(device=device, dtype=torch_dtype) #half precision (float16) does not work. Use float32.
        
        output, gen_time = generate_with_time(model, inputs, language="nl", task="transcribe")
        # output, gen_time = assisted_generate_with_time(model, inputs, language="nl", task="transcribe")
        all_time += gen_time
        predictions.append(processor.batch_decode(output, skip_special_tokens=True, normalize=True)[0])
        # references.append(processor.tokenizer._normalize(sample["text"]))
        references.append(processor.tokenizer._normalize(sample["normalized_text"]))

    # print(predictions)
    print(all_time)
    wer = load("wer")
    print(wer.compute(predictions=predictions, references=references))