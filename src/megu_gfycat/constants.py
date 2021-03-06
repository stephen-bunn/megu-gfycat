# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# GPLv3 License <https://choosealicense.com/licenses/gpl-3.0/>

"""Contains constants used through multiple places within the package."""

import re
from typing import List, NamedTuple, Pattern, Set

# Optional environment configuration names
ENV_API_ENABLED = "MEGU_GFYCAT_API_ENABLED"
ENV_API_TOKEN = "MEGU_GFYCAT_API_TOKEN"
ENV_API_SECRET = "MEGU_GFYCAT_API_SECRET"

# URL patterns that we know how to handle
BASIC_PATTERN = re.compile(
    r"^https:?://(?:www\.)?gfycat\.com/(?:gifs/detail)?"
    r"(?P<id>[a-zA-Z]+)[a-zA-Z0-9-]*/?$"
)
RAW_PATTERN = re.compile(
    r"^https:?://[a-z]+\.gfycat\.com/(?P<id>[a-zA-Z]+)[a-zA-Z0-9_-]*\.[a-zA-Z0-9]+$"
)
VALID_PATTERNS: Set[Pattern] = {BASIC_PATTERN, RAW_PATTERN}

# Template for producing very basic Gfycat source URLs
GFYCAT_URL_TEMPLATE = "https://gfycat.com/{id!s}"


class ContentEntry(NamedTuple):
    """Helps describe a content entry that we want to extract from Gfycat."""

    name: str
    type: str
    extension: str
    mimetype: str
    quality: float
    url_template: str


CONTENT_ENTRIES: List[ContentEntry] = [
    ContentEntry(
        name="MP4 Video",
        type="mp4",
        extension=".mp4",
        mimetype="video/mp4",
        quality=1.0,
        url_template="https://giant.gfycat.com/{id}.mp4",
    ),
    ContentEntry(
        name="WEBM Video",
        type="webm",
        extension=".webm",
        mimetype="video/webm",
        quality=0.5,
        url_template="https://giant.gfycat.com/{id}.webm",
    ),
    ContentEntry(
        name="5MB Gif Image",
        type="max5mbGif",
        extension=".gif",
        mimetype="image/gif",
        quality=0.25,
        url_template="https://thumbs.gfycat.com/{id}-size_restricted.gif",
    ),
    ContentEntry(
        name="2MB Gif Image",
        type="max2mbGif",
        extension=".gif",
        mimetype="image/gif",
        quality=0.10,
        url_template="https://thumbs.gfycat.com/{id}-small.gif",
    ),
    ContentEntry(
        name="1MB Gift Image",
        type="max1mbGif",
        extension=".gif",
        mimetype="image/gif",
        quality=0.05,
        url_template="https://thumbs.gfycat.com/{id}-max-1mb.gif",
    ),
]
