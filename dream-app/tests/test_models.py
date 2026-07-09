from dreamapp.models import Amplification, Interpretation, Passage, Symbol, parse_model_json


def test_symbol_round_trip():
    s = Symbol(image="milk", kind="archetypal", salience=5, query="milk nourishment")
    assert Symbol.from_dict(s.to_dict()) == s


def test_passage_round_trip():
    p = Passage(page_path="wiki/concepts/Foo.md", absolute_path="/abs/Foo.md",
                snippet="a snippet", score=0.42, page_text="full text")
    assert Passage.from_dict(p.to_dict()) == p


def test_interpretation_round_trip():
    i = Interpretation(
        dramatic_structure="exposition then culmination",
        compensation="balances neglect",
        amplifications=[Amplification("milk", "corpus says", "personal", "archetypal", False)],
        objective_level="obj", subjective_level="subj", movement="toward wholeness",
        question="what are you avoiding?", sources=["wiki/concepts/Foo.md"],
    )
    d = i.to_dict()
    i2 = Interpretation.from_dict(d)
    assert i2.dramatic_structure == i.dramatic_structure
    assert i2.amplifications[0].symbol == "milk"
    assert i2.sources == ["wiki/concepts/Foo.md"]


def test_parse_model_json_clean():
    assert parse_model_json('{"a": 1}') == {"a": 1}


def test_parse_model_json_fenced():
    assert parse_model_json('```json\n{"a": 1}\n```') == {"a": 1}


def test_parse_model_json_prefixed_prose():
    assert parse_model_json('Here is the result:\n{"a": 1}\nThanks.') == {"a": 1}


def test_parse_model_json_array():
    assert parse_model_json('[{"a": 1}, {"b": 2}]') == [{"a": 1}, {"b": 2}]
