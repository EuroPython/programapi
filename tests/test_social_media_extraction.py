import pytest

from src.transform import PretalxSpeaker


@pytest.mark.parametrize(
    ("input_string", "result"),
    [
        ("http://mastodon.social/@username", "https://mastodon.social/@username"),
        ("https://mastodon.social/@username", "https://mastodon.social/@username"),
        ("https://mastodon.social/@username?something=true", "https://mastodon.social/@username"),
        ("@username@mastodon.social", "https://mastodon.social/@username"),
    ]
)
def test_extract_mastodon_url(input_string: str, result: str) -> None:
    assert PretalxSpeaker.extract_mastodon_url(input_string) == result


@pytest.mark.parametrize(
    ("input_string", "result"),
    [
        ("username", "https://linkedin.com/in/username"),
        ("in/username", "https://linkedin.com/in/username"),
        ("www.linkedin.com/in/username", "https://www.linkedin.com/in/username"),
        ("http://linkedin.com/in/username", "https://linkedin.com/in/username"),
        ("https://linkedin.com/in/username", "https://linkedin.com/in/username"),
    ]
)
def test_extract_linked_url(input_string: str, result: str) -> None:
    assert PretalxSpeaker.extract_linkedin_url(input_string) == result
