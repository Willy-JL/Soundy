from modules import api, globals
import asyncio


async def update_loop():
    while True:
        await asyncio.sleep(1)
        await update_run()



async def update_run():
        media_info = await api.get_media_info()

        cur_state = f'{media_info[1]["max_seek_time"]}{media_info[1]["min_seek_time"]}{media_info[2]["artist"]}{media_info[2]["is_spotify"]}{media_info[2]["title"]}'

        if cur_state != globals.prev_state:
            globals.gui.update_track_name(" " + media_info[2]["title"])
            globals.gui.update_artist_name(" " + media_info[2]["artist"])

            pixmap = await api.get_thumbnail(media_info[2])
            if pixmap:
                globals.gui.update_cover_art(pixmap)
            globals.prev_state = cur_state
