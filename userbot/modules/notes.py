# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module containing commands for keeping notes. """

from userbot import BOTLOG, BOTLOG_CHATID, CMD_HELP
from userbot.events import register, errors_handler
from asyncio import sleep


@register(outgoing=True, pattern="^.notes$")
@errors_handler
async def notes_active(svd):
    """ For .notes command, list all of the notes saved in a chat. """
    try:
        from userbot.modules.sql_helper.notes_sql import get_notes
    except AttributeError:
        await svd.edit("`Running on Non-SQL mode!`")
        return
    message = "`There are no saved notes in this chat`"
    notes = get_notes(svd.chat_id)
    for note in notes:
        if message == "`There are no saved notes in this chat`":
            message = "Notes saved in this chat:\n"
            message += "`#{}`\n".format(note.keyword)
        else:
            message += "`#{}`\n".format(note.keyword)
    await svd.edit(message)


@register(outgoing=True, pattern=r"^.clear (.*)")
@errors_handler
async def remove_notes(clr):
    """ For .clear command, clear note with the given name."""
    try:
        from userbot.modules.sql_helper.notes_sql import rm_note
    except AttributeError:
        await clr.edit("`Running on Non-SQL mode!`")
        return
    notename = clr.pattern_match.group(1)
    if rm_note(clr.chat_id, notename) is False:
        return await clr.edit("`Couldn't find note:` **{}**".format(notename))
    else:
        return await clr.edit(
            "`Successfully deleted note:` **{}**".format(notename))


@register(outgoing=True, pattern=r"^.save (.*)")
@errors_handler
async def add_filter(fltr):
    """ For .save command, saves notes in a chat. """
    try:
        from userbot.modules.sql_helper.notes_sql import add_note
    except AttributeError:
        await fltr.edit("`Running on Non-SQL mode!`")
        return
    notename = fltr.pattern_match.group(1)
    msg = await fltr.get_reply_message()
    if not msg:
        await fltr.edit("`I need something to save as a note.`")
    elif BOTLOG_CHATID:
        await fltr.client.send_message(
            BOTLOG_CHATID, f"#NOTE\
        \nCHAT: {fltr.chat.title}\
        \nKEYWORD: {notename}\
        \nThe following message is saved as the note's reply data for the chat, please do NOT delete it !!"
        )
        msg_o = await fltr.client.forward_messages(
            entity=BOTLOG_CHATID,
            messages=msg,
            from_peer=new_handler.chat_id,
            silent=True)
    else:
        await fltr.edit("`This feature requires the BOTLOG_CHATID to be set.`")
        return
    success = "`Note {} successfully. Use` #{} `to get it`"
    if add_note(str(fltr.chat_id), notename, snip['text'], snip['type'],
                snip.get('id'), snip.get('hash'), snip.get('fr')) is False:
        return await fltr.edit(success.format('updated', notename))
    else:
        return await fltr.edit(success.format('added', notename))


@register(pattern=r"#\.*", disable_edited=True)
@errors_handler
async def incom_note(getnt):
    """ Notes logic. """
    try:
        if not (await getnt.get_sender()).bot:
            try:
                from userbot.modules.sql_helper.notes_sql import get_notes
            except AttributeError:
                return
            notename = getnt.text[1:]
            notes = get_notes(getnt.chat_id)
            for note in notes:
                if notename == note.keyword:
                    if note.snip_type == TYPE_PHOTO:
                        media = types.InputPhoto(int(note.media_id),
                                                 int(note.media_access_hash),
                                                 note.media_file_reference)
                    elif note.snip_type == TYPE_DOCUMENT:
                        media = types.InputDocument(
                            int(note.media_id), int(note.media_access_hash),
                            note.media_file_reference)
                    else:
                        media = None
                    message_id = getnt.message.id
                    if getnt.reply_to_msg_id:
                        message_id = getnt.reply_to_msg_id
                    await getnt.client.send_message(getnt.chat_id,
                                                    note.reply,
                                                    reply_to=message_id,
                                                    file=media)
    except AttributeError:
        pass


@register(outgoing=True, pattern="^.rmbotnotes (.*)")
@errors_handler
async def kick_marie_notes(kick):
    """ For .rmbotnotes command, allows you to kick all \
        Marie(or her clones) notes from a chat. """
    bot_type = kick.pattern_match.group(1).lower()
    if bot_type not in ["marie", "rose"]:
        await kick.edit("`That bot is not yet supported!`")
        return
    await kick.edit("```Will be kicking away all Notes!```")
    await sleep(3)
    resp = await kick.get_reply_message()
    filters = resp.text.split("-")[1:]
    for i in filters:
        if bot_type == "marie":
            await kick.reply("/clear %s" % (i.strip()))
        if bot_type == "rose":
            i = i.replace('`', '')
            await kick.reply("/clear %s" % (i.strip()))
        await sleep(0.3)
    await kick.respond(
        "```Successfully purged bots notes yaay!```\n Gimme cookies!")
    if BOTLOG:
        await kick.client.send_message(
            BOTLOG_CHATID, "I cleaned all Notes at " + str(kick.chat_id))


CMD_HELP.update({
    "notes":
    "\
#<notename>\
\nUsage: Gets the specified note.\
\n\n.save <notename>\
\nUsage: Saves the replied message as a note with the name notename. (Works with pics, docs, and stickers too!)\
\n\n.notes\
\nUsage: Gets all saved notes in a chat.\
\n\n.clear <notename>\
\nUsage: Deletes the specified note.\
\n\n.rmbotnotes <bot_name>\
\nUsage: Removes all notes of admin bots (Currently supported: Marie, Rose and their clones.) in the chat."
})
