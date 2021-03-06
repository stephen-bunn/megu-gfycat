# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains the functionality for guessing content endpoints."""

from typing import Generator

from megu import Content, HttpMethod, HttpResource, Meta, Url
from megu.helpers import get_soup, http_session
from megu.log import instance as log

from .constants import CONTENT_ENTRIES
from .utils import build_content_id, get_gfycat_id


def find_gfycat_id(url: Url) -> str:
    """Attempt to discover the Gfycat item internal ID from the given URL.

    This requires that we fetch the DOM of the given URL and try to discover the ID by
    looking at the main video element on the page and pull the internal ID from the
    content they have dropped as sources.

    .. warning::
        This is tying the functionality of the non-api solution to the structure of DOM
        which I hate doing. But this solution has worked for me for the past few years.
        May need to update this to something more sustainable in the future.

    Args:
        url (~megu.Url):
            The Url the user provided through the plugin.

    Raises:
        ValueError:
            If the request for page content fails.
        ValueError:
            If the main video element could not be found on the page DOM.
        ValueError:
            If the thumbnail/poster URL could not be pulled off as a source from the
            main video element.
        ValueError:
            If the found thumbnail URL doesn't appear to be formatted correctly.

    Returns:
        str:
            The best guess we can come up with for the internal Gfycat content ID.
    """

    with http_session() as session:
        log.debug(f"Fetching HTML page content from {url}")
        response = session.get(url.url)
        if not response.ok:
            raise ValueError(
                f"Request to fetch site content at {url} resolved to failed response "
                f"{response!r}"
            )

        soup = get_soup(response.text)
        log.debug(f"Looking for main video element on HTML page content from {url}")
        video_element = soup.find("video", {"class": "video media"})
        if not video_element:
            raise ValueError(f"Could not find video element in the page from {url}")

        log.debug(
            f"Extracting the poster URL from the discovered video element from {url}"
        )
        video_poster = video_element.get("poster")
        if not video_poster:
            raise ValueError(
                f"Could not fetch video poster from the video element {video_element!r}"
            )

        log.debug(f"Extracting the internal gfycat ID from the poster url from {url}")
        video_poster_url = Url(video_poster)
        return get_gfycat_id(video_poster_url)


def iter_content(url: Url) -> Generator[Content, None, None]:
    """Iterate over the content we know should likely exist.

    .. note::
        For each guessed content entry, we are making a HEAD request to determine
        existence and content size.

    Args:
        url (~megu.Url):
            The Url the user provided through the plugin.

    Yields:
        ~megu.Content:
            The content that we have guessed and verified exists.
    """

    gfycat_id = find_gfycat_id(url)
    gfycat_meta = Meta(id=gfycat_id)

    with http_session() as session:
        for content_entry in CONTENT_ENTRIES:
            content_url = content_entry.url_template.format(id=gfycat_id)
            response = session.head(content_url)
            if not response.ok:
                log.warning(
                    f"Content entry {content_entry!r} doesn't appear to exist for "
                    f"gfycat {gfycat_id!r}, skipping content entry"
                )
                continue

            yield Content(
                id=build_content_id(gfycat_id, content_entry.type),
                url=url.url,
                size=int(response.headers.get("content-length", 0)),
                type=content_entry.mimetype,
                quality=content_entry.quality,
                resources=[HttpResource(method=HttpMethod.GET, url=content_url)],
                meta=gfycat_meta,
            )
