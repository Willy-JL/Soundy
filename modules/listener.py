import asyncio
import time

from modules import globals, api, gui


async def listener_loop():
    globals.loop.create_task(gui.label_loop())
    while True:
        media_info = await api.get_media_info()

        if globals.discord_rpc._discord_rpc is not None:
            presence = {
                'small_image_key': "icon",
                'small_image_text': f"Soundy v{globals.version}"
            }

        if globals.gui.isHidden() and not globals.settings.value("autoHide", 1):
            globals.timeout = None
            globals.gui.show()
            if globals.settings.value("discordRPC", 0) and globals.discord_rpc._discord_rpc is None:
                globals.discord_rpc.initialize('826397574394413076', callbacks={}, log=False)

        if media_info:
            if globals.gui.isHidden():
                globals.timeout = None
                globals.gui.show()
                if globals.settings.value("discordRPC", 0) and globals.discord_rpc._discord_rpc is None:
                    globals.discord_rpc.initialize('826397574394413076', callbacks={}, log=False)

            if not globals.gui.time_scrubber.scrubbing and media_info[1]["position"] != globals.prev_position and media_info[0]["playback_status"] == 4:
                if isinstance(media_info[1]["position"], int) and media_info[1]["position"] != 0:
                    globals.gui.time_scrubber.setValue(media_info[1]["position"])
                    globals.gui.time_scrubber_opacity.setOpacity(1.0)
                else:
                    globals.gui.time_scrubber.setValue(0)
                    globals.gui.time_scrubber_opacity.setOpacity(0.0)
                globals.gui.play_pause.set_state(True)
                globals.prev_position = media_info[1]["position"]
                globals.paused = False
            elif media_info[0]["playback_status"] != 4:
                if isinstance(media_info[1]["position"], int) and media_info[1]["position"] != 0:
                    globals.gui.time_scrubber.setValue(media_info[1]["position"])
                    globals.gui.time_scrubber_opacity.setOpacity(1.0)
                else:
                    globals.gui.time_scrubber.setValue(0)
                    globals.gui.time_scrubber_opacity.setOpacity(0.0)
                globals.gui.play_pause.set_state(False)
                globals.prev_position = media_info[1]["position"]
                globals.paused = True
                if globals.discord_rpc._discord_rpc is not None:
                    presence["large_image_key"] = "pause"
                    presence["large_image_text"] = "*awkward cricket noises*"
                    presence["details"] = media_info[2].get("title")
                    presence["state"] = media_info[2].get("artist")
            if media_info[0]["playback_status"] == 4:
                if globals.discord_rpc._discord_rpc is not None:
                    presence["large_image_key"] = "play"
                    presence["large_image_text"] = "Currently vibing"
                    presence["details"] = media_info[2].get("title")
                    presence["state"] = media_info[2].get("artist")

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
            if globals.settings.value("autoHide", 1):
                if globals.timeout is None:
                    globals.timeout = 5
                elif globals.timeout > 0:
                    globals.timeout -= 1
                if globals.timeout == 0:
                    if not globals.gui.isHidden():
                        globals.gui.hide()
                        if globals.settings.value("discordRPC", 0) and globals.discord_rpc._discord_rpc is not None:
                            globals.discord_rpc.shutdown()
            globals.gui.time_scrubber.setValue(0)
            globals.gui.time_scrubber_opacity.setOpacity(0.0)
            globals.gui.play_pause.set_state(False)
            globals.prev_position = 0
            globals.paused = True
            globals.gui.update_track_info()
            globals.gui.update_cover_art()
            if globals.discord_rpc._discord_rpc is not None:
                presence["large_image_key"] = "pause"
                presence["large_image_text"] = "*awkward cricket noises*"
                presence["details"] = "By WillyJL"
                presence["state"] = "No media detected"

        if globals.discord_rpc._discord_rpc is not None:
            if not globals.paused and media_info and isinstance(media_info[1]["position"], int) and media_info[1]["position"] != 0:
                presence["start_timestamp"] = int(time.time()) - int(media_info[1]["position"] / 1000)
            for item in presence:
                should_update_presence = False
                if not globals.prev_presence: should_update_presence = True
                if not should_update_presence:
                    if item != "start_timestamp" and globals.prev_presence.get(item) != presence.get(item): should_update_presence = True
                    if item == "start_timestamp" and globals.prev_presence.get(item) not in list(range(int(presence.get(item))-6, int(presence.get(item))+7)): should_update_presence = True
                if should_update_presence:
                    globals.discord_rpc.update_presence(**presence)
                    globals.discord_rpc.update_connection()
                    globals.discord_rpc.run_callbacks()
                    break
            globals.prev_presence = {}
            for item in presence:
                globals.prev_presence[item] = presence[item]

        next_update = time.time() + 1
        while time.time() < next_update:
            if not globals.gui.time_scrubber.scrubbing and not globals.paused:
                globals.gui.time_scrubber.setValue(globals.gui.time_scrubber.value() + 100)
            await asyncio.sleep(0.1)
        globals.gui.save_geometry()


# Example response from api.get_media_info()
"""
(
    0: {
        'auto_repeat_mode': 0,
        'is_shuffle_active': True,
        'playback_status': 4
    },
    1: {
        'max_seek_time': 130370,
        'min_seek_time': 0,
        'position': 24249
    },
    2: {
        'artist': 'Ghostface Playa',
        'is_spotify': True,
        'thumbnail': <_winrt_Windows_Storage_Streams.IRandomAccessStreamReference object at 0x000001AD6D5E2950>,
        'title': 'Bitch Try to Make a Move'
    }
)
"""
