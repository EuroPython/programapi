import pytest

from src.models.europython import EuroPythonSpeaker


# === Mastodon ===
@pytest.mark.parametrize(
    ("input_string",),
    [
        ("",),
        ("false",),
        ("mastodon@",),
        ("@user@",),
        ("username@",),
        ("https://mastodon.social/user",),
        ("mastodon.social/user",),
        ("@mastodon.social",),
        ("https://hostux.social/users/username",),
        ("https://social/@",),
    ],
)
def test_mastodon_url_invalid(input_string):
    assert EuroPythonSpeaker.extract_mastodon_url(input_string) is None


# === LinkedIn ===
@pytest.mark.parametrize(
    ("input_string",),
    [
        ("",),
        ("/in/",),
        ("linkedin.com/in/",),
        ("linkedin.com/in",),
        ("linkedin.com/username",),
        ("linkedin.net/in/username",),
        ("http://linkedin.com/user",),
        ("http://",),
        ("n/a",),
    ],
)
def test_linkedin_url_invalid(input_string):
    assert EuroPythonSpeaker.extract_linkedin_url(input_string) is None


# === Twitter / X ===
@pytest.mark.parametrize(
    ("input_string",),
    [
        ("",),
        ("-",),
        ("user-name",),
        ("x.com/",),
        ("https://x.com/",),
        ("https://twitter.com/",),
        ("http://",),
        ("@user@",),
        ("user!",),
        ("too_long_username_123",),
        ("twitter.com/user-with-hyphen",),
        ("https://github.com/user",),
    ],
)
def test_twitter_url_invalid(input_string):
    assert EuroPythonSpeaker.extract_twitter_url(input_string) is None


# === GitHub / GitLab ===
@pytest.mark.parametrize(
    ("input_string",),
    [
        ("",),
        ("https://bitbucket.org/user",),
        ("bitbucket.org/user",),
        ("codeberg.org/user",),
        ("https://git.example.com/user",),
        ("http://",),
        ("@/",),
    ],
)
def test_gitx_url_invalid(input_string):
    assert EuroPythonSpeaker.extract_gitx_url(input_string) is None
