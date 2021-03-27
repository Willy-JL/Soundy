from PyQt5.QtGui import QPixmap
import asyncio
import time

from modules import api, globals


async def update_loop():
    while True:
        media_info = await api.get_media_info()

        if media_info:
            if not globals.gui.time_scrubber.scrubbing and media_info[1]["position"] != globals.prev_position and media_info[0]["playback_status"] == 4:
                globals.gui.time_scrubber.setValue(media_info[1]["position"])
                globals.prev_position = media_info[1]["position"]
                globals.paused = False
            elif media_info[0]["playback_status"] == 5:
                globals.gui.time_scrubber.setValue(media_info[1]["position"])
                globals.prev_position = media_info[1]["position"]
                globals.paused = True

            cur_state = f'{media_info[1]["max_seek_time"]}{media_info[1]["min_seek_time"]}{media_info[2]["artist"]}{media_info[2]["is_spotify"]}{media_info[2]["title"]}'

            if cur_state != globals.prev_state:
                globals.gui.update_track_name(media_info[2]["title"])
                globals.gui.update_artist_name(media_info[2]["artist"])

                globals.gui.time_scrubber.setMinimum(media_info[1]["min_seek_time"])
                globals.gui.time_scrubber.setMaximum(media_info[1]["max_seek_time"])

                pixmap = await api.get_thumbnail(media_info[2])
                if pixmap:
                    globals.gui.update_cover_art(pixmap)
                else:
                    globals.blank_cover_art = True
                    pixmap = QPixmap("resources/icon_small.png")
                    globals.gui.update_cover_art(pixmap)
                globals.prev_state = cur_state
            globals.app.processEvents()
        if globals.blank_cover_art:
            pixmap = await api.get_thumbnail(media_info[2])
            if pixmap:
                globals.gui.update_cover_art(pixmap)
                globals.blank_cover_art = False
        next_update = time.time() + 1
        while time.time() < next_update:
            if not globals.gui.time_scrubber.scrubbing and not globals.paused:
                globals.gui.time_scrubber.setValue(globals.gui.time_scrubber.value() + 10)
            await asyncio.sleep(0.01)

"""
(
    {
        'auto_repeat_mode': 0,
        'is_shuffle_active': True,
        'playback_status': 4
    },
    {
        'max_seek_time': 130370,
        'min_seek_time': 0,
        'position': 24249
    },
    {
        'artist': 'Ghostface Playa',
        'is_spotify': True,
        'thumbnail': <_winrt_Windows_Storage_Streams.IRandomAccessStreamReference object at 0x000001AD6D5E2950>,
        'title': 'Bitch Try to Make a Move'
    }
)
"""
