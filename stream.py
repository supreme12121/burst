import asyncio
import logging
import os
import sys
import time

import discord
from discord.ext.native_voice import FFmpegMediaSource, StreamClient, VoiceClient

logging.basicConfig(level=logging.INFO)  # change to DEBUG if you need detail

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    print("token not entered")
    sys.exit(1)

CHANNEL_ID = 1575118260515635221  # voice channel id (must be a number)
VIDEO_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.mp4")

client = discord.Client()
started = False  # on_ready can fire more than once


async def stream_forever(channel):
    voice = await channel.connect(cls=VoiceClient)
    print(f"[+] Joined {channel}")
    stream = await voice.create_stream(cls=StreamClient)
    print("[+] Stream created")
    loop = asyncio.get_running_loop()

    while True:
        done = asyncio.Event()

        def after(error):
            # runs on the player thread, so hand off to the event loop
            if error:
                print(f"[!] Player error: {error!r}")
            loop.call_soon_threadsafe(done.set)

        # a source can't be reused, so build a fresh one every round
        source = FFmpegMediaSource.from_file(
            VIDEO_FILE,
            "H264",
            width=1280,
            height=720,
            fps=30,
            bitrate=4_000_000,
        )
        began = time.monotonic()
        stream.play(source, after=after)
        print("[+] Playing (restarts automatically when it ends)")
        await done.wait()

        if not voice.is_connected():
            raise ConnectionError("voice disconnected")
        if time.monotonic() - began < 3:
            await asyncio.sleep(5)  # ended instantly, so avoid a tight crash loop


async def supervisor(channel):
    while True:
        try:
            await stream_forever(channel)
        except Exception as e:
            logging.exception("Stream stopped")
            print(f"[!] {e!r}. Restarting in 15s...")
        # best-effort cleanup before retrying
        for vc in list(client.voice_clients):
            try:
                await vc.disconnect(force=True)
            except Exception:
                pass
        await asyncio.sleep(15)


@client.event
async def on_ready():
    global started
    if started:
        return
    started = True
    print(f"[+] Logged in as {client.user}")
    print("[*] video exists:", os.path.exists(VIDEO_FILE))
    channel = client.get_channel(CHANNEL_ID) or await client.fetch_channel(CHANNEL_ID)
    client.loop.create_task(supervisor(channel))


client.run(TOKEN)
