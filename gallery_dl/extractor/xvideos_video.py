# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
"""Extractor for videos on https://www.xvideos.com/"""

import re

from .common import Extractor, Message
from .. import text


class XVideosVideoExtractor(Extractor):
    """Base class for rule34video extractors"""
    category = "xvideos_videos"
    directory_fmt = ("{category}", "{id}", "{title}")
    filename_fmt = "{id}_{title}.{extension}"
    archive_fmt = "{id}"
    root = "https://www.xvideos.com"
    pattern = r"(?:https?://)?(?:www\.)?xvideos\.com/video\.(?P<video_id>[^/]+)/(?:[^/?#]+)"
    example = "https://xvideos.com/video.VIDEOID/VIDEO-TITLE"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.url = match[0]
        self.video_id = match[1]

    def items(self):
        page = self.request(self.url).text
        self.data = data = self.metadata(page)
        data["extension"] = "mp4"
        yield Message.Directory, data
        url = "ytdl:" +self.url
        data["url"] = url
        yield Message.Url, url, data

    def metadata(self, page):
        title = text.extract(
            text.extract(page, '<h2 class="page-title">', "</h2>")[0], "", "<span"
        )[0]
        duration = text.extract(page, '<span class="duration">', "</span>")[0]
        tags = text.split_html(
            text.extract(
                text.extract(
                    page,
                    '<div class="video-metadata video-tags-list',
                    "</div>",
                )[0],
                "<li>",
                "</ul>",
            )[0]
        )[0:-2]
        views = text.extract(page, '<div id="v-views">', "</div>")[0]
        if views:
            views = int(text.split_html(views)[0].replace(",", ""))
        else:
            views = 0
        artist = []

        return {
            "title": title,
            "views": views,
            "duration": duration,
            "artist": artist,
            "tags": tags,
            "id": self.video_id
        }
