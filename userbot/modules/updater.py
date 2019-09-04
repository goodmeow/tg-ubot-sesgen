# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
"""
This module updates the userbot based on Upstream revision
"""

from os import remove, execl, mkdir, rename
from shutil import rmtree
import sys

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError

from userbot import CMD_HELP, BOTLOG, BOTLOG_CHATID
from userbot.events import register, errors_handler


async def gen_chlog(repo, diff):
    ch_log = ''
    d_form = "%d/%m/%y"
    for c in repo.iter_commits(diff):
        ch_log += f'•[{c.committed_datetime.strftime(d_form)}]: {c.summary} <{c.author}>\n'
    return ch_log


async def is_off_br(br):
    off_br = ['sql-extended', 'sql-dirty']
    if br in off_br:
        return True
    return

# Kanged from : https://github.com/AyraHikari/Nana-TgBot/blob/master/nana/modules/updater.py
async def initial_git(repo):
	isexist = os.path.exists('userbot-old')
	if isexist:
		rmtree('userbot-old')
	mkdir('userbot-old')
    rename('userbot', 'userbot-old/userbot')
    rename('.gitignore', 'userbot-old/.gitignore')
    rename('LICENSE', 'userbot-old/LICENSE')
    rename('README.md', 'userbot-old/README.md')
    rename('requirements.txt', 'userbot-old/requirements.txt')
    rename('Procfile', 'userbot-old/Procfile')
    rename('runtime.txt', 'userbot-old/runtime.txt')
    rename('config.env', 'userbot-old/config.env')
    rename('userbot.session', 'userbot-old/userbot.session')
    update = repo.create_remote('sql-extended', off_repo)
    update.pull('sql-extended')
    rename('userbot-old/userbot.session', 'userbot.session')
    rename('userbot-old/config.env', 'config.env')

@register(outgoing=True, pattern="^.update(?: |$)(.*)")
@errors_handler
async def upstream(ups):
    "For .update command, check if the bot is up to date, update if specified"
    if not ups.text[0].isalpha() and ups.text[0] not in ("/", "#", "@", "!"):
        await ups.edit("`Checking for updates, please wait....`")
        initial = False
        conf = ups.pattern_match.group(1)
        off_repo = 'https://github.com/AvinashReddy3108/PaperplaneExtended.git'

        try:
            txt = "`Oops.. Updater cannot continue due to some problems occured`\n\n**LOGTRACE:**\n"
            repo = Repo()
        except NoSuchPathError as error:
            await ups.edit(f'{txt}\n`directory {error} is not found`')
            return
        except InvalidGitRepositoryError as error:
            repo = Repo.init()
            initial = True
        except GitCommandError as error:
            await ups.edit(f'{txt}\n`{error}`')
            return
        
        if initial:
            if len(ups.text.split()) != 2:
                await ups.edit('Your git workdir is missing!\nBut i can repair and take new latest update for you.\nJust do `update now` to repair and take update!')
                return
            elif len(ups.text.split()) == 2 and ups.text.split()[1] == "now":
                try:
                    await initial_git(repo)
                except Exception as err:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    await ups.edit('An error has accured!\nPlease see your Assistant for more information!')
                    sys.__excepthook__(exc_type, exc_obj, exc_tb)
                    errors = traceback.format_exception(etype=exc_type, value=exc_obj, tb=exc_tb)
                    text = "An error has accured!\n\n```{}```\n".format("".join(errors))
                    if errtype == ModuleNotFoundError:
                        text += "\nHint: Try this in your terminal `pip install -r requirements.txt`"
                    if BOTLOG:
                        await ups.client.send_message(BOTLOG_CHATID, text)
                    return
                await ups.edit('Successfully Updated!\nBot is restarting...')
                await ups.client.disconnect()
                execl(sys.executable, sys.executable, *sys.argv)
                exit()

        ac_br = repo.active_branch.name
        if not await is_off_br(ac_br):
            await ups.edit(
                f'**[UPDATER]:**` Looks like you are using your own custom branch ({ac_br}). \
                in that case, Updater is unable to identify which branch is to be merged. \
                please checkout to any official branch`')
            return

        try:
            repo.create_remote('upstream', off_repo)
        except BaseException:
            pass

        ups_rem = repo.remote('upstream')
        ups_rem.fetch(ac_br)
        try:
            changelog = await gen_chlog(repo, f'HEAD..upstream/{ac_br}')
        except Exception as err:
            if "fatal: bad revision" in str(err):
                try:
                    await initial_git(repo)
                except Exception as err:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    await ups.edit('An error has accured!\nPlease see your Assistant for more information!')
                    sys.__excepthook__(exc_type, exc_obj, exc_tb)
                    errors = traceback.format_exception(etype=exc_type, value=exc_obj, tb=exc_tb)
                    text = "An error has accured!\n\n```{}```\n".format("".join(errors))
                    if errtype == ModuleNotFoundError:
                        text += "\nHint: Try this in your terminal `pip install -r requirements.txt`"
                    if BOTLOG:
                        await ups.client.send_message(BOTLOG_CHATID, text)
                    return
                await ups.edit('Successfully Updated!\nBot is restarting...')
                await ups.client.disconnect()
                execl(sys.executable, sys.executable, *sys.argv)
                exit()

        if not changelog:
            await ups.edit(
                f'\n`Your BOT is` **up-to-date** `with` **{ac_br}**\n')
            return

        if conf != "now":
            changelog_str = f'**New UPDATE available for [{ac_br}]:\n\nCHANGELOG:**\n`{changelog}`'
            if len(changelog_str) > 4096:
                await ups.edit("`Changelog is too big, sending it as a file.`")
                file = open("output.txt", "w+")
                file.write(changelog_str)
                file.close()
                await ups.client.send_file(
                    ups.chat_id,
                    "output.txt",
                    reply_to=ups.id,
                )
                remove("output.txt")
            else:
                await ups.edit(changelog_str)
            await ups.respond(
                "`do \".update now\" to update\nDon't if using Heroku`")
            return

        await ups.edit('`New update found, updating...`')
        try:
            ups_rem.pull(ac_br)
        except GitCommandError:
            ups_rem.git.reset('--hard')
            repo.git.clean('-fd', 'userbot/modules/')
        await ups.edit('`Successfully Updated!\n'
                       'Bot is restarting... Wait for a second!`')
        await ups.client.disconnect()
        # Spin a new instance of bot
        execl(sys.executable, sys.executable, *sys.argv)
        # Shut the existing one down
        exit()


CMD_HELP.update({
    'update':
    ".update\
\nUsage: Checks if the main userbot repository has any updates and shows a changelog if so.\
\n\n.update now\
\nUsage: Updates your userbot, if there are any updates in the main userbot repository."
})
