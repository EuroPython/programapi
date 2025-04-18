import pytest

from src.models.europython import EuroPythonSpeaker


# === Mastodon ===
@pytest.mark.parametrize(
    ("input_string", "result"),
    [
        ("https://mastodon.example/@user123", "https://mastodon.example/@user123"),
        ("http://mastodon.example/@user123", "https://mastodon.example/@user123"),
        (
            "https://mastodon.example/@user123?ref=xyz",
            "https://mastodon.example/@user123",
        ),
        ("@user123@mastodon.example", "https://mastodon.example/@user123"),
        ("user123@mastodon.example", "https://mastodon.example/@user123"),
        ("mastodon.example/@user123", "https://mastodon.example/@user123"),
        ("www.mastodon.example/@user123", "https://mastodon.example/@user123"),
        (" mastodon.example/@user123 ", "https://mastodon.example/@user123"),
        ("https://instance.social/@foobar", "https://instance.social/@foobar"),
        ("foobar@instance.social", "https://instance.social/@foobar"),
    ],
)
def test_extract_mastodon_url(input_string, result):
    assert EuroPythonSpeaker.extract_mastodon_url(input_string) == result


# === LinkedIn ===
@pytest.mark.parametrize(
    ("input_string", "result"),
    [
        ("user123", "https://linkedin.com/in/user123"),
        ("in/user123", "https://linkedin.com/in/user123"),
        ("linkedin.com/in/user123", "https://linkedin.com/in/user123"),
        ("http://linkedin.com/in/user123", "https://linkedin.com/in/user123"),
        ("https://linkedin.com/in/user123", "https://linkedin.com/in/user123"),
        ("https://www.linkedin.com/in/user123", "https://linkedin.com/in/user123"),
        (
            "https://linkedin.com/in/example-user-%C3%A3-encoded",
            "https://linkedin.com/in/example-user-%c3%a3-encoded",
        ),
        (
            "https://linkedin.com/in/example-user-ã-encoded",
            "https://linkedin.com/in/example-user-%c3%a3-encoded",
        ),
        ("https://linkedin.com/in/user123?ref=xyz", "https://linkedin.com/in/user123"),
        (" LINKEDIN.COM/IN/USER123 ", "https://linkedin.com/in/user123"),
        (
            "https://regional.linkedin.com/in/example",
            "https://regional.linkedin.com/in/example",
        ),
        ("in/user123/nl", "https://linkedin.com/in/user123/nl"),
        ("https://nl.linkedin.com/in/user123/en", "https://nl.linkedin.com/in/user123/en"),
    ],
)
def test_extract_linkedin_url(input_string, result):
    assert EuroPythonSpeaker.extract_linkedin_url(input_string) == result


# === Bluesky ===
@pytest.mark.parametrize(
    ("input_string", "result"),
    [
        ("user123", "https://bsky.app/profile/user123.bsky.social"),
        ("@user123", "https://bsky.app/profile/user123.bsky.social"),
        ("user123.bsky.social", "https://bsky.app/profile/user123.bsky.social"),
        ("@user123.bsky.social", "https://bsky.app/profile/user123.bsky.social"),
        ("user123.dev", "https://bsky.app/profile/user123.dev"),
        ("bsky.app/profile/user123", "https://bsky.app/profile/user123.bsky.social"),
        ("bsky/user123", "https://bsky.app/profile/user123.bsky.social"),
        (
            "www.bsky.app/profile/user123",
            "https://bsky.app/profile/user123.bsky.social",
        ),
        (
            "www.bsky.app/profile/user123.bsky.social",
            "https://bsky.app/profile/user123.bsky.social",
        ),
        (
            "http://bsky.app/profile/user123",
            "https://bsky.app/profile/user123.bsky.social",
        ),
        (
            "https://bsky.app/profile/user123",
            "https://bsky.app/profile/user123.bsky.social",
        ),
        (
            "https://bsky.app/profile/user123.dev",
            "https://bsky.app/profile/user123.dev",
        ),
        (
            "https://bsky.app/profile/user123.bsky.social",
            "https://bsky.app/profile/user123.bsky.social",
        ),
        (" BSKY.APP/PROFILE/USER123 ", "https://bsky.app/profile/user123.bsky.social"),
    ],
)
def test_extract_bluesky_url(input_string, result):
    assert EuroPythonSpeaker.extract_bluesky_url(input_string) == result


# === Twitter/X ===
@pytest.mark.parametrize(
    ("input_string", "result"),
    [
        ("user123", "https://x.com/user123"),
        ("@user123", "https://x.com/user123"),
        ("twitter.com/user123", "https://x.com/user123"),
        ("https://twitter.com/user123", "https://x.com/user123"),
        ("https://x.com/user123", "https://x.com/user123"),
        ("http://twitter.com/user123", "https://x.com/user123"),
        ("TWITTER.COM/user_name", "https://x.com/user_name"),
        (" user123 ", "https://x.com/user123"),
    ],
)
def test_extract_twitter_url(input_string, result):
    assert EuroPythonSpeaker.extract_twitter_url(input_string) == result


# === GitHub/GitLab ===
@pytest.mark.parametrize(
    ("input_string", "result"),
    [
        ("user123", "https://github.com/user123"),
        ("@user123", "https://github.com/user123"),
        ("github.com/user123", "https://github.com/user123"),
        ("https://github.com/user123", "https://github.com/user123"),
        ("gitlab.com/user123", "https://gitlab.com/user123"),
        ("https://gitlab.com/user123", "https://gitlab.com/user123"),
        (" http://github.com/user123 ", "https://github.com/user123"),
        ("GITHUB.COM/USER123", "https://github.com/user123"),
    ],
)
def test_extract_gitx(input_string, result):
    assert EuroPythonSpeaker.extract_gitx_url(input_string) == result
