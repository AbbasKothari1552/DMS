# app/modules/category_prediction/category_predictor.py

from app.modules.rag_chat.llm_engine import LLMEngine
from app.core.config import CATEGORY_LIST


from app.core.logging_config import get_logger
logger = get_logger(__name__)

class CategoryPredictor:
    def __init__(self):
        self.llm_engine = LLMEngine()

    def build_prompt(self, text: str) -> str:
        prompt = f"""
        Given the following document content:

        ---
        {text}
        ---

        Choose the most appropriate category from the following list:
        {', '.join(CATEGORY_LIST)}

        Respond with only one category name.
        """
        return prompt.strip()

    def predict_category(self, document_text: str) -> str:
        prompt = self.build_prompt(document_text)
        logger.info("Sending prompt to LLM for category prediction")
        result = self.llm_engine.generate(prompt)
        return result.strip()