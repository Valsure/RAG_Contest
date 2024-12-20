from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoProcessor
from vllm import LLM, SamplingParams
from qwen_vl_utils import process_vision_info
import os

app = FastAPI()

MODEL_PATH = os.path.expanduser("~/.cache/huggingface/hub/models--Qwen--Qwen2-VL-7B-Instruct/snapshots/51c47430f97dd7c74aa1fa6825e68a813478097f")

llm = LLM(
    model=MODEL_PATH,
    limit_mm_per_prompt={'image': 10, 'video': 10},
    tensor_parallel_size=2
)

processor = AutoProcessor.from_pretrained(MODEL_PATH)

class GenerateResponse(BaseModel):
    generated_text: str

class SearchDataBase(BaseModel):
    text: str
    


@app.post("/generate", response_model=GenerateResponse)
async def generate_text(request: SearchDataBase):
    try:
        with open('/hy-tmp/project/WWW2025/liziheng/RAG/prompt.txt', 'r', encoding='utf-8') as file:  
            system_content = file.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="没有此prompt")
    messages = [
        {'role': 'system', 'content': system_content},
        {'role': 'user', 'content': [
            {'type': 'text', 'text': request.text}
        ]},
    ]

    prompt = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    
    image_inputs, video_inputs = process_vision_info(messages)
    mm_data = {}
    if image_inputs is not None:
        mm_data['image'] = image_inputs
    if video_inputs is not None:
        mm_data['video'] = video_inputs

    sampling_params = SamplingParams(
        temperature=0.1, top_p=0.001, repetition_penalty=1.05, max_tokens=1024, stop_token_ids=[]
    )

    llm_inputs = {'prompt': prompt, 'multi_modal_data': mm_data}
    outputs = llm.generate([llm_inputs], sampling_params=sampling_params)
    
    if outputs and outputs[0].outputs:
        generated_text = outputs[0].outputs[0].text
        
    else:
        raise HTTPException(status_code=500, detail="Failed to generate text")

    return GenerateResponse(generated_text=generated_text)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
