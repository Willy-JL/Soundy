import asyncio
import time

from modules import globals, api


async def listener_loop():
    while True:
        media_info = await api.get_media_info()

        if media_info:
            if globals.gui.isHidden():
                globals.timeout = None
                globals.gui.show()

            if not globals.gui.time_scrubber.scrubbing and media_info[1]["position"] != globals.prev_position and media_info[0]["playback_status"] == 4:
                if isinstance(media_info[1]["position"], int):
                    globals.gui.time_scrubber.setValue(media_info[1]["position"])
                else:
                    globals.gui.time_scrubber.setValue(0)
                globals.gui.play_pause.set_state(True)
                globals.prev_position = media_info[1]["position"]
                globals.paused = False
            elif media_info[0]["playback_status"] != 4:
                if isinstance(media_info[1]["position"], int):
                    globals.gui.time_scrubber.setValue(media_info[1]["position"])
                else:
                    globals.gui.time_scrubber.setValue(0)
                globals.gui.play_pause.set_state(False)
                globals.prev_position = media_info[1]["position"]
                globals.paused = True

            if globals.shuffle_mode is None:
                if isinstance(media_info[0]["is_shuffle_active"], bool):
                    globals.shuffle_mode = media_info[0]["is_shuffle_active"]
                else:
                    globals.shuffle_mode = False

            if globals.repeat_mode is None:
                if isinstance(media_info[0]["auto_repeat_mode"], int) and media_info[0]["auto_repeat_mode"] in list(range(3)):
                    globals.repeat_mode = media_info[0]["auto_repeat_mode"]
                else:
                    globals.repeat_mode = 0

            if media_info[0]["is_shuffle_active"] != globals.prev_shuffle:
                if isinstance(media_info[0]["is_shuffle_active"], bool):
                    globals.gui.shuffle.set_state(media_info[0]["is_shuffle_active"])
                else:
                    globals.gui.shuffle.set_state(False)
                globals.prev_shuffle = media_info[0]["is_shuffle_active"]

            if media_info[0]["auto_repeat_mode"] != globals.prev_repeat:
                if isinstance(media_info[0]["auto_repeat_mode"], int) and media_info[0]["auto_repeat_mode"] in list(range(3)):
                    globals.gui.repeat.set_state(media_info[0]["auto_repeat_mode"])
                else:
                    globals.gui.repeat.set_state(0)
                globals.prev_repeat = media_info[0]["auto_repeat_mode"]

            cur_state = f'{media_info[1].get("max_seek_time")}{media_info[1].get("min_seek_time")}{media_info[2].get("artist")}{media_info[2].get("is_spotify")}{media_info[2].get("title")}'

            if cur_state != globals.prev_state:
                globals.gui.update_track_info(media_info[2].get("title"), media_info[2].get("artist"))

                globals.gui.time_scrubber.setMinimum(media_info[1].get("min_seek_time") if isinstance(media_info[1].get("min_seek_time"), int) else 0)
                globals.gui.time_scrubber.setMaximum(media_info[1].get("max_seek_time") if isinstance(media_info[1].get("max_seek_time"), int) else 600000)

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
            if globals.timeout is None:
                globals.timeout = 10
            elif globals.timeout > 0:
                globals.timeout -= 1
            if globals.timeout == 0:
                if not globals.gui.isHidden():
                    globals.gui.hide()
            globals.gui.time_scrubber.setValue(0)
            globals.gui.play_pause.set_state(False)
            globals.prev_position = 0
            globals.paused = True
            globals.gui.update_track_info()
            globals.gui.update_cover_art()
        next_update = time.time() + 0.5
        while time.time() < next_update:
            if not globals.gui.time_scrubber.scrubbing and not globals.paused:
                globals.gui.time_scrubber.setValue(globals.gui.time_scrubber.value() + 100)
            await asyncio.sleep(0.1)

# Example response from api.get_media_info()
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
