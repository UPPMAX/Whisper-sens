import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, AutoModelForCausalLM
import time
from tqdm import tqdm
from datasets import load_dataset
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

if __name__ == "__main__":
    
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    # model_id = "openai/whisper-tiny"
    model_id = "openai/whisper-large-v2"
    # model_id = "openai/whisper-tiny"
    # assistant_model_id = "distil-whisper/distil-large-v2"
    assistant_model_id = "openai/whisper-tiny"

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id,
        torch_dtype=torch_dtype,
        low_cpu_mem_usage=True,
        use_safetensors=True,
        attn_implementation="sdpa",
    )
    model.to(device)

    # Use AutoModelForCausalLM in case the encoder is same like distil-large-v2
    assistant_model = AutoModelForSpeechSeq2Seq.from_pretrained( 
        assistant_model_id,
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
        inputs = inputs.to(device=device, dtype=torch.float32) #half precision (float16) does not work. Use float32.
        
        # output, gen_time = generate_with_time(model, inputs)
        output, gen_time = assisted_generate_with_time(model, inputs, language="nl", task="transcribe")
        all_time += gen_time
        predictions.append(processor.batch_decode(output, skip_special_tokens=True, normalize=True)[0])
        # references.append(processor.tokenizer._normalize(sample["text"]))
        references.append(processor.tokenizer._normalize(sample["normalized_text"]))

    # print(predictions)
    print(all_time)
    wer = load("wer")
    print(wer.compute(predictions=predictions, references=references))