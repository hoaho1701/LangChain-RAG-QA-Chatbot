from langchain_core.documents.base import Document

from src.chunking import SEPARATORS, _hard_split, _recursive_split, split_documents

SIZE, OVERLAP = 240, 30


def sentence(i):
    return f"Sentence number {i:03d} talks about topic {i * 7 % 101:03d}."


def long_paragraph(first, count):
    return " ".join(sentence(first + k) for k in range(count))


def repeats_inside(chunk, length=25):
    """True when some block of `length` characters occurs twice in the chunk."""
    return any(chunk.find(chunk[i : i + length], i + 1) != -1 for i in range(len(chunk) - length))


def test_a_short_text_stays_one_chunk():
    assert _recursive_split("short text", SIZE, OVERLAP, SEPARATORS) == ["short text"]


def test_a_text_of_only_spaces_gives_no_chunk():
    assert _recursive_split("   \n  ", 3, OVERLAP, SEPARATORS) == []


def test_chunks_of_a_text_without_long_paragraphs_overlap_by_the_end_of_the_previous_chunk():
    text = "alpha beta gamma delta\n\nepsilon zeta eta theta iota kappa\n\nlambda mu nu xi omicron pi rho sigma"

    chunks = _recursive_split(text, 60, 10, SEPARATORS)

    assert chunks == [
        "alpha beta gamma delta\n\nepsilon zeta eta theta iota kappa",
        "iota kappa\n\nlambda mu nu xi omicron pi rho sigma",
    ]


def test_the_overlap_is_not_added_twice_when_a_long_paragraph_is_split_again():
    # The middle paragraph is longer than a chunk, so it is split by a nested call
    text = "\n\n".join([long_paragraph(0, 2), long_paragraph(10, 12), long_paragraph(40, 2)])

    chunks = _recursive_split(text, SIZE, OVERLAP, SEPARATORS)

    assert len(chunks) > 3
    assert not [c for c in chunks if repeats_inside(c)]


def test_the_overlap_is_not_added_twice_when_a_long_word_is_hard_split():
    unique_long_word = "".join(f"{i:04d}" for i in range(120))
    text = "\n\n".join([long_paragraph(0, 2), unique_long_word, long_paragraph(40, 2)])

    chunks = _recursive_split(text, SIZE, OVERLAP, SEPARATORS)

    assert not [c for c in chunks if repeats_inside(c)]


def test_no_chunk_is_longer_than_a_chunk_and_a_fifth():
    text = "\n\n".join([long_paragraph(0, 2), long_paragraph(10, 12), long_paragraph(40, 2)])

    chunks = _recursive_split(text, SIZE, OVERLAP, SEPARATORS)

    assert max(len(c) for c in chunks) <= SIZE * 1.2


def test_no_part_of_the_text_is_lost():
    # Splitting on ". " drops the full stops, so look for the numbered start of each sentence instead
    sentences = [sentence(i) for i in range(40)]
    text = "\n\n".join(" ".join(sentences[i : i + 12]) for i in range(0, 40, 12))

    joined = "\n".join(_recursive_split(text, SIZE, OVERLAP, SEPARATORS))

    assert [i for i in range(40) if f"number {i:03d}" not in joined] == []


def test_a_text_without_any_separator_is_cut_in_overlapping_windows():
    text = "".join(f"{i:04d}" for i in range(63))  # 252 characters

    chunks = _hard_split(text, 100, 20)

    assert [len(c) for c in chunks] == [100, 100, 92]
    assert chunks[0][-20:] == chunks[1][:20]
    assert chunks[1][-20:] == chunks[2][:20]


def test_split_documents_keeps_the_metadata_and_numbers_the_chunks():
    doc = Document(
        page_content="\n\n".join([long_paragraph(0, 12), long_paragraph(20, 12)]),
        metadata={"source": "a.txt", "page": 3},
    )

    splits = split_documents([doc], SIZE, OVERLAP)

    assert len(splits) > 2
    assert [s.metadata["start_index"] for s in splits] == list(range(len(splits)))
    assert {(s.metadata["source"], s.metadata["page"]) for s in splits} == {("a.txt", 3)}
