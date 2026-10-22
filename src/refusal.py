"""Fixed reply for a question that no indexed passage helps with, in the language of the question."""

import re

NO_CONTEXT_REPLY = {
    "en": "I cannot find the relevant information in the provided documents.",
    "vi": "Tôi không tìm thấy thông tin liên quan trong các tài liệu được cung cấp.",
}

# Letters Vietnamese uses and English does not: d with stroke, the circumflex/breve/horn vowels and the vowels with a
# tone mark. An English word with an accent (a "café") counts as Vietnamese, which is rare in this English/Vietnamese
# corpus. A Vietnamese question typed without diacritics is taken for English.
VIETNAMESE_LETTERS = re.compile(
    r"[ăâđêôơưàáảãạằắẳẵặầấẩẫậèéẻẽẹềếểễệìíỉĩịòóỏõọồốổỗộờớởỡợùúủũụừứửữựỳýỷỹỵ]",
    re.IGNORECASE,
)


def is_vietnamese(text: str) -> bool:
    return VIETNAMESE_LETTERS.search(text) is not None


def no_context_reply(question: str) -> str:
    """The refusal in Vietnamese for a Vietnamese question, in English otherwise."""
    return NO_CONTEXT_REPLY["vi"] if is_vietnamese(question) else NO_CONTEXT_REPLY["en"]
