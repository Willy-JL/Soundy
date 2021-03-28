from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
from winrt.windows.storage.streams import DataReader, Buffer, InputStreamOptions
from winrt.windows.foundation import TimeSpan
from PIL import Image, UnidentifiedImageError
from PyQt5.QtGui import QImage, QPixmap
from colorthief import ColorThief
from qasync import asyncSlot
from io import BytesIO

from modules import globals


async def get_media_session():
    sessions = await MediaManager.request_async()
    return sessions.get_current_session()


async def get_media_info():
    current_session = await get_media_session()
    if current_session:

        state = current_session.get_playback_info()
        state_dict = {song_attr: state.__getattribute__(song_attr) for song_attr in dir(state) if song_attr[0] != '_' and song_attr != 'controls' and song_attr != 'playback_rate' and song_attr != 'playback_type'}

        timeline = current_session.get_timeline_properties()
        timeline_dict = {song_attr: int(timeline.__getattribute__(song_attr).duration / 10000) for song_attr in dir(timeline) if song_attr[0] != '_' and isinstance(timeline.__getattribute__(song_attr), TimeSpan) and song_attr != 'end_time' and song_attr != 'start_time'}

        properties = await current_session.try_get_media_properties_async()
        properties_dict = {song_attr: properties.__getattribute__(song_attr) for song_attr in dir(properties) if song_attr[0] != '_' and song_attr != 'album_artist' and song_attr != 'album_title' and song_attr != 'album_track_count' and song_attr != 'genres' and song_attr != 'playback_type' and song_attr != 'subtitle' and song_attr != 'track_number'}
        properties_dict['is_spotify'] = (current_session.source_app_user_model_id == 'Spotify.exe')

        return state_dict, timeline_dict, properties_dict

    return None


@asyncSlot()
async def play_pause(*args):
    current_session = await get_media_session()
    if current_session:
        if globals.paused:
            globals.gui.play_pause.set_state("playing")
        else:
            globals.gui.play_pause.set_state("paused")
        await current_session.try_toggle_play_pause_async()


@asyncSlot()
async def skip_prev(*args):
    current_session = await get_media_session()
    if current_session:
        await current_session.try_skip_previous_async()


@asyncSlot()
async def skip_next(*args):
    current_session = await get_media_session()
    if current_session:
        await current_session.try_skip_next_async()


async def set_shuffle(enabled: bool):
    current_session = await get_media_session()
    if current_session:
        await current_session.try_change_shuffle_active_async(enabled)


async def set_repeat(mode: int):
    """0 = Disabled, 1 = Single, 2 = Queue"""
    current_session = await get_media_session()
    if current_session:
        await current_session.try_change_auto_repeat_mode_async(mode)


async def seek(position: int):
    current_session = await get_media_session()
    if current_session:
        await current_session.try_change_playback_position_async(position * 10000)


def find_colors(palette):
    results = []
    for color in palette:
        lightness = sum(color) / 3
        results.append([color, lightness])
    results.sort(key=lambda x: x[1])
    return results[0], results[-1]


async def read_stream_into_buffer(stream_ref, buffer):
    readable_stream = await stream_ref.open_read_async()
    await readable_stream.read_async(buffer, buffer.capacity, InputStreamOptions.READ_AHEAD)


async def get_thumbnail(media_info: dict):
    thumb_stream_ref = media_info['thumbnail']
    thumb_read_buffer = Buffer(5000000)

    try:
        await read_stream_into_buffer(thumb_stream_ref, thumb_read_buffer)
    except AttributeError:
        return None, None

    buffer_reader = DataReader.from_buffer(thumb_read_buffer)
    byte_buffer = buffer_reader.read_bytes(thumb_read_buffer.length)

    binary = BytesIO()
    binary.write(bytearray(byte_buffer))
    binary.seek(0)

    try:
        img = Image.open(binary)

        if media_info["is_spotify"]:
            img = img.crop((33, 0, 267, 234))

        img = img.resize((69, 69))

        binary2 = BytesIO()
        img.save(binary2, format='png')
        binary2.seek(0)
        image_data = binary2.read()
        qimg = QImage.fromData(image_data)

        binary.seek(0)
        color_thief = ColorThief(binary)
        palette = color_thief.get_palette(color_count=6)
        colors = find_colors(palette)

        return QPixmap.fromImage(qimg), colors

    except UnidentifiedImageError:
        return None, None
