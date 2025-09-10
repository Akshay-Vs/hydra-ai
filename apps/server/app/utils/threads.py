import asyncio
import threading


def fire_and_forget(coro):
    def runner():
        asyncio.run(coro)

    threading.Thread(target=runner, daemon=True).start()
