import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, AutoModelForCausalLM
import time
from tqdm import tqdm
from datasets import load_dataset, Audio
from evaluate import load

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
        self.model_id = "openai/whisper-tiny"
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

    def __data_loader__(self, data_path):
        # self.data_path = data_path        
        audio_dataset = dataset.from_dict(
            {"audio": [data_path]}).cast_column("audio", Audio())
        return audio_dataset

    def encoder(self, ):
        pass

    def decoder(self,):
        pass

    def pipeline(self,data_path):

        self.__from_pretrained__(self.model_id, self.cache_dir, self.torch_dtype)
        dataset = self.__data_loader__(data_path)

        predictions = []
        # dataset = load_dataset("sanchit-gandhi/voxpopuli_dummy", "nl", split="validation")
        for sample in tqdm(dataset):
            audio = sample["audio"]
            inputs = self.processor(audio["array"], sampling_rate=audio["sampling_rate"], return_tensors="pt")
            inputs = inputs.to(device=self.device, dtype=self.torch_dtype) #half precision (float16) does not work. Use float32.
            
            outputs = self.model.generate(**inputs, language="nl", task="transcribe")
            # output, gen_time = assisted_generate_with_time(model, inputs, language="nl", task="transcribe")
            predictions.append(self.processor.batch_decode(outputs, skip_special_tokens=True, normalize=True)[0])

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