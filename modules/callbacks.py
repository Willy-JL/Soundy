# from pprint import pprint
import asyncio
import time

from modules import api, globals


async def update_loop():
    while True:
        media_info = await api.get_media_info()
        # pprint(media_info)

        if media_info:
            if not globals.gui.time_scrubber.scrubbing and media_info[1]["position"] != globals.prev_position and media_info[0]["playback_status"] == 4:
                globals.gui.time_scrubber.setValue(media_info[1]["position"])
                globals.gui.play_pause.set_state(True)
                globals.prev_position = media_info[1]["position"]
                globals.paused = False
            elif media_info[0]["playback_status"] != 4:
                globals.gui.time_scrubber.setValue(media_info[1]["position"])
                globals.gui.play_pause.set_state(False)
                globals.prev_position = media_info[1]["position"]
                globals.paused = True

            if globals.shuffle_mode is None:
                globals.shuffle_mode = media_info[0]["is_shuffle_active"]

            if globals.repeat_mode is None:
                globals.repeat_mode = media_info[0]["auto_repeat_mode"]

            if media_info[0]["is_shuffle_active"] != globals.prev_shuffle:
                globals.gui.shuffle.set_state(media_info[0]["is_shuffle_active"])
                globals.prev_shuffle = media_info[0]["is_shuffle_active"]

            if media_info[0]["auto_repeat_mode"] != globals.prev_repeat:
                globals.gui.repeat.set_state(media_info[0]["auto_repeat_mode"])
                globals.prev_repeat = media_info[0]["auto_repeat_mode"]

            cur_state = f'{media_info[1]["max_seek_time"]}{media_info[1]["min_seek_time"]}{media_info[2]["artist"]}{media_info[2]["is_spotify"]}{media_info[2]["title"]}'

            if cur_state != globals.prev_state:
                globals.gui.update_track_name(media_info[2]["title"])
                globals.gui.update_artist_name(media_info[2]["artist"])

                globals.gui.time_scrubber.setMinimum(media_info[1]["min_seek_time"])
                globals.gui.time_scrubber.setMaximum(media_info[1]["max_seek_time"])

                thumbnail = await api.get_thumbnail(media_info[2])
                if thumbnail[0]:
                    globals.gui.update_cover_art(thumbnail)
                else:
                    globals.gui.update_cover_art()
                globals.prev_state = cur_state
            if globals.blank_cover_art:
                thumbnail = await api.get_thumbnail(media_info[2])
                if thumbnail[0]:
                    globals.gui.update_cover_art(thumbnail)
        else:
            globals.gui.time_scrubber.setValue(0)
            globals.gui.play_pause.set_state(False)
            globals.prev_position = 0
            globals.paused = True
            globals.gui.update_cover_art()
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
