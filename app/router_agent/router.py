import re
import json
from pathlib import Path

def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

INTENT_PATH = Path("app/intent_dataset/sales_crm_intents.json")

with open(INTENT_PATH, "r", encoding="utf-8") as f:
    INTENTS = json.load(f)

def score_pattern(user_text: str, pattern: str) -> int:
    """
    Tính điểm khớp giữa câu user và pattern
    """
    user_words = set(normalize_text(user_text).split())
    pattern_words = set(normalize_text(pattern).split())

    # số từ trùng nhau
    common = user_words & pattern_words
    return len(common)

def score_intent(user_input: str, intent: dict) -> int:
    score = 0
    for pattern in intent["patterns"]:
        score += score_pattern(user_input, pattern)
    return score

def match_intent(user_input: str):
    best_intent = None
    best_score = 0

    for intent in INTENTS:
        score = score_intent(user_input, intent)
        if score > best_score:
            best_score = score
            best_intent = intent

    if best_score == 0:
        return None

    return best_intent

def extract_entities(text: str, entity_list: list):
    entities = {}
    text_norm = normalize_text(text)

    if "order_id" in entity_list:
        match = re.search(r"\bđơn\s*hàng\s*(\d+)|\b(\d{3,})\b", text_norm)
        if match:
            entities["order_id"] = int(match.group(1) or match.group(2))

    if "product_id" in entity_list:
        match = re.search(r"\bsản\s*phẩm\s*(\d+)|\b(\d{3,})\b", text_norm)
        if match:
            entities["product_id"] = int(match.group(1) or match.group(2))

    if "voucher_code" in entity_list:
        match = re.search(r"\b[A-Z0-9]{4,}\b", text)
        if match:
            entities["voucher_code"] = match.group()

    if "rating" in entity_list:
        match = re.search(r"(\d)\s*sao", text_norm)
        if match:
            entities["rating"] = int(match.group(1))

    return entities

def route(user_input: str):
    intent = match_intent(user_input)

    if not intent:
        return {
            "intent": None,
            "message": "Xin lỗi, tôi chưa hiểu yêu cầu của bạn."
        }

    entities = extract_entities(user_input, intent.get("entities", []))

    return {
        "intent": intent["intent"],
        "tool": intent["tool"],
        "entities": entities,
        "confidence": "rule-based-scoring"
    }
