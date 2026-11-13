"""Content integrity checks for app.content and app.quiz modules."""
import os
import tempfile
import unicodedata

os.environ.setdefault("DANSH_DB", os.path.join(tempfile.mkdtemp(), "i.db"))
os.environ.setdefault("DANSH_RATE_PER_MIN", "100000")

from app import content, quiz  # noqa: E402


def has_devanagari(text: str) -> bool:
    """Check if text contains at least one Devanagari character."""
    for char in text:
        if unicodedata.name(char, "").startswith("DEVANAGARI"):
            return True
    return False


def test_follow_ups_keys_in_red_flags():
    """Every key used in app.content.FOLLOW_UPS exists in app.content.RED_FLAGS."""
    follow_up_keys = {key for key, _ in content.FOLLOW_UPS}
    red_flag_keys = set(content.RED_FLAGS.keys())
    
    missing = follow_up_keys - red_flag_keys
    assert not missing, f"FOLLOW_UPS keys not in RED_FLAGS: {missing}"


def test_items_have_required_fields():
    """Every entry in app.content.ITEMS has non-empty 'en' and 'hi' text and valid 'src'."""
    source_keys = set(content.SOURCES.keys())
    
    for item_id, item in content.ITEMS.items():
        # Check that 'en' exists and is non-empty
        assert "en" in item, f"Item '{item_id}' missing 'en' field"
        assert isinstance(item["en"], str) and item["en"].strip(), \
            f"Item '{item_id}' has empty or non-string 'en' field"
        
        # Check that 'hi' exists and is non-empty
        assert "hi" in item, f"Item '{item_id}' missing 'hi' field"
        assert isinstance(item["hi"], str) and item["hi"].strip(), \
            f"Item '{item_id}' has empty or non-string 'hi' field"
        
        # Check that 'src' exists and is a valid key
        assert "src" in item, f"Item '{item_id}' missing 'src' field"
        assert item["src"] in source_keys, \
            f"Item '{item_id}' has invalid src '{item['src']}' not in SOURCES"


def test_quiz_concepts_lesson_in_items():
    """Every quiz concept in app.quiz.CONCEPTS has a 'lesson' that is a key of app.content.ITEMS."""
    item_keys = set(content.ITEMS.keys())
    
    for concept_id, concept in quiz.CONCEPTS.items():
        assert "lesson" in concept, f"Concept '{concept_id}' missing 'lesson' field"
        lesson_id = concept["lesson"]
        assert lesson_id in item_keys, \
            f"Concept '{concept_id}' has lesson '{lesson_id}' not in ITEMS"


def test_hindi_strings_contain_devanagari():
    """Every Hindi string in ITEMS contains at least one Devanagari character."""
    for item_id, item in content.ITEMS.items():
        hi_text = item.get("hi", "")
        if hi_text:
            assert has_devanagari(hi_text), \
                f"Item '{item_id}' Hindi text has no Devanagari characters: {hi_text}"
