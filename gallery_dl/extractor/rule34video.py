# -*- coding: utf-8 -*-

# Copyright 2019-2023 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.rule34video.com/"""

import re

from .common import Extractor, Message
from .. import text


class Rule34video(Extractor):
    """Base class for rule34video extractors"""

    category = "rule34video"
    directory_fmt = ("{category}", "{artist}", "{title}")
    filename_fmt = "{id}_{title}.{extension}"
    archive_fmt = "{id}"
    root = "https://rule34video.com"
    pattern = r"(?:https?://)?rule34video\.com/video/(\d+)/(?:[^/?#]+)"
    example = "https://rule34video.com/video/VIDEO"

    def __init__(self, match):
        Extractor.__init__(self, match)
        self.url = match[0]

    def items(self):
        page = self.request(self.url).text
        self.data = data = self.metadata(page)
        data["extension"] = "mp4"
        yield Message.Directory, data
        url = "ytdl:" + self.url
        data["url"] = url
        yield Message.Url, url, data

    def metadata(self, page):
        extr = text.extract_from(page)
        title = extr('<h1 class="title_video">', "</h1>")
        views = int(
            re.search(
                r"\(([\d,\.]*)\)",
                text.split_html(
                    extr(
                        '<svg class="custom-svg custom-eye">',
                        "</span>",
                    )
                )[0],
            )
            .group(1)
            .replace(",", "")
        )
        duration = text.split_html(
            extr(
                '<svg class="custom-svg custom-time">',
                "</span>",
            )
        )[0]
        artist = text.split_html(
            text.extr(page, '<div class="label">Artist', '<div class="col">')
        )
        tags = text.extr(
            text.extr(page, '<div id="tab_video_info"', '<div id="tab_report_rrror"'),
            '<div class="wrap">',
            '<div class="row row_spacer"',
        )
        tags = text.split_html(tags)[1:-6]
        video_id = text.extr(
            text.extr(page, "flashvars = {", "};"), "video_id: '", "',"
        )

        return {
            "title": title,
            "views": views,
            "duration": duration,
            "artist": artist,
            "tags": tags,
            "id": video_id,
        }
