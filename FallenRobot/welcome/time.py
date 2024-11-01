from os import getenv
from pyrogram import filters
from dotenv import load_dotenv
import sukh
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()

TIME_ZONE= "Asia/Kolkata"


#time zone
TIME_ZONE = pytz.timezone(sukh.TIME_ZONE)
scheduler = AsyncIOScheduler(timezone=TIME_ZONE)
