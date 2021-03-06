# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# GPLv3 License <https://choosealicense.com/licenses/gpl-3.0/>

"""Contains minimal and pretty basic utilities for the package."""

from megu import Url


def build_content_id(gfycat_id: str) -> str:
    """Build an appropriate content identification string.

    Args:
        gfycat_id (str):
            The ID of the gfycat content we discovered.

    Returns:
        str:
            The appropriate content identifier.
    """

    return f"gfycat-{gfycat_id!s}"


def get_gfycat_id(url: Url) -> str:
    """Try to extract the gfycat id from the given Url.

    Args:
        url (~megu.Url):
            The Url the user provided to the plugin.

    Raises:
        ValueError:
            If the provided URL doesn't appear to have a path.

    Returns:
        str:
            The extracted gfycat id.
    """

    if len(url.path.segments) <= 0:
        raise ValueError(f"Provided url {url} appears to have no path")

    return url.path.segments[0].split("-")[0]
