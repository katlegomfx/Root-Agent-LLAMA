### building\code\LangLLM.pyimport time
import ollama
from huggingface_hub import hf_hub_download

from typing import Any, List, Mapping, Optional

from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM

from building.code.constants.script import model_map  # nopep
from building.code.loader.load_models_bypassed import load_gguf_completion_model, load_full_model, load_gguf_image_model, local_model_path  # nopep
from building.code.general.script import create_llm_result # nopep
MODELS_PATH = "./models/llms/"

class CustomLLM(LLM):
    model: str
    process_type: str
    process_time: Optional[str] = None
    last_prompt: Optional[Any] = None
    last_response: Optional[Any] = None

    @property
    def _llm_type(self) -> str:
        return "custom"

    def _call(
        self,
        prompt: Any,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        model_info, model_basename = model_map[self.model]

        start_time = time.time()

        if self.process_type == "ggufCompletionImage":
            engine = load_gguf_image_model()
            response = engine.create_chat_completion(
                messages=prompt
            )["choices"][0]["message"]["content"]
        
        elif self.process_type == "Ollama":
            
            model_path = local_model_path(model_info, model_basename)
            if self.model not in ollama.list()['models']:
                modelfile = f'''
FROM {model_path}
'''

                ollama.create(model=self.model, modelfile=modelfile)

            if isinstance(prompt, list):

                final_prompt = prompt

            elif isinstance(prompt, str):

                final_prompt = [{'role': 'user', 'content': prompt}]

            elif isinstance(prompt, dict):
                final_prompt = [prompt]
            
            stream = ollama.chat(
                    model=self.model,
                    messages=final_prompt,
                    stream=True,
                )
            
            response = ''

            for chunk in stream:
                text = chunk['message']['content']

                print(text, end='', flush=True)
                response += text
            
            print()
        elif self.process_type == "ggufCompletion":
            
            engine = load_gguf_completion_model(
                model_info, model_basename, formatting="llama-2")
            test = engine.create_chat_completion(
                messages=prompt
            )
            print(test)
            input('continue')
            response = test["choices"][0]["message"]["content"]

        elif self.process_type == "ggufCompletionJSON":
            
            response_format = {"type": "json_object"}
            engine = load_gguf_completion_model(
                model_info, model_basename, formatting="chatml")
            response = engine.create_chat_completion(
                messages=prompt,
                response_format=response_format,
            )["choices"][0]["message"]["content"]

        else:
            
            engine = load_full_model(model_info, model_basename)
            response = engine(final_prompt)

        end_time = time.time()
        time_taken = end_time - start_time
        time_taken_minutes = int(time_taken // 60)
        time_taken_seconds = int(time_taken % 60)

        self.process_time = f"{time_taken_minutes}:{time_taken_seconds}"
        self.last_response = response
        self.last_prompt = prompt

        self.store_response()

        return response

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"model": self.model}
    
    def store_response(self):
        ran = f"""
### Model Name:\n{self.model}\n### Query Type:\n{self.process_type}\n### Time taken:\n{self.process_time}\n### Input\n\n{self.last_prompt}\n### Answer:\n\n{self.last_response}"""
        result_folder = f"./results"
        create_llm_result(result_folder, ran)

