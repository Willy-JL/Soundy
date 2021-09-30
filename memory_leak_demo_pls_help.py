from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
from pympler.tracker import SummaryTracker
import asyncio
import gc


async def get_media_info():
    # Memory leaking calls
    sessions = await MediaManager.request_async()
    current_session = sessions.get_current_session()
    await current_session.try_get_media_properties_async()

    # Force garbage collect, does nothing
    gc.collect()

    return


if __name__ == '__main__':

    # Pause to check starting memory usage (I used task manager)
    # ~ 30 MB in my case
    input()

    # Track objects and sizes
    tracker = SummaryTracker()

    # 500 iterations is a good example amount
    for _ in range(500):
        # Leak memory
        asyncio.run(get_media_info())

        # Force garbage collect, does nothing
        gc.collect()

    # Print info on object count and size differences
    # Will always show ~ 1 MB of leaks, no matter how many iterations
    tracker.print_diff()

    # Pause to check ending memory usage (I used task manager)
    # ~ 60 MB in my case with 500 iterations
    # ~ 330 MB with 5000 iterations
    # ~ 3.2 GB with 50000 iterations
    input()
