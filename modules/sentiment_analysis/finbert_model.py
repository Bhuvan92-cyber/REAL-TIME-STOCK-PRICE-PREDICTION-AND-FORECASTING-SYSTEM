from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from modules.utils.logger import get_logger

logger = get_logger(__name__)

class FinBERTSentiment:
    def __init__(self):
        logger.info("Loading FinBERT model")
        self.tokenizer = AutoTokenizer.from_pretrained(
            "ProsusAI/finbert"
        )
        self.model = AutoModelForSequenceClassification.from_pretrained(
            "ProsusAI/finbert"
        )

    def predict(self, texts):
        """
        Predicts sentiment labels for financial texts.
        Returns average sentiment score.
        """

        logger.info("Predicting sentiment using FinBERT")

        sentiments = []

        for text in texts:
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True
            )
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=1)
            sentiment_score = (
                probs[0][2].item() - probs[0][0].item()
            )  # positive - negative
            sentiments.append(sentiment_score)

        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
        logger.info(f"FinBERT sentiment score: {avg_sentiment}")
        return avg_sentiment
