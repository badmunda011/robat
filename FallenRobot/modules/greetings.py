from html import escape
from secrets import choice
from traceback import format_exc

from pyrogram import enums, filters
from pyrogram.enums import ChatMemberStatus as CMS
from pyrogram.errors import ChatAdminRequired, RPCError
from pyrogram.types import ChatMemberUpdated, Message

from FallenRobot import LOGGER
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator
from FallenRobot import telethn as client
from FallenRobot import pbot
from telethon import events
from FallenRobot.events import register
from FallenRobot.welcome.antispam_db import GBan
from FallenRobot.welcome.greetings_db import Greetings
from FallenRobot.welcome.supports import get_support_staff
from FallenRobot.welcome.cmd_senders import send_cmd
from FallenRobot.welcome.kbhelpers import ikb
from FallenRobot.welcome.msg_types import Types, get_wlcm_type
from FallenRobot.welcome.parser import escape_markdown, mention_html
from FallenRobot.welcome.string import (build_keyboard, escape_invalid_curly_brackets,
                                 parse_button)
from FallenRobot import (
    BOT_ID,
)

# Initialize
gdb = GBan()

DEV_USERS = get_support_staff("dev")

ChatType = enums.ChatType


async def escape_mentions_using_curly_brackets_wl(
    m: ChatMemberUpdated,
    n: bool,
    text: str,
    parse_words: list,
) -> str:
    teks = await escape_invalid_curly_brackets(text, parse_words)
    if n:
        user = m.new_chat_member.user if m.new_chat_member else m.from_user
    else:
        user = m.old_chat_member.user if m.old_chat_member else m.from_user
    if teks:
        teks = teks.format(
            first=escape(user.first_name),
            last=escape(user.last_name or user.first_name),
            fullname=" ".join(
                [
                    escape(user.first_name),
                    escape(user.last_name),
                ]
                if user.last_name
                else [escape(user.first_name)],
            ),
            username=(
                "@" + (await escape_markdown(escape(user.username)))
                if user.username
                else (await (mention_html(escape(user.first_name), user.id)))
            ),
            mention=await (mention_html(escape(user.first_name), user.id)),
            chatname=escape(m.chat.title)
            if m.chat.type != ChatType.PRIVATE
            else escape(user.first_name),
            id=user.id,
        )
    else:
        teks = ""

    return teks

@pbot.on_message(filters.command("cleanwelcome"))
async def cleanwlcm(_, m: Message):
    db = Greetings(m.chat.id)
    status = db.get_current_cleanwelcome_settings()
    args = m.text.split(" ", 1)

    if len(args) >= 2:
        if args[1].lower() == "on":
            db.set_current_cleanwelcome_settings(True)
            await m.reply_text("Turned on!")
            return
        if args[1].lower() == "off":
            db.set_current_cleanwelcome_settings(False)
            await m.reply_text("Turned off!")
            return
        await m.reply_text("what are you trying to do ??")
        return
    await m.reply_text(f"Current settings:- {status}")
    return

@pbot.on_message(filters.command("cleangoodbye"))
async def cleangdbye(_, m: Message):
    db = Greetings(m.chat.id)
    status = db.get_current_cleangoodbye_settings()
    args = m.text.split(" ", 1)

    if len(args) >= 2:
        if args[1].lower() == "on":
            db.set_current_cleangoodbye_settings(True)
            await m.reply_text("Turned on!")
            return
        if args[1].lower() == "off":
            db.set_current_cleangoodbye_settings(False)
            await m.reply_text("Turned off!")
            return
        await m.reply_text("what are you trying to do ??")
        return
    await m.reply_text(f"Current settings:- {status}")
    return


@client.on(events.NewMessage(pattern="^/cleanservice ?(.*)"))
async def cleanservice(_, m: Message):
    db = Greetings(m.chat.id)
    status = db.get_current_cleanservice_settings()
    args = m.text.split(" ", 1)

    if len(args) >= 2:
        if args[1].lower() == "on":
            db.set_current_cleanservice_settings(True)
            await m.reply_text("Turned on!")
            return
        if args[1].lower() == "off":
            db.set_current_cleanservice_settings(False)
            await m.reply_text("Turned off!")
            return
        await m.reply_text("what are you trying to do ??")
        return
    await m.reply_text(f"Current settings:- {status}")
    return


@pbot.on_message(filters.command("setwelcome"))
async def save_wlcm(_, m: Message):
    db = Greetings(m.chat.id)
    if m and not m.from_user:
        return
    args = m.text.split(None, 1)

    if len(args) >= 4096:
        await m.reply_text(
            "Word limit exceed !!",
        )
        return
    if not (m.reply_to_message and m.reply_to_message.text) and len(m.command) == 0:
        await m.reply_text(
            "Error: There is no text in here! and only text with buttons are supported currently !",
        )
        return
    text, msgtype, file = await get_wlcm_type(m)
    if not m.reply_to_message and msgtype == Types.TEXT and len(m.command) <= 2:
        await m.reply_text(f"<code>{m.text}</code>\n\nError: There is no data in here!")
        return

    if not text and not file:
        await m.reply_text(
            "Please provide some data!",
        )
        return

    if not msgtype:
        await m.reply_text("Please provide some data for this to reply with!")
        return

    db.set_welcome_text(text,msgtype,file)
    await m.reply_text("Saved welcome!")
    return


@pbot.on_message(filters.command("setgoodbye"))
async def save_gdbye(_, m: Message):
    db = Greetings(m.chat.id)
    if m and not m.from_user:
        return
    args = m.text.split(None, 1)

    if len(args) >= 4096:
        await m.reply_text(
            "Word limit exceeds !!",
        )
        return
    if not (m.reply_to_message and m.reply_to_message.text) and len(m.command) == 0:
        await m.reply_text(
            "Error: There is no text in here! and only text with buttons are supported currently !",
        )
        return
    text, msgtype, file = await get_wlcm_type(m)

    if not m.reply_to_message and msgtype == Types.TEXT and len(m.command) <= 2:
        await m.reply_text(f"<code>{m.text}</code>\n\nError: There is no data in here!")
        return

    if not text and not file:
        await m.reply_text(
            "Please provide some data!",
        )
        return

    if not msgtype:
        await m.reply_text("Please provide some data for this to reply with!")
        return

    db.set_goodbye_text(text,msgtype,file)
    await m.reply_text("Saved goodbye!")
    return


@client.on(events.NewMessage(pattern="^/resetgoodbye ?(.*)"))
async def resetgb(_, m: Message):
    db = Greetings(m.chat.id)
    if m and not m.from_user:
        return
    text = "Sad to see you leaving {first}.\nTake Care!"
    db.set_goodbye_text(text,None)
    await m.reply_text("Ok Done!")
    return



@client.on(events.NewMessage(pattern="^/resetwelcome ?(.*)"))
async def resetwlcm(_, m: Message):
    db = Greetings(m.chat.id)
    if m and not m.from_user:
        return
    text = "Hey {first}, welcome to {chatname}!"
    db.set_welcome_text(text,None)
    await m.reply_text("Done!")
    return


@pbot.on_message(filters.service & filters.group, group=59)
async def cleannnnn(_, m: Message):
    db = Greetings(m.chat.id)
    clean = db.get_current_cleanservice_settings()
    try:
        if clean:
            await m.delete()
    except Exception:
        pass


@pbot.on_chat_member_updated(filters.group, group=69)
async def member_has_joined(c: pbot, member: ChatMemberUpdated):

    if (
        member.new_chat_member
        and member.new_chat_member.status not in {CMS.BANNED, CMS.LEFT, CMS.RESTRICTED}
        and not member.old_chat_member
    ):
        pass
    else:
        return

    user = member.new_chat_member.user if member.new_chat_member else member.from_user

    db = Greetings(member.chat.id)
    banned_users = gdb.check_gban(user.id)
    try:
        if user.id == Config.BOT_ID:
            return
        if user.id in DEV_USERS:
            await c.send_animation(
                chat_id=member.chat.id,
                animation="./extras/william.gif",
                caption="ᴍʏ ᴏᴡɴᴇʀ ɪs ʜᴇʀᴇ 🌸🙈❤️",
            )
            return
        if banned_users:
            await member.chat.ban_member(user.id)
            await c.send_message(
                member.chat.id,
                f"{user.mention} was globally banned so i banned!",
            )
            return
        if user.is_bot:
            return  # ignore bots
    except ChatAdminRequired:
        return
    status = db.get_welcome_status()
    oo = db.get_welcome_text()
    UwU = db.get_welcome_media()
    mtype = db.get_welcome_msgtype()
    parse_words = [
        "first",
        "last",
        "fullname",
        "username",
        "mention",
        "id",
        "chatname",
    ]
    hmm = await escape_mentions_using_curly_brackets_wl(member, True, oo, parse_words)
    if status:
        tek, button = await parse_button(hmm)
        button = await build_keyboard(button)
        button = ikb(button) if button else None

        if "%%%" in tek:
            filter_reply = tek.split("%%%")
            teks = choice(filter_reply)
        else:
            teks = tek
        ifff = db.get_current_cleanwelcome_id()
        gg = db.get_current_cleanwelcome_settings()
        if ifff and gg:
            try:
                await c.delete_messages(member.chat.id, int(ifff))
            except RPCError:
                pass
        if not teks:
            teks = "Hey {first}, welcome to {chatname}"
        try:
            if not UwU:
                jj = await c.send_message(
                    member.chat.id,
                    text=teks,
                    reply_markup=button,
                    disable_web_page_preview=True,
                )
            elif UwU:
                jj = await (await send_cmd(c,mtype))(
                    member.chat.id,
                    UwU,
                    caption=teks,
                    reply_markup=button,
                )

            if jj:
                db.set_cleanwlcm_id(int(jj.id))
        except RPCError as e:
            LOGGER.error(e)
            LOGGER.error(format_exc(e))
            return
    else:
        return


@pbot.on_chat_member_updated(filters.group, group=99)
async def member_has_left(c: pbot, member: ChatMemberUpdated):

    if (
        not member.new_chat_member
        and member.old_chat_member.status not in {CMS.BANNED, CMS.RESTRICTED}
        and member.old_chat_member
    ):
        pass
    else:
        return
    db = Greetings(member.chat.id)
    status = db.get_goodbye_status()
    oo = db.get_goodbye_text()
    UwU = db.get_goodbye_media()
    mtype = db.get_goodbye_msgtype()
    parse_words = [
        "first",
        "last",
        "fullname",
        "id",
        "username",
        "mention",
        "chatname",
    ]

    user = member.old_chat_member.user if member.old_chat_member else member.from_user

    hmm = await escape_mentions_using_curly_brackets_wl(member, False, oo, parse_words)
    if status:
        tek, button = await parse_button(hmm)
        button = await build_keyboard(button)
        button = ikb(button) if button else None

        if "%%%" in tek:
            filter_reply = tek.split("%%%")
            teks = choice(filter_reply)
        else:
            teks = tek
        ifff = db.get_current_cleangoodbye_id()
        iii = db.get_current_cleangoodbye_settings()
        if ifff and iii:
            try:
                await c.delete_messages(member.chat.id, int(ifff))
            except RPCError:
                pass
        if user.id in DEV_USERS:
            await c.send_message(
                member.chat.id,
                "Will miss you master :(",
            )
            return
        if not teks:
            teks = "Sad to see you leaving {first}\nTake Care!"
        try:
            if not UwU:
                ooo = await c.send_message(
                    member.chat.id,
                    text=teks,
                    reply_markup=button,
                    disable_web_page_preview=True,
                )
            elif UwU:
                ooo = await (await send_cmd(c,mtype))(
                    member.chat.id,
                    UwU,
                    caption=teks,
                    reply_markup=button,
                )

            if ooo:
                db.set_cleangoodbye_id(int(ooo.id))
            return
        except RPCError as e:
            LOGGER.error(e)
            LOGGER.error(format_exc(e))
            return
    else:
        return


@client.on(events.NewMessage(pattern="^/welcome ?(.*)"))
async def welcome(c: pbot, m: Message):
    db = Greetings(m.chat.id)
    status = db.get_welcome_status()
    oo = db.get_welcome_text()
    args = m.text.split(" ", 1)

    if m and not m.from_user:
        return

    if len(args) >= 2:
        if args[1].lower() == "noformat":
            await m.reply_text(
                f"""Current welcome settings:-
            Welcome power: {status}
            Clean Welcome: {db.get_current_cleanwelcome_settings()}
            Cleaning service: {db.get_current_cleanservice_settings()}
            Welcome text in no formating:
            """,
            )
            await c.send_message(
                m.chat.id, text=oo, parse_mode=enums.ParseMode.DISABLED
            )
            return
        if args[1].lower() == "on":
            db.set_current_welcome_settings(True)
            await m.reply_text("I will greet newly joined member from now on.")
            return
        if args[1].lower() == "off":
            db.set_current_welcome_settings(False)
            await m.reply_text("I will stay quiet when someone joins.")
            return
        await m.reply_text("what are you trying to do ??")
        return
    await m.reply_text(
        f"""Current welcome settings:-
    Welcome power: {status}
    Clean Welcome: {db.get_current_cleanwelcome_settings()}
    Cleaning service: {db.get_current_cleanservice_settings()}
    Welcome text:
    """,
    )
    UwU = db.get_welcome_media()
    mtype = db.get_welcome_msgtype()
    tek, button = await parse_button(oo)
    button = await build_keyboard(button)
    button = ikb(button) if button else None
    if not UwU:
            await c.send_message(
            m.chat.id,
            text=tek,
            reply_markup=button,
            disable_web_page_preview=True,
        )
    elif UwU:
            await (await send_cmd(c,mtype))(
            m.chat.id,
            UwU,
            caption=tek,
            reply_markup=button,
        )
    return


@client.on(events.NewMessage(pattern="^/goodbye ?(.*)"))
async def goodbye(c: pbot, m: Message):
    db = Greetings(m.chat.id)
    status = db.get_goodbye_status()
    oo = db.get_goodbye_text()
    args = m.text.split(" ", 1)
    if m and not m.from_user:
        return
    if len(args) >= 2:
        if args[1].lower() == "noformat":
            await m.reply_text(
                f"""Current goodbye settings:-
            Goodbye power: {status}
            Clean Goodbye: {db.get_current_cleangoodbye_settings()}
            Cleaning service: {db.get_current_cleanservice_settings()}
            Goodbye text in no formating:
            """,
            )
            await c.send_message(
                m.chat.id, text=oo, parse_mode=enums.ParseMode.DISABLED
            )
            return
        if args[1].lower() == "on":
            db.set_current_goodbye_settings(True)
            await m.reply_text("I don't want but I will say goodbye to the fugitives")
            return
        if args[1].lower() == "off":
            db.set_current_goodbye_settings(False)
            await m.reply_text("I will stay quiet for fugitives")
            return
        await m.reply_text("what are you trying to do ??")
        return
    await m.reply_text(
        f"""Current Goodbye settings:-
    Goodbye power: {status}
    Clean Goodbye: {db.get_current_cleangoodbye_settings()}
    Cleaning service: {db.get_current_cleanservice_settings()}
    Goodbye text:
    """,
    )
    UwU = db.get_goodbye_media()
    mtype = db.get_goodbye_msgtype()
    tek, button = await parse_button(oo)
    button = await build_keyboard(button)
    button = ikb(button) if button else None
    if not UwU:
            await c.send_message(
            m.chat.id,
            text=tek,
            reply_markup=button,
            disable_web_page_preview=True,
        )
    elif UwU:
            await (await send_cmd(c,mtype))(
            m.chat.id,
            UwU,
            caption=tek,
            reply_markup=button,
        )
    return
    return
