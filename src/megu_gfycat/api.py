# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains the functionality for fetching content via the Gfycat API."""

import json
from datetime import datetime
from typing import Dict, Generator, List, Optional, TypedDict

from megu import Content, HttpMethod, HttpResource, Meta, Url
from megu.helpers import disk_cache, http_session
from megu.log import instance as log

from .constants import CONTENT_ENTRIES, GFYCAT_URL_TEMPLATE
from .utils import build_content_id, get_gfycat_id

DISK_CACHE_NAME = "megu_gfycat"
DISK_CACHE_KEY = "bearer_token"

API_URL_BASE = "https://api.gfycat.com/v1/"
API_URL_DATA = API_URL_BASE + "gfycats/"
API_URL_AUTH = API_URL_BASE + "oauth/token/"


class GfycatContent(TypedDict):
    """Describes the API payload dictionary for some Gfycat content."""

    url: str
    size: int
    width: int
    height: int


class GfycatItem(TypedDict):
    """Describes the API payload dictionary for a Gfycat item."""

    # NOTE: Although there are URLs present on the top layer of the response
    # (mp4Url, webmUrl, etc.), these have been flaky in my past experience.
    # I would recommend only relying on the data out of `content_urls`.

    avgColor: str
    content_urls: Dict[str, GfycatContent]
    createDate: int
    description: str
    dislikes: str
    domainWhitelist: List[str]
    extraLemmas: str
    frameRate: float
    gfyId: str
    gfyName: str
    gfyNumber: str
    hasAudio: bool
    hasTransparency: bool
    height: int
    languageCategories: Optional[List[str]]
    languageText: str
    likes: str
    max1mbGif: str
    max2mbGif: str
    max5mbGif: str
    miniPosterUrl: str
    miniUrl: str
    mobilePosterUrl: str
    mobileUrl: str
    mp4Size: int
    mp4Url: str
    nsfw: str
    numFrames: float
    posterUrl: str
    published: int
    source: int
    tags: List[str]
    thumb100PosterUrl: str
    title: str
    url: str
    userDisplayName: str
    username: str
    views: int
    webmSize: int
    webmUrl: str
    width: int


class GfycatResponse(TypedDict):
    """Describes the API payload for a successful Gfycat item response."""

    gfyItem: GfycatItem


class AuthResponse(TypedDict):
    """Descibes the API payload for a sucessful Gfycat OAuth token response."""

    token_type: str
    scope: str
    expires_in: int
    access_token: str


def get_auth_response(token: str, secret: str) -> AuthResponse:
    """Request an OAuth bearer token.

    Args:
        token (str):
            The "client_id" for the registered Gfycat application.
        secret (str):
            The "client_secret" for the registered Gfycat application.

    Raises:
        ValueError:
            If the request for the OAuth bearer token fails.

    Returns:
        AuthResponse:
            The successful response payload of the auth request.
    """

    with http_session() as session:
        log.debug(f"Fetching OAuth token response for client {token!r}")
        response = session.post(
            API_URL_AUTH,
            json.dumps(
                {
                    "grant_type": "client_credentials",
                    "client_id": token,
                    "client_secret": secret,
                }
            ),
        )

        if not response.ok:
            raise ValueError(
                f"Request for bearer token to {API_URL_AUTH} resolved to "
                f"failed response {response!r}"
            )

        data: AuthResponse = response.json()
        return data


def get_bearer_token(token: str, secret: str) -> str:
    """Fetch the OAuth bearer token to use for requests.

    Args:
        token (str):
            The "client_id" for the registered Gfycat application.
        secret (str):
            The "client_secret" for the registered Gfycat application.

    Raises:
        ValueError:
            If the request for a bearer token returns an invalid payload.

    Returns:
        str:
            The bearer token to use for further Gfycat requests.
    """

    with disk_cache(DISK_CACHE_NAME) as cache:
        bearer_token = cache.get(DISK_CACHE_KEY, default=None)
        if bearer_token is not None:
            log.debug(
                f"Using cached OAuth token from {DISK_CACHE_KEY!r} in cache "
                f"{cache.directory}"
            )
            return bearer_token

        auth_response = get_auth_response(token, secret)
        bearer_token = auth_response["access_token"]
        if not bearer_token:
            raise ValueError(
                f"Request for bearer token to {API_URL_AUTH} returned invalid payload "
                f"{auth_response!r}"
            )

        log.debug(
            f"Fetched OAuth token for client {token!r}, caching under "
            f"{DISK_CACHE_KEY!r} in cache {cache.directory}"
        )

        # HACK: probably deprecated by now, but we've seen instances where `expires_in`
        # doesn't come through the payload all the time.
        # Defaulting to 3600 (from Gfycat's docs) which we are just assuming is safe.
        cache.set(
            DISK_CACHE_KEY,
            bearer_token,
            expire=auth_response.get("expires_in", 3600),
        )
        return bearer_token


def get_gfycat_response(gfycat_id: str, token: str, secret: str) -> GfycatResponse:
    """Request the Gfycat data for a given Gfycat item ID.

    Args:
        gfycat_id (str):
            The ID of the Gfycat item we want to get the data for.
        token (str):
            The "client_id" for the registered Gfycat application.
        secret (str):
            The "client_secret" for the registered Gfycat application.

    Raises:
        ValueError:
            If the request for the Gfycat item failed.

    Returns:
        GfycatResponse:
            The Gfycat item API payload.
    """

    gfycat_url = API_URL_DATA + gfycat_id
    with http_session() as session:
        session.headers.update(
            {"Authorization": f"Bearer {get_bearer_token(token, secret)!s}"}
        )

        log.debug(f"Fetching gfycat data from {gfycat_url!r} using client {token!r}")
        response = session.get(gfycat_url)
        if not response.ok:
            raise ValueError(
                f"Request for gfycat item {gfycat_id!r} resolved to failed response "
                f"{response!r}"
            )

        data: GfycatResponse = response.json()
        if "error" in data:
            raise ValueError(
                f"Request for gfycat item {gfycat_id!r} returned invalid payload "
                f"{data!r}"
            )

        return data


def iter_content(url: Url, token: str, secret: str) -> Generator[Content, None, None]:
    """Iterate over the content retrieved via the Gfycat API for a given Url.

    Args:
        url (Url):
            The URL of the Gfycat item the user provided through the plugin.
        token (str):
            The "client_id" for the registered Gfycat application.
        secret (str):
            The "client_secret" for the registered Gfycat application.

    Yields:
        ~megu.Content:
            Content pulled from the Gfycat API.
    """

    gfycat_id = get_gfycat_id(url)
    gfycat_response = get_gfycat_response(gfycat_id, token, secret)

    gfycat_item = gfycat_response["gfyItem"]
    gfycat_url = GFYCAT_URL_TEMPLATE.format(id=gfycat_item["gfyId"])

    meta = Meta(
        id=gfycat_item["gfyId"],
        description=gfycat_item["description"],
        publisher=gfycat_item["username"],
        published_at=datetime.fromtimestamp(gfycat_item["createDate"]),
        thumbnail=gfycat_item["posterUrl"],
    )

    gfycat_content = gfycat_item["content_urls"]
    for content_entry in CONTENT_ENTRIES:
        if content_entry.type in gfycat_content:
            data = gfycat_content[content_entry.type]

            yield Content(
                id=build_content_id(gfycat_id, content_entry.type),
                url=gfycat_url,
                size=data["size"],
                type=content_entry.mimetype,
                quality=content_entry.quality,
                resources=[HttpResource(method=HttpMethod.GET, url=data["url"])],
                meta=meta,
                extra=gfycat_response,
            )
