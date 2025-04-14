from string import ascii_letters, digits
from urllib.parse import quote

import pytest
from hypothesis import given
from hypothesis.strategies import characters, composite, one_of, sampled_from, text

from src.models.europython import EuroPythonSpeaker

ALPHABET_SAFE = ascii_letters + digits + "-_"
SAFE_USERNAME = text(
    alphabet=ALPHABET_SAFE,
    min_size=4,
    max_size=15,
).filter(lambda x: any(c.isalnum() for c in x) and not x.startswith(("-", "_")))


@composite
def domain_names(draw, allow_subdomains=False):
    tlds = draw(
        sampled_from(["com", "net", "org", "dev", "social", "app", "io", "xyz"])
    )
    label = text(alphabet=ascii_letters + digits + "-", min_size=1, max_size=10)
    labels = [draw(label)]
    if allow_subdomains:
        labels.insert(0, draw(label))
    return ".".join(labels + [tlds])


# === Mastodon ===
@given(SAFE_USERNAME)
def test_mastodon_invalid_fallbacks(text: str):
    result = EuroPythonSpeaker.extract_mastodon_url(text)
    if "@" not in text and "/@" not in text:
        assert result is None


@given(SAFE_USERNAME, domain_names(allow_subdomains=True))
def test_mastodon_username_at_instance(username: str, domain: str):
    input_str = f"{username}@{domain}"
    expected = f"https://{domain.lower()}/@{username.lower()}"
    assert EuroPythonSpeaker.extract_mastodon_url(input_str) == expected


@given(domain_names(allow_subdomains=True), SAFE_USERNAME)
def test_mastodon_instance_slash_at_username(instance: str, username: str):
    input_str = f"{instance}/@{username}"
    expected = f"https://{instance.lower()}/@{username.lower()}"
    assert EuroPythonSpeaker.extract_mastodon_url(input_str) == expected


# === LinkedIn ===
@given(SAFE_USERNAME)
def test_linkedin_handle(username: str):
    expected = f"https://linkedin.com/in/{username.lower()}"
    assert EuroPythonSpeaker.extract_linkedin_url(username) == expected


@given(
    text(
        alphabet=one_of(
            characters(whitelist_categories=("Ll", "Lu", "Nd")),  # letters and numbers
            characters(  ## special characters (accents, etc.)
                whitelist_categories=("Ll", "Lu", "Nl", "No", "Mn", "Mc"),
            ).filter(lambda c: not c.isascii() and not c.isspace()),
        ),
        min_size=1,
        max_size=30,
    )
)
def test_linkedin_encoding_support(username: str):
    encoded = quote(username, safe="@/-_.+~#=:")
    expected = f"https://linkedin.com/in/{encoded.lower()}"
    assert (
        EuroPythonSpeaker.extract_linkedin_url(f"https://linkedin.com/in/{username}")
        == expected
    )


@given(domain_names().filter(lambda d: not d.endswith("linkedin.com")), SAFE_USERNAME)
def test_linkedin_nonsense_domains(domain: str, path: str):
    assert EuroPythonSpeaker.extract_linkedin_url(f"{domain}/in/{path}") is None


# === Bluesky ===
@given(SAFE_USERNAME)
def test_bluesky_handle_to_fallback_domain(handle: str):
    expected = f"https://bsky.app/profile/{handle.lower()}.bsky.social"
    assert EuroPythonSpeaker.extract_bluesky_url(handle) == expected


@given(domain_names())
def test_bluesky_custom_domains(domain: str):
    expected = f"https://bsky.app/profile/{domain.lower()}"
    assert EuroPythonSpeaker.extract_bluesky_url(domain) == expected


# === Twitter / X ===
@given(
    text(alphabet=ascii_letters + digits + "_", min_size=4, max_size=15),
)
def test_twitter_usernames(handle: str):
    expected = f"https://x.com/{handle.lower()}"
    assert EuroPythonSpeaker.extract_twitter_url(handle) == expected
    assert EuroPythonSpeaker.extract_twitter_url(f"@{handle}") == expected
    assert (
        EuroPythonSpeaker.extract_twitter_url(f"https://twitter.com/{handle}")
        == expected
    )
    assert EuroPythonSpeaker.extract_twitter_url(f"https://x.com/{handle}") == expected
    assert (
        EuroPythonSpeaker.extract_twitter_url(f"http://twitter.com/{handle}/")
        == expected
    )


# === GitHub / GitLab ===
@given(SAFE_USERNAME)
def test_github_usernames(username: str):
    expected = f"https://github.com/{username.lower()}"
    assert EuroPythonSpeaker.extract_gitx_url(username) == expected
    assert EuroPythonSpeaker.extract_gitx_url(f"@{username}") == expected
    assert EuroPythonSpeaker.extract_gitx_url(f"github.com/{username}") == expected


@given(SAFE_USERNAME)
def test_gitlab_usernames(username: str):
    expected = f"https://gitlab.com/{username.lower()}"
    assert EuroPythonSpeaker.extract_gitx_url(f"gitlab.com/{username}") == expected
    assert (
        EuroPythonSpeaker.extract_gitx_url(f"https://gitlab.com/{username}") == expected
    )
