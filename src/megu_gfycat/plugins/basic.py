# -*- encoding: utf-8 -*-
# Copyright (c) 2021 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""Contains the basic gfycat.com Megu plugin."""

from pathlib import Path
from typing import Generator

from megu import BasePlugin, Content, Manifest, Url

from ..helpers import get_content_iterator, is_known_url


class GfycatBasicPlugin(BasePlugin):
    """The basic Gfycat.com plugin.

    This plugin is mean to handle URLs to a single gfycat item ``gfycat.com/<id>``.
    This plugin does not attempt to iterate over multiple items in any way.
    """

    name = "Gfycat Plugin"
    domains = {"gfycat.com"}

    def can_handle(self, url: Url) -> bool:
        """Determine if the given URL can be handled by the current plugin.

        Args:
            url (~megu.Url):
                The Url the user requested to download.

        Returns:
            bool:
                True if the current plugin can handle the user requested URL,
                otherwise False.
        """

        return is_known_url(url)

    def extract_content(self, url: Url) -> Generator[Content, None, None]:
        """Extract Gfycat content from the given URL.

        Args:
            url (~megu.Url):
                The Url the user requested to download content from.

        Yields:
            ~megu.Content:
                Any content the plugin discovers.
        """

        yield from get_content_iterator(url)

    def merge_manifest(self, manifest: Manifest, to_path: Path) -> Path:
        """Merge the downloaded artifacts from the given manifest to the desired path.

        Args:
            manifest (~megu.Manifest):
                The manifest of the downloaded artifacts.
            to_path (~pathlib.Path):
                The path the artifacts within the manifest should be merged to.

        Raises:
            ValueError:
                If the given manifest doesn't have exactly 1 artifact.

        Returns:
            ~pathlib.Path:
                The resulting path the artifacts were merged to.
                This should always be ``to_path``.
        """

        if len(manifest.artifacts) != 1:
            raise ValueError(
                f"Expected only 1 artifact in the manifest {manifest!r}, "
                f"received {len(manifest.artifacts)}"
            )

        _, artifact_path = manifest.artifacts[0]
        artifact_path.rename(to_path)
        return to_path
