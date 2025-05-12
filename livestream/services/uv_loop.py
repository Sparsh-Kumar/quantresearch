
import asyncio
import uvloop

def uv_event_loop():
  asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


