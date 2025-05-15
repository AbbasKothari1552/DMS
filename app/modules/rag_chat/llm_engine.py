# --- app/modules/rag_chat/llm_engine.py ---

from typing import Literal
from langchain_huggingface.llms import HuggingFacePipeline
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import os
from langchain_ollama.llms import OllamaLLM


from app.core.config import LLM_MODEL

# logging configs
from app.core.logging_config import get_logger
logger = get_logger(__name__)


class LLMEngine:
    def __init__(self, model_source: Literal["llama", "openai"] = "llama"):

        self.llm = OllamaLLM(model=LLM_MODEL)
        # self.model_source = model_source

        # if model_source == "llama":
        #     self.llm = self._load_llama_model()
        # else:
        #     raise NotImplementedError("Only 'llama' is supported for now")

    def _load_llama_model(self):
        model_id = os.getenv("LLM_MODEL_ID", "TheBloke/Llama-2-7B-Chat-GGML") 

        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(model_id)

        pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=512)
        return HuggingFacePipeline(pipeline=pipe)

    def generate(self, prompt: str) -> str:
        logger.info(f"Generating answer from llm")
        return self.llm(prompt)
