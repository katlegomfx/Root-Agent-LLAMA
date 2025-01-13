### building\code\loader\load_models_bypassed.pyimport os
import ollama

from ctransformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import hf_hub_download
from llama_cpp import Llama
from llama_cpp.llama_chat_format import Llava15ChatHandler

from building.code.constants.script import MODELS_PATH
from building.code.constants.script import model_map

### import ssl### ssl._create_default_https_context = ssl._create_unverified_contextos.environ['CURL_CA_BUNDLE'] = ''

def load_full_model(model_id, model_basename):
    model_path = local_model_path(model_id, model_basename)

    config = AutoConfig.from_pretrained(model_path)
    config.config.max_seq_len = 16384 * 2
    config.config.max_answer_len = 16384 * 2
    config.config.max_new_tokens = 16384 * 2
    config.config.context_length = 16384 * 2

    model = AutoModelForCausalLM.from_pretrained(model_path, config=config)
    return model

def load_gguf_completion_model(model_id, model_basename, formatting):
    model_path = local_model_path(model_id, model_basename)
    llm = Llama(
        model_path=model_path,
    
        n_batch=int((16384/2)+(16384/8)),
        n_ctx=int((16384/2)+(16384/8)),
        chat_format=formatting,
        ### stop='[INST]'
    )
    return llm

def load_gguf_image_model():
    
    MODEL_ID = model_map["llavaPrj"][0]
    MODEL_BASENAME = model_map["llavaPrj"][1]
    clip_model_path = hf_hub_download(
        repo_id=MODEL_ID,
        filename=MODEL_BASENAME,
        cache_dir=MODELS_PATH,
    )
    chat_handler = Llava15ChatHandler(
        clip_model_path=clip_model_path)
  
    MODEL_ID = model_map["llava"][0]
    MODEL_BASENAME = model_map["llava"][1]
    model_path = hf_hub_download(
        repo_id=MODEL_ID,
        filename=MODEL_BASENAME,
        cache_dir=MODELS_PATH,
    )
    llm = Llama(
        model_path=model_path,
        chat_handler=chat_handler,
        n_ctx=int((16384/2)+(16384/8)), 
        logits_all=True,  
    )
    return llm

def local_model_path(model_info, model_basename):
    model_path = hf_hub_download(
        repo_id=model_info,
        filename=model_basename,
        cache_dir=MODELS_PATH,
    )

    return model_path

def load_to_ollama(local_name_llm):
    ### if local_name_llm not in ollama.list()['models']:        model_info, model_basename = model_map[local_name_llm]
        model_path = local_model_path(model_info, model_basename)
        modelfile = f'''
FROM {model_path}
'''

        ollama.create(model=local_name_llm, modelfile=modelfile)

