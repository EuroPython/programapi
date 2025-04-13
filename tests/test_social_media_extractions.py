import pytest

from src.models.europython import EuroPythonSpeaker


@pytest.mark.parametrize(
    ("input_string", "result"),
    [
        ("http://mastodon.social/@username", "https://mastodon.social/@username"),
        ("https://mastodon.social/@username", "https://mastodon.social/@username"),
        (
            "https://mastodon.social/@username?something=true",
            "https://mastodon.social/@username",
        ),
        ("@username@mastodon.social", "https://mastodon.social/@username"),
        ("username@mastodon.social", "https://mastodon.social/@username"),
    ],
)
def test_extract_mastodon_url(input_string: str, result: str) -> None:
    assert EuroPythonSpeaker.extract_mastodon_url(input_string) == result


@pytest.mark.parametrize(
    ("input_string", "result"),
    [
        ("username", "https://linkedin.com/in/username"),
        ("linkedin.com/in/username", "https://linkedin.com/in/username"),
        ("in/username", "https://linkedin.com/in/username"),
        ("www.linkedin.com/in/username", "https://www.linkedin.com/in/username"),
        ("http://linkedin.com/in/username", "https://linkedin.com/in/username"),
        ("https://linkedin.com/in/username", "https://linkedin.com/in/username"),
    ],
)
def test_extract_linkedin_url(input_string: str, result: str) -> None:
    assert EuroPythonSpeaker.extract_linkedin_url(input_string) == result


@pytest.mark.parametrize(
    ("input_string", "result"),
    [
        ("username", "https://bsky.app/profile/username.bsky.social"),
        ("@username", "https://bsky.app/profile/username.bsky.social"),
        ("username.dev", "https://bsky.app/profile/username.dev"),
        ("@username.dev", "https://bsky.app/profile/username.dev"),
        ("username.bsky.social", "https://bsky.app/profile/username.bsky.social"),
        ("bsky.app/profile/username", "https://bsky.app/profile/username.bsky.social"),
        ("bsky/username", "https://bsky.app/profile/username.bsky.social"),
        (
            "www.bsky.app/profile/username",
            "https://bsky.app/profile/username.bsky.social",
        ),
        (
            "www.bsky.app/profile/username.bsky.social",
            "https://bsky.app/profile/username.bsky.social",
        ),
        (
            "http://bsky.app/profile/username",
            "https://bsky.app/profile/username.bsky.social",
        ),
        (
            "https://bsky.app/profile/username.com",
            "https://bsky.app/profile/username.com",
        ),
        (
            "https://bsky.app/profile/username.bsky.social",
            "https://bsky.app/profile/username.bsky.social",
        ),
    ],
)
def test_extract_bluesky_url(input_string: str, result: str) -> None:
    assert EuroPythonSpeaker.extract_bluesky_url(input_string) == result
