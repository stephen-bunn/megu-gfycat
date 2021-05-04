# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# GPLv3 License <https://choosealicense.com/licenses/gpl-3.0/>

"""Contains helper functions that the plugins can use freely."""

import os
from typing import Generator, Optional, Tuple

from megu import Content, Url
from megu.log import instance as log

from .api import iter_content as iter_gfycat_content
from .constants import ENV_API_ENABLED, ENV_API_SECRET, ENV_API_TOKEN, VALID_PATTERNS
from .guesswork import iter_content as iter_guessed_content


def get_url_id(url: Url) -> Optional[str]:
    """Attempt to extract the gfycat internal ID for the given URL.

    Args:
        url (~megu.Url):
            The Url the user passed through the plugin.

    Returns:
        Optional[str]:
            The discovered gfycat internal ID if found.
    """

    for pattern in VALID_PATTERNS:
        url_match = pattern.match(url.url)
        if url_match:
            return url_match.groupdict().get("id", None)

    return None


def is_known_url(url: Url) -> bool:
    """Determine if the given URL is one we know how to handle.

    Args:
        url (~megu.Url):
            The Url the user passed through the plugin.

    Returns:
        bool:
            True if we can handle the given URL, otherwise False.
    """

    return get_url_id(url) is not None


def is_api_enabled() -> bool:
    """Determine if the environment indicates that the API logic should be used.

    .. tip:
        Since environment values are strings, we are not evaluating the string with just
        a direct cast to ``bool()``. Instead truthy strings in the environment can be
        any of the following case-insensitive values:

        - ``1``
        - ``true``

    Returns:
        bool:
            True if the environment variable to enable the API logic is truthy,
            otherwise False.
    """

    return os.getenv(ENV_API_ENABLED, "").lower() in ("1", "true")


def get_api_tokens() -> Optional[Tuple[str, str]]:
    """Attempt to pull the API tokens from the environment.

    Returns:
        Optional[Tuple[str, str]]:
            A tuple of the (client_id, client_secret) strings if available/
    """

    token = os.getenv(ENV_API_TOKEN)
    secret = os.getenv(ENV_API_SECRET)

    if token is None or secret is None:
        return None

    return (token, secret)


def get_content_iterator(url: Url) -> Generator[Content, None, None]:
    """Get the appropraite content iterator for the given URL.

    The "appropriate" content iterator is determined by checking the environment
    configuration to see if the end user wishes to enable the API logic vs the
    guesswork logic that we can do without API credentials.

    Args:
        url (~megu.Url):
            The Url the customer passed through the plugin.

    Raises:
        RuntimeError:
            If the API logic path is enabled but no token or secret is defined.

    Returns:
        Generator[~megu.Content, None, None]:
            A content generator for the given URL.
    """

    if is_api_enabled():
        log.debug(f"Using the API logic for fetching Gfycat items for {url}")
        api_tokens = get_api_tokens()
        if api_tokens is None:
            raise RuntimeError(
                f"Expected environment values for {ENV_API_TOKEN!r} and "
                f"{ENV_API_SECRET!r} to be defined"
            )

        return iter_gfycat_content(url, *api_tokens)
    else:
        log.debug(f"Using the guesswork logic for fetching Gfycat items for {url}")
        return iter_guessed_content(url)
