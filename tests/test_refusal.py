from src.refusal import NO_CONTEXT_REPLY, is_vietnamese, no_context_reply


def test_vietnamese_questions_are_recognised_by_their_letters():
    assert is_vietnamese("Thủ đô của nước Pháp là gì?")
    assert is_vietnamese("Nó thường được dùng để làm gì?")
    assert is_vietnamese("MA TRẬN JORDAN LÀ GÌ")  # capitals count too


def test_english_questions_are_not_taken_for_vietnamese():
    assert not is_vietnamese("What is the capital of France?")
    assert not is_vietnamese("Which optimizer does the book use to train neural networks, such as SGD?")
    assert not is_vietnamese("")


def test_the_reply_follows_the_language_of_the_question():
    assert no_context_reply("Định lý Cayley-Hamilton phát biểu điều gì?") == NO_CONTEXT_REPLY["vi"]
    assert no_context_reply("What does the Cayley-Hamilton theorem state?") == NO_CONTEXT_REPLY["en"]


def test_each_reply_is_written_in_its_own_language():
    assert is_vietnamese(NO_CONTEXT_REPLY["vi"])
    assert not is_vietnamese(NO_CONTEXT_REPLY["en"])
