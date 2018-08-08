import discord
import sys
import logging
import json
import requests
import os
from time import localtime, strftime
from discord.ext import commands
from lxml import html
from datetime import datetime,timedelta

with open("database.txt","r") as databaseFile:
    if os.stat("database.txt").st_size == 0:
        botDatabase = {}
    else:
        botDatabase = json.load(databaseFile)
databaseFile.close()
TOKEN = [botDatabase['testToken'],botDatabase['realToken']]
client = discord.Client()
bot = commands.Bot(command_prefix='-', description="Fortnite Bot made by th3infinity#6720")
url = "https://api.fortnitetracker.com/v1/profile/{}/{}"
headers = {"TRN-Api-Key": botDatabase['trnKey']}
platforms = ['pc', 'psn', 'xbl']
roles = ['80%+', '70%', '60%', '50%', '40%', '30%', '25%', '20%', '15%', '10%']
maint = False
developerID = 198844841977708545

###Tournaments Stuff
class Tournament:
    next_id = 0

    def __init__(self,t_name,t_time,t_costs,t_link,t_slots,t_id):
        self.id = Tournament.next_id
        Tournament.next_id += 1
        self.name = t_name
        self.time = t_time
        self.costs = t_costs
        self.link = t_link
        self.slots = t_slots
        self.tid = t_id


umg_tournaments = []
egl_tournaments = []

version = '0.4'
lastupdated = '2018-08-08'
changelog = '- added autom Tournament crawling\n - multi Server support'


def is_allowedchannel(ctx):
    allowed = True
    channels = botDatabase[str(ctx.message.guild.id)]['allowedChannels']
    if len(channels) > 0:
        allowed = ctx.message.channel.id in channels
    return allowed


def is_developer(ctx):
    return ctx.author.id == developerID


def is_allowed(ctx):
    if str(ctx.message.guild.id) in botDatabase:
        modroleslist = botDatabase[str(ctx.message.guild.id)]['modRoles']
    else:
        modroleslist = []
    return is_developer(ctx) or commands.has_any_role(modroleslist)


async def is_setup(ctx):
    issetup = str(ctx.message.guild.id) in botDatabase
    if not issetup:
        await ctx.send("Please Setup the Bot for this Server: `-setup <botspam Channel ID> <log Channel ID> <turnier Channel ID>`")
    return issetup


def saveDatabase():
    with open("database.txt", "w") as databaseFile:
        json.dump(botDatabase, databaseFile, sort_keys=True)
    databaseFile.close()


@bot.command(pass_context=True, name='commandList', aliases=['commandlist', 'cl'], help='Postet eine Liste aller '
                                                                                        'verfügbaren Commands')
async def commandList(ctx):
    for rl in ctx.message.author.roles:
        print(rl.mention)
    logger.info('Command -commandList from User: ' + str(ctx.message.author.id))

    embed_bot = discord.Embed(title='Bot - Commands', description='', color=0x0000FF)
    embed_bot.add_field(name='`-info`', value='Postet Stats Bot Info')
    embed_bot.add_field(name='`-rank <pc|psn|xbl> <epicGameName>`',
                        value='Gibt dir den entsprechenden Rang je nach Winrate, für Leerzeichen den Namen mit "" '
                              'schreiben!')
    embed_bot.add_field(name='`-commandList`', value='Postet Liste aller verfügbaren Commands')

    ###ModOnly
    guildID = str(ctx.message.guild.id)
    if is_developer(ctx) or (guildID in botDatabase and ctx.message.author.id in botDatabase[guildID]['modRoles']) :
        embed_bot.add_field(name='`-blacklist`', value='Postet die aktuelle Acc Blacklist für Ranks')
        embed_bot.add_field(name='`-addBlacklist <name>`', value='Fügt Namen zur Blacklist hinzu')
        embed_bot.add_field(name='`-removeBlacklist <name>`', value='Entfernt Namen von Blacklist')
        embed_bot.add_field(name='`-matchMin <number>`', value='Ändert das Match Minimum')
        embed_bot.add_field(name='`-database`', value='Schickt die aktuelle Nutzungsdatenbank per PN')
        embed_bot.add_field(name='`-autoRank <roleName>`', value='Gibt allen Mitgliedern der Role den WinRate Rang')
    embed_bot.set_footer(text='made with <3 by th3infinity#6720')
    await ctx.send(embed=embed_bot)


@bot.command(hidden=True, pass_context=True, name='maintenance', aliases=['maint', 'mt'])
@commands.check(is_developer)
async def maintenance(ctx):
    global maint
    maint = not maint
    if maint:
        answer = 'Bot Maintenance wurde aktiviert!'
    else:
        answer = 'Bot Maintenance wurde deaktiviert!'
    embed_maint = discord.Embed(title='Maintenance', description=answer, color=0xE88100)
    embed_maint.set_footer(text='made with <3 by th3infinity#6720')
    await ctx.send(embed=embed_maint)


@bot.command(hidden=True, pass_context=True, name='database', aliases=['db'])
@commands.check(is_setup)
@commands.check(is_allowed)
async def database(ctx):
    logger.info('Command -database from User: ' + str(ctx.message.author.id))
    guildID = str(ctx.message.guild.id)
    with open("database" + guildID + ".txt", "w") as guildDBFile:
        json.dump(botDatabase[guildID]['nameDatabase'], guildDBFile, sort_keys=True)
    guildDBFile.close()
    # res = json.dumps(response, indent=4)
    # for part in [res[o:o+2000] for o in range(0, len(res), 2000)]:
    #    await ctx.message.author.send(part)
    await ctx.message.author.send('Nutzerlist Json', file=discord.File(open("database" + guildID + ".txt", "rb")))
    # await ctx.message.author.send(json.dumps(namedatabase,indent=4))


@bot.command(hidden=True, pass_context=True, name='blacklist', aliases=['Blacklist', 'bl'])
@commands.check(is_setup)
@commands.check(is_allowed)
async def blacklist(ctx):
    logger.info('Command -blacklist from User: ' + str(ctx.message.author.id))
    guildID = str(ctx.message.guild.id)
    blstr = ''
    for blname in botDatabase[guildID]['blacklist']:
        blstr += blname + '\n'
    embed_success = discord.Embed(title='Blacklist',
                                  description=blstr, color=0x008CFF)
    embed_success.set_footer(text='made with <3 by th3infinity#6720')
    await ctx.send(embed=embed_success)


@bot.command(hidden=True, pass_context=True, name='matchMin', aliases=['matchmin', 'mm'])
@commands.check(is_setup)
@commands.check(is_allowed)
async def matchMin(ctx, number=-1):
    guildID = str(ctx.message.guild.id)
    logger.info('Command -matchMin from User: ' + str(ctx.message.author.id))
    if number > -1:
        botDatabase[guildID]['minGames'] = int(number)
        saveDatabase()

        logger.info('Changed Match Min to: ' + str(number))
        embed_info = discord.Embed(title='Match Minimum',
                                   description='Match Minimum zu **' + str(botDatabase[guildID]['minGames']) + '** geändert',
                                   color=0x00FF00)
        embed_info.set_footer(text='made with <3 by th3infinity#6720')
        await ctx.send(embed=embed_info)
    else:
        embed_info = discord.Embed(title='Match Minimum',
                                   description='Aktuelles Match Minimum: **' + str(botDatabase[guildID]['minGames']) + '**', color=0x008CFF)
        embed_info.set_footer(text='made with <3 by th3infinity#6720')
        await ctx.send(embed=embed_info)


@bot.command(hidden=True, pass_context=True, name='setup', aliases=['SETUP', 'Setup'])
@commands.check(is_allowed)
async def setup(ctx, botspamID: commands.TextChannelConverter, logChannelID: commands.TextChannelConverter, tournamentChannelID: commands.TextChannelConverter ):

    guildID = str(ctx.message.guild.id)
    if guildID in botDatabase:
        botDatabase[guildID]['botspamID'] = botspamID.id
        botDatabase[guildID]['logChannelID'] = logChannelID.id
        botDatabase[guildID]['tournamentChannelID'] = tournamentChannelID.id
    else:
        botDatabase[guildID] = {'botspamID': botspamID.id, 'logChannelID': logChannelID.id, 'tournamentChannelID': tournamentChannelID.id, 'allowedChannels': [], 'modRoles': [], 'umg_posted': [], 'egl_posted': [], 'blacklist': [], 'minGames': 200, 'nameDatabase': {}}
    saveDatabase()
    embed = discord.Embed(title='Bot Setup',description='Bot erfolgreich eingerichtet!', color=0x00FF00)
    embed.set_footer(text='made with <3 by th3infinity#6720')
    await ctx.send(embed=embed)


@setup.error
async def setup_on_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title='Setup', description='Fehlende Argumente! `-setup <botspam Channel ID> <log '
                                                         'Channel ID> <turnier Channel ID>`', color=0xFF0000)
        embed.set_footer(text='made with <3 by th3infinity#6720')
        await ctx.send(embed=embed)


@bot.command(hidden=True, pass_context=True, name='allowedChannels', aliases=['allowedchannels', 'allowedc', 'allowedch'])
@commands.check(is_setup)
@commands.check(is_allowed)
async def allowedChannels(ctx,channel: commands.TextChannelConverter = ''):
    guildID = str(ctx.message.guild.id)
    embed = discord.Embed(title='Erlaubte Channel')
    embed.colour = 0x008CFF
    embed.set_footer(text='made with <3 by th3infinity#6720')
    if channel == '':
        channelStr = ''
        for ch in botDatabase[guildID]['allowedChannels']:
            channelStr += '<#' + str(ch) + '>\n'
        embed.description = channelStr
    elif type(channel) is discord.channel.TextChannel:
        channels = botDatabase[guildID]['allowedChannels']
        embed.description = 'Channel <#' + str(channel.id) + '> wurde '
        embed.colour = 0x00FF00

        if channel.id in channels:
            embed.colour = 0xFF6600
            channels.remove(channel.id)
            embed.description += '**entfernt**!'
        else:
            channels.append(channel.id)
            embed.description += '**hinzugefügt**!'

        botDatabase[guildID]['allowedChannels'] = channels
        saveDatabase()
    else:
        embed.description = 'Ungültiges Channel Format! Gültig: ID, Erwähnung(#Channel), Name'
        embed.colour = 0xFF0000
    await ctx.send(embed=embed)


@bot.command(hidden=True, pass_context=True, name='modRoles', aliases=['modroles', 'modr', 'mr'])
@commands.check(is_setup)
@commands.check(is_allowed)
async def modRoles(ctx,role: commands.RoleConverter = ''):
    guildID = str(ctx.message.guild.id)
    embed = discord.Embed(title='Moderatoren')
    embed.colour = 0x008CFF
    embed.set_footer(text='made with <3 by th3infinity#6720')
    if role == '':
        roleStr = ''
        for r in botDatabase[guildID]['modRoles']:
            roleStr += '<@&' + str(r) + '>\n'
        embed.description = roleStr
    elif type(role) is discord.Role:
        modlist = botDatabase[guildID]['modRoles']
        embed.description = 'Role <@&' + str(role.id) + '> wurde '
        embed.colour = 0x00FF00
        if role.id in modlist:
            embed.colour = 0xFF6600
            modlist.remove(role.id)
            embed.description += '**entfernt**!'
        else:
            modlist.append(role.id)
            embed.description += '**hinzugefügt**!'
        botDatabase[guildID]['modRoles'] = modlist
        saveDatabase()
    else:
        embed.description = 'Ungültiges Rollen Format! Gültig: ID, Erwähnung(@Role), Name'
        embed.colour = 0xFF0000
    await ctx.send(embed=embed)


@bot.command(hidden=True, pass_context=True, name='addBlacklist', aliases=['addblacklist', 'addbl', 'bl+'])
@commands.check(is_setup)
@commands.check(is_allowed)
async def addBlacklist(ctx, *name):
    blname = ' '.join(name)
    guildID = str(ctx.message.guild.id)
    logger.info('Command -addBlacklist from User: ' + str(ctx.message.author.id))

    if blname.lower() in (n.lower() for n in botDatabase[guildID]['blacklist']):
        embed_already = discord.Embed(title='Blacklist',
                                      description='Name **' + blname + '** schon auf der Blacklist!', color=0xFF0000)
        embed_already.set_footer(text='made with <3 by th3infinity#6720')
        logger.error('name: ' + blname + ' already on blacklist')
        await ctx.send(embed=embed_already)
    else:
        botDatabase[guildID]['blacklist'].append(blname)
        saveDatabase()
        embed_success = discord.Embed(title='Blacklist',
                                      description='Name **' + blname + '** zur Blacklist hinzugefügt!', color=0x00FF00)
        embed_success.set_footer(text='made with <3 by th3infinity#6720')
        logger.error('name: ' + blname + ' added to blacklist')
        await ctx.send(embed=embed_success)


@addBlacklist.error
async def addBlacklist_on_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title='Blacklist', description='Fehlendes Argument! `-addBlacklist <name>', color=0xFF0000)
        embed.set_footer(text='made with <3 by th3infinity#6720')
        await ctx.send(embed=embed)


@bot.command(hidden=True, pass_context=True, name='removeBlacklist', aliases=['removeblacklist', 'removebl', 'bl-'])
@commands.check(is_setup)
@commands.check(is_allowed)
async def removeBlacklist(ctx, *name):
    blname = ' '.join(name)
    guildID = str(ctx.message.guild.id)
    logger.info('Command -removeBlacklist from User: ' + str(ctx.message.author.id))

    if blname.lower() in (n.lower() for n in botDatabase[guildID]['blacklist']):
        botDatabase[guildID]['blacklist'].remove(blname)
        saveDatabase()
        embed_success = discord.Embed(title='Blacklist',
                                      description='Name **' + blname + '** von Blacklist gelöscht!', color=0x00FF00)
        embed_success.set_footer(text='made with <3 by th3infinity#6720')
        logger.error('name: ' + blname + ' deleted from blacklist')
        await ctx.send(embed=embed_success)
    else:
        embed_error = discord.Embed(title='Blacklist',
                                    description='Name **' + blname + '** nicht in der Blacklist!', color=0xFF0000)
        embed_error.set_footer(text='made with <3 by th3infinity#6720')
        logger.error('name: ' + blname + ' not in blacklist')
        await ctx.send(embed=embed_error)


@removeBlacklist.error
async def removeBlacklist_on_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title='Blacklist', description='Fehlendes Argument! `-removeBlacklist <name>', color=0xFF0000)
        embed.set_footer(text='made with <3 by th3infinity#6720')
        await ctx.send(embed=embed)


@bot.command(pass_context=True, name='rank', aliases=['r', 'rang', 'Rank', 'RANK', 'RANG', 'Rang'], help='Gibt dir basierend auf deiner Winrate den entsprechenden Rang. `-rank <platform> <epicGamesName>`', brief='Rangvergabe basierend auf Winrate')
@commands.check(is_setup)
@commands.check(is_allowedchannel)
async def rank(ctx, platform, *all):
    if not maint or is_developer(ctx):
        guildID = str(ctx.message.guild.id)
        name = ' '.join(all)
        logger.info('Command -rank from User: ' + str(ctx.message.author.id))
        if platform.lower() not in platforms:
            embed_platform = discord.Embed(title='Win Rate Rank',
                                           description='Ungültige Plattform! <' + ', '.join(platforms) + '>', color=0xFF0000)
            embed_platform.set_footer(text='made with <3 by th3infinity#6720')

            logger.error('No valid Mode: ' + platform)
            await ctx.send(embed=embed_platform)
        elif name.lower() in (n.lower() for n in botDatabase[guildID]['blacklist']):
            embed_blacklist = discord.Embed(title='Win Rate Rank', description='<@' + str(
                ctx.message.author.id) + '> AccName **' + name.lower() + '** ist blockiert! Falls du der Eigentümer des Accounts bist wende dich an jemanden vom Team!',
                                            color=0xFF0000)
            embed_blacklist.set_footer(text='made with <3 by th3infinity#6720')
            logger.error('Name on blacklist: ' + name.lower())
            await ctx.send(embed=embed_blacklist)
        else:
            results = await getStats(ctx,name,platform)
            if results['accname']:
                accname = results['accname']
                overall_winRatio = results['overall_winRatio']
                overall_winRatio_old = results['overall_winRatio_old']
                overall_matches = results['overall_matches']
                overall_matches_old = results['overall_matches_old']

                namedatabase = botDatabase[guildID]['nameDatabase']
                checkChannelID = botDatabase[guildID]['logChannelID']

                if accname in namedatabase:
                    if ctx.message.author.id not in namedatabase[accname]['ids']:
                        namedatabase[accname]['usages'] += 1
                        namedatabase[accname]['winRatio'] = round(overall_winRatio, 2)
                        namedatabase[accname]['winRatio_old'] = round(overall_winRatio_old, 2)
                        namedatabase[accname]['ids'].append(ctx.message.author.id)
                        idused = '['
                        for ids in namedatabase[accname]['ids']:
                            idused += '<@' + str(ids) + '> '
                        idused += ']'
                        await (bot.get_channel(checkChannelID)).send('Accname: **' + accname + '** was used **' + str(
                            namedatabase[accname]['usages']) + '** Times! Users: ' + idused)
                else:
                    namedatabase[accname] = {'usages': 1, 'winRatio': round(overall_winRatio, 2),
                                             'winRatio_old': round(overall_winRatio_old, 2),
                                             'ids': [ctx.message.author.id]}

                    botDatabase[guildID]['nameDatabase'] = namedatabase
                    saveDatabase()

                match_min = botDatabase[guildID]['minGames']
                if (overall_matches >= match_min):
                    overten = True
                    if (round(overall_winRatio) >= 80):
                        role = discord.utils.get(ctx.message.guild.roles, name='80%+')
                    elif (round(overall_winRatio) >= 70):
                        role = discord.utils.get(ctx.message.guild.roles, name='70%')
                    elif (round(overall_winRatio) >= 60):
                        role = discord.utils.get(ctx.message.guild.roles, name='60%')
                    elif (round(overall_winRatio) >= 50):
                        role = discord.utils.get(ctx.message.guild.roles, name='50%')
                    elif (round(overall_winRatio) >= 40):
                        role = discord.utils.get(ctx.message.guild.roles, name='40%')
                    elif (round(overall_winRatio) >= 30):
                        role = discord.utils.get(ctx.message.guild.roles, name='30%')
                    elif (round(overall_winRatio) >= 25):
                        role = discord.utils.get(ctx.message.guild.roles, name='25%')
                    elif (round(overall_winRatio) >= 20):
                        role = discord.utils.get(ctx.message.guild.roles, name='20%')
                    elif (round(overall_winRatio) >= 15):
                        role = discord.utils.get(ctx.message.guild.roles, name='15%')
                    elif (round(overall_winRatio) >= 10):
                        role = discord.utils.get(ctx.message.guild.roles, name='10%')
                    else:
                        overten = False

                    if round(overall_winRatio) >= 30:
                        await (bot.get_channel(checkChannelID)).send(
                            'User: <@' + str(ctx.message.author.id) + '> got **' + str(round(overall_winRatio,
                                                                                             2)) + '%** with Accountname: **' + accname + '** [Current Season]')

                    if (round(overall_winRatio)) >= 50:
                        await ctx.message.guild.get_member(developerID).send('User: ' + ctx.message.author.display_name
                                                                             + '(' + ctx.message.author.name + ') ' + 'ID[' + str(
                            ctx.message.author.id) + '] got **'
                                                                             + str(
                            round(overall_winRatio, 2)) + '%** with Accountname: **' + accname + '** [Current '
                                                                                                'Season]')

                    if overten:
                        for r in ctx.message.author.roles:
                            if r.name in roles:
                                await ctx.message.author.remove_roles(r)
                            if r.name == 'Alte Season':
                                await ctx.message.author.remove_roles(r)
                        await ctx.message.author.add_roles(role)
                        embed_role = discord.Embed(title='Win Rate Rank - Aktuelle Season',
                                                   description='<@' + str(
                                                       ctx.message.author.id) + '> dir wurde der Rang **' + role.name + '** gegeben! Deine aktuelle Winrate beträgt: **' + str(
                                                       round(overall_winRatio, 2)) + '%**', color=0x00FF00)
                        embed_role.set_footer(text='EpicGameName: ' + accname + ' | made with <3 by th3infinity#6720')
                        logger.info('Rank ' + role.name + ' was given with winrate: ' + str(overall_winRatio))
                        await ctx.send(embed=embed_role)
                    else:
                        embed_norole = discord.Embed(title='Win Rate Rank  - Aktuelle Season',
                                                     description='<@' + str(
                                                         ctx.message.author.id) + '> dir fehlen **' + str(
                                                         round(10 - overall_winRatio, 2)) + '%** zum 10% Rang!',
                                                     color=0xFF0000)
                        embed_norole.set_footer(text='EpicGameName: ' + accname + ' | made with <3 by th3infinity#6720')
                        logger.info('User missing ' + str(10 - overall_winRatio) + '%')
                        await ctx.send(embed=embed_norole)
                elif overall_matches_old >= match_min:
                    overten = True
                    if (round(overall_winRatio_old) >= 80):
                        role = discord.utils.get(ctx.message.guild.roles, name='80%+')
                    elif (round(overall_winRatio_old) >= 70):
                        role = discord.utils.get(ctx.message.guild.roles, name='70%')
                    elif (round(overall_winRatio_old) >= 60):
                        role = discord.utils.get(ctx.message.guild.roles, name='60%')
                    elif (round(overall_winRatio_old) >= 50):
                        role = discord.utils.get(ctx.message.guild.roles, name='50%')
                    elif (round(overall_winRatio_old) >= 40):
                        role = discord.utils.get(ctx.message.guild.roles, name='40%')
                    elif (round(overall_winRatio_old) >= 30):
                        role = discord.utils.get(ctx.message.guild.roles, name='30%')
                    elif (round(overall_winRatio_old) >= 25):
                        role = discord.utils.get(ctx.message.guild.roles, name='25%')
                    elif (round(overall_winRatio_old) >= 20):
                        role = discord.utils.get(ctx.message.guild.roles, name='20%')
                    elif (round(overall_winRatio_old) >= 15):
                        role = discord.utils.get(ctx.message.guild.roles, name='15%')
                    elif (round(overall_winRatio_old) >= 10):
                        role = discord.utils.get(ctx.message.guild.roles, name='10%')
                    else:
                        overten = False

                    if round(overall_winRatio_old) >= 30:
                        await (bot.get_channel(checkChannelID)).send(
                            'User: <@' + str(ctx.message.author.id) + '> got **' + str(round(overall_winRatio_old,
                                                                                             2)) + '%** with Accountname: **' + accname + '** [Last Season]')

                    if (round(overall_winRatio_old)) >= 50:
                        await ctx.message.guild.get_member(developerID).send('User: ' + ctx.message.author.display_name
                                                                             + '(' + ctx.message.author.name + ') ' + 'ID[' + str(
                            ctx.message.author.id) + '] got **'
                                                                             + str(
                            round(overall_winRatio_old, 2)) + '%** with Accountname: **' + accname + '** [Last '
                                                                                                'Season]')

                    if overten:
                        for r in ctx.message.author.roles:
                            if r.name in roles:
                                await ctx.message.author.remove_roles(r)
                        await ctx.message.author.add_roles(role)
                        await ctx.message.author.add_roles(
                            discord.utils.get(ctx.message.guild.roles, name='Alte Season'))
                        embed_role = discord.Embed(title='Win Rate Rank  - Alte Season',
                                                   description='<@' + str(
                                                       ctx.message.author.id) + '> dir wurde basierend auf der letzten Season der Rang **' + role.name + '** gegeben! Winrate letzte Season: **' + str(
                                                       round(overall_winRatio_old,
                                                             2)) + '%** Für Season 5 Rang fehlen dir: **' + str(
                                                       match_min - overall_matches) + ' Matches**', color=0x00FF00)
                        embed_role.set_footer(text='EpicGameName: ' + accname + ' | made with <3 by th3infinity#6720')
                        logger.info('Rank ' + role.name + ' was given with winrate: ' + str(overall_winRatio_old))
                        await ctx.send(embed=embed_role)
                    else:
                        embed_norole = discord.Embed(title='Win Rate Rank  - Alte Season',
                                                     description='<@' + str(
                                                         ctx.message.author.id) + '> dir fehlen **' + str(
                                                         round(10 - overall_winRatio_old,
                                                               2)) + '%** zum 10% Rang, basierend auf der letzten Season! Für Season 5 Rang fehlen dir: **' + str(
                                                       match_min - overall_matches) + ' Matches**',
                                                     color=0xFF0000)
                        embed_norole.set_footer(text='EpicGameName: ' + accname + ' | made with <3 by th3infinity#6720')
                        logger.info('User missing ' + str(10 - overall_winRatio_old) + '%')
                        await ctx.send(embed=embed_norole)
                else:
                    embed_matches = discord.Embed(title='Win Rate Rank',
                                                  description='<@' + str(
                                                      ctx.message.author.id) + '> Zu wenig Spiele in der aktuellen Season! Dir fehlen noch **' + str(
                                                      match_min - overall_matches) + ' Matches**',
                                                  color=0xFF0000)
                    embed_matches.add_field(name='Alte Stats',
                                            value='Melde dich für die **Rangvergabe** basierend auf der **alten Season** beim **Community Support** oder geh in den **Rang anfordern Channel**! Automatische Rangvergabe nicht möglich, da die FNTracker API keine Stats der alten Season mehr sendet. **FeelsBadMan.**')
                    embed_matches.set_footer(text='EpicGameName: ' + accname + ' | made with <3 by th3infinity#6720')
                    #embed_matches = discord.Embed(title='Win Rate Rank',
                    #                              description='<@' + str(
                    #                                  ctx.message.author.id) + '> Zu wenig Spiele in der aktuellen/letzten Season! Dir fehlen noch **' + str(
                    #                                  match_min - overall_matches) + ' Matches** in der aktuellen Season und **' + str(
                    #                                  match_min - overall_matches_old) + ' Matches** in der letzten Season!',
                    #                              color=0xFF0000)
                    logger.error('Not enough Matches ' + str(overall_matches))
                    await ctx.send(embed=embed_matches)
    else:
        embed_maint = discord.Embed(title='Maintenance',
                                    description='Bot befindet sich im Maintenance Modus! Rangvergabe deaktiviert. Bitte warten.',
                                    color=0xE88100)
        embed_maint.set_footer(text='made with <3 by th3infinity#6720')
        await ctx.send(embed=embed_maint)


@bot.command(hidden=True, pass_context=True, name='autoRank', aliases=['autorank', 'autorang', 'ar', 'autoRang'])
@commands.check(is_setup)
@commands.check(is_allowed)
async def autoRank(ctx, roleName):
    if not maint or is_developer(ctx):
        guildID = str(ctx.message.guild.id)
        logger.info('Command -autoRank from User: ' + str(ctx.message.author.id))
        role = discord.utils.get(ctx.message.guild.roles, name=roleName)
        if role is None:
            embed_notfound = discord.Embed(title='Auto Rank', description='Rank: **' + roleName + '** nicht gefunden!', color=0xFF0000)
            embed_notfound.set_footer(text='made with <3 by th3infinity#6720')
            logger.error('Role ' + roleName + ' not found')
            await ctx.send(embed=embed_notfound)
        else:
            count_found = 0
            count_notfound = 0
            for member in role.members:
                results = await getStats(ctx,member.display_name.split("|")[0],'pc',False)
                if results['accname']:
                    count_found += 1
                    accname = results['accname']
                    overall_winRatio = results['overall_winRatio']
                    overall_winRatio_old = results['overall_winRatio_old']
                    overall_matches = results['overall_matches']
                    overall_matches_old = results['overall_matches_old']

                    namedatabase = botDatabase[guildID]['nameDatabase']
                    checkChannelID = botDatabase[guildID]['logChannelID']
                    match_min = botDatabase[guildID]['minGames']

                    if (overall_matches >= match_min):
                        overten = True
                        if (round(overall_winRatio) >= 80):
                            role = discord.utils.get(ctx.message.guild.roles, name='80%+')
                        elif (round(overall_winRatio) >= 70):
                            role = discord.utils.get(ctx.message.guild.roles, name='70%')
                        elif (round(overall_winRatio) >= 60):
                            role = discord.utils.get(ctx.message.guild.roles, name='60%')
                        elif (round(overall_winRatio) >= 50):
                            role = discord.utils.get(ctx.message.guild.roles, name='50%')
                        elif (round(overall_winRatio) >= 40):
                            role = discord.utils.get(ctx.message.guild.roles, name='40%')
                        elif (round(overall_winRatio) >= 30):
                            role = discord.utils.get(ctx.message.guild.roles, name='30%')
                        elif (round(overall_winRatio) >= 25):
                            role = discord.utils.get(ctx.message.guild.roles, name='25%')
                        elif (round(overall_winRatio) >= 20):
                            role = discord.utils.get(ctx.message.guild.roles, name='20%')
                        elif (round(overall_winRatio) >= 15):
                            role = discord.utils.get(ctx.message.guild.roles, name='15%')
                        elif (round(overall_winRatio) >= 10):
                            role = discord.utils.get(ctx.message.guild.roles, name='10%')
                        else:
                            overten = False

                        if round(overall_winRatio) >= 30:
                            await (bot.get_channel(checkChannelID)).send(
                                'User: <@' + str(member.id) + '> got **' + str(round(overall_winRatio,
                                                                                                 2)) + '%** with Accountname: **' + accname + '** [Current Season]')

                        if (round(overall_winRatio)) >= 50:
                            await ctx.message.guild.get_member(developerID).send(
                                'User: ' + member.display_name
                                + '(' + member.name + ') ' + 'ID[' + str(
                                    member.id) + '] got **'
                                + str(
                                    round(overall_winRatio, 2)) + '%** with Accountname: **' + accname + '** [Current '
                                                                                                        'Season]')

                        if overten:
                            for r in member.roles:
                                if r.name in roles:
                                    await member.remove_roles(r)
                                if r.name == 'Alte Season':
                                    await member.remove_roles(r)
                            await member.add_roles(role)
                            embed_role = discord.Embed(title='Win Rate Rank - Aktuelle Season',
                                                       description='<@' + str(
                                                           member.id) + '> wurde der Rang **' + role.name + '** gegeben! Seine aktuelle Winrate beträgt: **' + str(
                                                           round(overall_winRatio, 2)) + '%**', color=0x00FF00)
                            embed_role.set_footer(text='EpicGameName: ' + accname + ' | made with <3 by th3infinity#6720')
                            logger.info('Rank ' + role.name + ' was given with winrate: ' + str(overall_winRatio) + ' to User: ' + str(member.id))
                            await ctx.send(embed=embed_role)
                        else:
                            embed_norole = discord.Embed(title='Win Rate Rank  - Aktuelle Season',
                                                         description='<@' + str(
                                                             member.id) + '> fehlen **' + str(
                                                             round(10 - overall_winRatio, 2)) + '%** zum 10% Rang!',
                                                         color=0xFF0000)
                            embed_norole.set_footer(text='EpicGameName: ' + accname + ' | made with <3 by th3infinity#6720')
                            logger.info('User: ' + str(member.id) + ' missing ' + str(10 - overall_winRatio) + '%')
                            await ctx.send(embed=embed_norole)
                    elif (overall_matches_old >= match_min):
                        overten = True
                        if (round(overall_winRatio_old) >= 80):
                            role = discord.utils.get(ctx.message.guild.roles, name='80%+')
                        elif (round(overall_winRatio_old) >= 70):
                            role = discord.utils.get(ctx.message.guild.roles, name='70%')
                        elif (round(overall_winRatio_old) >= 60):
                            role = discord.utils.get(ctx.message.guild.roles, name='60%')
                        elif (round(overall_winRatio_old) >= 50):
                            role = discord.utils.get(ctx.message.guild.roles, name='50%')
                        elif (round(overall_winRatio_old) >= 40):
                            role = discord.utils.get(ctx.message.guild.roles, name='40%')
                        elif (round(overall_winRatio_old) >= 30):
                            role = discord.utils.get(ctx.message.guild.roles, name='30%')
                        elif (round(overall_winRatio_old) >= 25):
                            role = discord.utils.get(ctx.message.guild.roles, name='25%')
                        elif (round(overall_winRatio_old) >= 20):
                            role = discord.utils.get(ctx.message.guild.roles, name='20%')
                        elif (round(overall_winRatio_old) >= 15):
                            role = discord.utils.get(ctx.message.guild.roles, name='15%')
                        elif (round(overall_winRatio_old) >= 10):
                            role = discord.utils.get(ctx.message.guild.roles, name='10%')
                        else:
                            overten = False

                        if round(overall_winRatio_old) >= 30:
                            await (bot.get_channel(checkChannelID)).send(
                                'User: <@' + str(member.id) + '> got **' + str(round(overall_winRatio_old,
                                                                                                 2)) + '%** with Accountname: **' + accname + '** [Last Season]')

                        if (round(overall_winRatio_old)) >= 50:
                            await ctx.message.guild.get_member(developerID).send(
                                'User: ' + member.display_name
                                + '(' + member.name + ') ' + 'ID[' + str(
                                    member.id) + '] got **'
                                + str(
                                    round(overall_winRatio_old, 2)) + '%** with Accountname: **' + accname + '** [Last '
                                                                                                            'Season]')

                        if overten:
                            for r in member.roles:
                                if r.name in roles:
                                    await member.remove_roles(r)
                            await member.add_roles(role)
                            await member.add_roles(
                                discord.utils.get(ctx.message.guild.roles, name='Alte Season'))
                            embed_role = discord.Embed(title='Win Rate Rank  - Alte Season',
                                                       description='<@' + str(
                                                           member.id) + '> wurde basierend auf der letzten Season der Rang **' + role.name + '** gegeben! Winrate letzte Season: **' + str(
                                                           round(overall_winRatio_old,
                                                                 2)) + '%** Für Season 5 Rang fehlen: **' + str(
                                                           match_min - overall_matches) + ' Matches**', color=0x00FF00)
                            embed_role.set_footer(text='EpicGameName: ' + accname + ' | made with <3 by th3infinity#6720')
                            logger.info('Rank ' + role.name + ' was given with winrate: ' + str(overall_winRatio_old) + '% to User: ' + str(member.id))
                            await ctx.send(embed=embed_role)
                        else:
                            embed_norole = discord.Embed(title='Win Rate Rank  - Alte Season',
                                                         description='<@' + str(
                                                             member.id) + '> fehlen **' + str(
                                                             round(10 - overall_winRatio_old,
                                                                   2)) + '%** zum 10% Rang, basierend auf der letzten Season! Für Season 5 Rang fehlen: **' + str(
                                                             match_min - overall_matches) + ' Matches**',
                                                         color=0xFF0000)
                            embed_norole.set_footer(text='EpicGameName: ' + accname + ' | made with <3 by th3infinity#6720')
                            logger.info('User:' + str(member.id) + ' missing ' + str(10 - overall_winRatio_old) + '%')
                            await ctx.send(embed=embed_norole)
                    else:
                        embed_matches = discord.Embed(title='Win Rate Rank',
                                                      description='<@' + str(
                                                          member.id) + '> Zu wenig Spiele in der aktuellen Season! Es fehlen noch **' + str(
                                                          match_min - overall_matches) + ' Matches**',
                                                      color=0xFF0000)
                        embed_matches.add_field(name='Alte Stats',
                                                value='Melde dich für die **Rangvergabe** basierend auf der **alten Season** beim **Community Support** oder geh in den **Rang anfordern Channel**! Automatische Rangvergabe nicht möglich, da die FNTracker API keine Stats der alten Season mehr sendet. **FeelsBadMan.**')
                        embed_matches.set_footer(text='EpicGameName: ' + accname + ' | made with <3 by th3infinity#6720')
                        #embed_matches = discord.Embed(title='Win Rate Rank',
                        #                              description='<@' + str(
                        #                                  member.id) + '> Zu wenig Spiele in der aktuellen/letzten Season! Es fehlen noch **' + str(
                        #                                  match_min - overall_matches) + ' Matches** in der aktuellen Season und **' + str(
                        #                                  match_min - overall_matches_old) + ' Matches** in der letzten Season!',
                        #                              color=0xFF0000)
                        logger.error('Not enough Matches ' + str(overall_matches))
                        await ctx.send(embed=embed_matches)
                else:
                    count_notfound += 1
                    await ctx.send('Member: **' + member.display_name + '** not found!')

            logger.info('Total Tested: ' + str(count_found + count_notfound) + ' | Found: ' + str(count_found) + ' | Not Found: ' + str(count_notfound))
            embed_result = discord.Embed(title='Auto Rank - Result',description='Total Tested: ' + str(count_found + count_notfound) + ' | Found: ' + str(count_found) + ' | Not Found: ' + str(count_notfound),color=0x008CFF)
            embed_result.set_footer(text='made with <3 by th3infinity#6720')
            await ctx.send(embed=embed_result)
    else:
        embed_maint = discord.Embed(title='Maintenance',
                                    description='Bot befindet sich im Maintenance Modus! Rangvergabe deaktiviert. Bitte warten.',
                                    color=0xE88100)
        embed_maint.set_footer(text='made with <3 by th3infinity#6720')
        await ctx.send(embed=embed_maint)


@autoRank.error
async def autoRank_on_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title='autoRank', description='Fehlendes Argument! `-autoRank <roleName>', color=0xFF0000)
        embed.set_footer(text='made with <3 by th3infinity#6720')
        await ctx.send(embed=embed)


async def getStats(ctx, name, platform, nameConvention=True):
    accname = ""
    overall_kd = 0
    overall_winRatio = 0
    overall_matches = 0
    overall_wins = 0
    overall_kills = 0
    solostats = {"kills": 0, "wins": 0, "matches": 0, "kd": 0, "winRatio": 0}
    duostats = {"kills": 0, "wins": 0, "matches": 0, "kd": 0, "winRatio": 0}
    squadstats = {"kills": 0, "wins": 0, "matches": 0, "kd": 0, "winRatio": 0}

    overall_kd_old = 0
    overall_winRatio_old = 0
    overall_matches_old = 0
    overall_wins_old = 0
    overall_kills_old = 0
    solostats_old = {"kills": 0, "wins": 0, "matches": 0, "kd": 0, "winRatio": 0}
    duostats_old = {"kills": 0, "wins": 0, "matches": 0, "kd": 0, "winRatio": 0}
    squadstats_old = {"kills": 0, "wins": 0, "matches": 0, "kd": 0, "winRatio": 0}

    resp = requests.get(url.format(platform.lower(), name), headers=headers)

    response = json.loads(resp.text)

    #print(response)

    try:
        accname = response["epicUserHandle"]
    except KeyError:
        results = {'accname': ''}
        embed_username = discord.Embed(title='Win Rate Rank',
                                       description='<@' + str(
                                           ctx.message.author.id) + '> Accname: **' + name + '** nicht gefunden!',
                                       color=0xFF0000)
        embed_username.set_footer(text='made with <3 by th3infinity#6720')
        logger.error('Username not found: ' + name)
        await ctx.send(embed=embed_username)
    else:
        if name.lower() not in ctx.message.author.display_name.lower() and nameConvention:
            embed_displayname = discord.Embed(title='Namenskonvention',
                                              description='Hey <@' + str(
                                                  ctx.message.author.id) + '> wir haben auf unserem Server eine Namenskonvention: `<Fortnitename> | [Spitzname]`',
                                              color=0x008CFF)
            embed_displayname.set_footer(text='made with <3 by th3infinity#6720')
            await ctx.send(embed=embed_displayname)

        logger.info('DisplayName: ' + ctx.message.author.display_name + ' | Used AccName: ' + accname)

        try:
            solostats_old["kills"] = response["stats"]["prior_p2"]["kills"]["valueInt"]
            solostats_old["wins"] = response["stats"]["prior_p2"]["top1"]["valueInt"]
            solostats_old["matches"] = response["stats"]["prior_p2"]["matches"]["valueInt"]
            solostats_old["kd"] = response["stats"]["prior_p2"]["kd"]["valueDec"]
            solostats_old["winRatio"] = response["stats"]["prior_p2"]["winRatio"]["valueDec"]
        except KeyError:
            logger.info("No Old Solo Stats")

        try:
            solostats["kills"] = response["stats"]["curr_p2"]["kills"]["valueInt"]
            solostats["wins"] = response["stats"]["curr_p2"]["top1"]["valueInt"]
            solostats["matches"] = response["stats"]["curr_p2"]["matches"]["valueInt"]
            solostats["kd"] = response["stats"]["curr_p2"]["kd"]["valueDec"]
            solostats["winRatio"] = response["stats"]["curr_p2"]["winRatio"]["valueDec"]
        except KeyError:
            logger.info("No Solo Stats")

        try:
            duostats_old["kills"] = response["stats"]["prior_p10"]["kills"]["valueInt"]
            duostats_old["wins"] = response["stats"]["prior_p10"]["top1"]["valueInt"]
            duostats_old["matches"] = response["stats"]["prior_p10"]["matches"]["valueInt"]
            duostats_old["kd"] = response["stats"]["prior_p10"]["kd"]["valueDec"]
            duostats_old["winRatio"] = response["stats"]["prior_p10"]["winRatio"]["valueDec"]
        except KeyError:
            logger.info("No Old Duo Stats")

        try:
            duostats["kills"] = response["stats"]["curr_p10"]["kills"]["valueInt"]
            duostats["wins"] = response["stats"]["curr_p10"]["top1"]["valueInt"]
            duostats["matches"] = response["stats"]["curr_p10"]["matches"]["valueInt"]
            duostats["kd"] = response["stats"]["curr_p10"]["kd"]["valueDec"]
            duostats["winRatio"] = response["stats"]["curr_p10"]["winRatio"]["valueDec"]
        except KeyError:
            logger.info("No Duo Stats")

        try:
            squadstats_old["kills"] = response["stats"]["prior_p9"]["kills"]["valueInt"]
            squadstats_old["wins"] = response["stats"]["prior_p9"]["top1"]["valueInt"]
            squadstats_old["matches"] = response["stats"]["prior_p9"]["matches"]["valueInt"]
            squadstats_old["kd"] = response["stats"]["prior_p9"]["kd"]["valueDec"]
            squadstats_old["winRatio"] = response["stats"]["prior_p9"]["winRatio"]["valueDec"]
        except KeyError:
            logger.info("No Old Squad Stats")

        try:
            squadstats["kills"] = response["stats"]["curr_p9"]["kills"]["valueInt"]
            squadstats["wins"] = response["stats"]["curr_p9"]["top1"]["valueInt"]
            squadstats["matches"] = response["stats"]["curr_p9"]["matches"]["valueInt"]
            squadstats["kd"] = response["stats"]["curr_p9"]["kd"]["valueDec"]
            squadstats["winRatio"] = response["stats"]["curr_p9"]["winRatio"]["valueDec"]
        except KeyError:
            logger.info("No Squad Stats")

        overall_wins_old = int(solostats_old["wins"]) + int(duostats_old["wins"]) + int(squadstats_old["wins"])
        overall_matches_old = int(solostats_old["matches"]) + int(duostats_old["matches"]) + int(
            squadstats_old["matches"])
        overall_kills_old = int(solostats_old["kills"]) + int(duostats_old["kills"]) + int(
            squadstats_old["kills"])

        if overall_matches_old > 0:
            overall_kd_old = overall_kills_old / (overall_matches_old - overall_wins_old)
            overall_winRatio_old = (overall_wins_old / overall_matches_old) * 100

        logger.info('Calculation Old Season: Wins: {} | Matches: {} | Kills: {} | KD: {} | WinRatio: {}'.format(
            overall_wins_old, overall_matches_old, overall_kills_old, round(overall_kd_old, 2),
            round(overall_winRatio_old, 2)))

        ################
        overall_wins = int(solostats["wins"]) + int(duostats["wins"]) + int(squadstats["wins"])
        overall_matches = int(solostats["matches"]) + int(duostats["matches"]) + int(squadstats["matches"])
        overall_kills = int(solostats["kills"]) + int(duostats["kills"]) + int(squadstats["kills"])

        if overall_matches > 0:
            overall_kd = overall_kills / (overall_matches - overall_wins)
            overall_winRatio = (overall_wins / overall_matches) * 100

        logger.info('Calculation Old Season: Wins: {} | Matches: {} | Kills: {} | KD: {} | WinRatio: {}'.format(
            overall_wins, overall_matches, overall_kills, round(overall_kd, 2),
            round(overall_winRatio, 2)))

        results = {'accname': accname, 'overall_matches': overall_matches, 'overall_matches_old': overall_matches_old, 'overall_winRatio': overall_winRatio, 'overall_winRatio_old': overall_winRatio_old}

    return results


@rank.error
async def rank_on_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title='Win Rate Rank',
                              description='Fehlendes Argument! `-rank <' + ', '.join(platforms) + '> <epicGamesName>`',
                              color=0xFF0000)
        embed.set_footer(text='made with <3 by th3infinity#6720')
        await ctx.send(embed=embed)


@bot.command(hidden=True, pass_context=True, name='getTournaments', aliases=['gettournaments', 'gettour', 'gett', 'gt'])
@commands.check(is_setup)
@commands.check(is_allowed)
async def getTournaments(ctx):
    global umg_posted,egl_posted
    guildID = str(ctx.message.guild.id)
    tournamentsChannelID = botDatabase[guildID]['tournamentChannelID']

    umg_posted = botDatabase[guildID]["umg_posted"]
    egl_posted = botDatabase[guildID]["egl_posted"]


    logger.info('Command -getTournaments from User: ' + str(ctx.message.author.id))
    await ctx.send("Updating Turnier Infos... Das könnte eine Weile dauern!")
    getEGLTournaments()
    getUMGTournaments()

    for egl_t in egl_tournaments:
        if egl_t.tid not in egl_posted:

            tournamentEmbed = discord.Embed(title=egl_t.name,url=egl_t.link, color=0xFFCA34)
            tournamentEmbed.set_thumbnail(url="https://agl.tv/assets/img/logo-xlarge-378f84197d.png")
            tournamentEmbed.add_field(name='Zeit', value=egl_t.time)
            tournamentEmbed.add_field(name='Slots', value=egl_t.slots)
            tournamentEmbed.add_field(name='Eintritt', value=egl_t.costs)
            tournamentEmbed.add_field(name='Hoster', value='EGL')
            tournamentEmbed.set_footer(text='made with <3 by th3infinity#6720')
            await (bot.get_channel(tournamentsChannelID)).send(embed=tournamentEmbed)
            egl_posted.append(egl_t.tid)

    botDatabase[guildID]["egl_posted"] = egl_posted

    for umg_t in umg_tournaments:
        if umg_t.tid not in umg_posted:

            tournamentEmbed = discord.Embed(title=umg_t.name,url=umg_t.link, color=0x202C39)
            tournamentEmbed.set_thumbnail(url="https://seedroid.com/img/post/icons/512/com.umggaming.events.jpg")
            tournamentEmbed.add_field(name='Zeit', value=umg_t.time)
            tournamentEmbed.add_field(name='Slots', value=umg_t.slots)
            tournamentEmbed.add_field(name='Eintritt', value=umg_t.costs)
            tournamentEmbed.add_field(name='Hoster', value='UMG')
            tournamentEmbed.set_footer(text='made with <3 by th3infinity#6720')
            await (bot.get_channel(tournamentsChannelID)).send(embed=tournamentEmbed)
            umg_posted.append(umg_t.tid)

    botDatabase[guildID]["umg_posted"] = umg_posted

    saveDatabase()

    await ctx.send("Erfolgreich Turniere aktualisiert!")


def getEGLTournaments():
    resp = requests.get("https://egl.tv/tournaments/game/fortnite")
    tree = html.fromstring(resp.content)

    gameBoxes = tree.xpath('//div[@class="card__cup"]')

    saveList = []

    for tournament in egl_tournaments:
        saveList.append(tournament.tid)

    for element in gameBoxes:

        platform_div = element.xpath('.//div[@class="card__cup-icons"]')
        platform_i = platform_div[0].xpath('.//i')
        platform = platform_i[0].attrib['title']

        if platform == 'PC':
            name = element.xpath('.//h3[@class="text-truncate"]/text()')
            if len(name) < 1:
                name = ["Unbekannt"]

            details = element.xpath('.//div[@class="card__cup-details"]/text()')
            if len(details) < 1:
                details = ["Unbekannt"]

            slots = element.xpath('.//span[@class="card__cup-counter-slots"]/text()')
            if len(slots) < 1:
                slots = ["Unbekannt"]

            allhref = element.xpath('.//a')
            if len(allhref) > 0:
                link = allhref[0].attrib['href']
                t_id = link.rpartition('/')[2]
            else:
                link = "Unbekannt"
                t_id = "Unbekannt"



            date = element.xpath('.//span[@class="h2"]/text()')
            if len(date) < 1:
                date = ["Unbekannt"]

            time = element.xpath('.//span[@class="type-md"]/text()')
            if len(time) > 0:
                time = time[0].rpartition('-')[2]
                time = time.replace('BST', '')
                time2 = datetime.strptime(time.strip(), '%H:%M')
                time2 = time2 + timedelta(hours=1)
            else:
                time2 = datetime.now()

            if t_id not in saveList:
                newtournament = Tournament(name[0] + ' - ' + details[0],
                                           date[0] + ' - ' + format(time2, '%H:%M Uhr'), '0', link, slots[0],
                                           t_id)
                egl_tournaments.append(newtournament)
                #print(newtournament.id)
                #print(newtournament.name)
                #print(newtournament.time)
                #print(newtournament.costs)
                #print(newtournament.link)
                #print(newtournament.slots)


def getUMGTournaments():
    resp = requests.get("https://umggaming.com/tournaments/platform/epic-games")
    tree = html.fromstring(resp.content)

    gameBoxes = tree.xpath('//li[@class="col-xs-6 margin-30"]')

    saveList = []

    for tournament in umg_tournaments:
        saveList.append(tournament.tid)

    for element in gameBoxes:
        name = element.xpath('.//h3[@class="gray"]/text()')
        if len(name) < 1:
            name = ["Unbekannt"]
        time_unformatted = element.xpath('.//span[@class="light-gray"]/text()')
        if len(time_unformatted) > 1:
            time = datetime.strptime(time_unformatted[1].replace('EDT','').strip(),'%m/%d/%y %I:%M%p')
            time += timedelta(hours=6)
        else:
            time = datetime.now()
        costs = element.xpath('.//div[@class="credits-circle"]/text()')
        if len(costs) < 1:
            costs = ["Unbekannt"]
        allhref = element.xpath('.//a')
        if len(allhref) > 0 and int(costs[0]) == 0:
            link = "https://umggaming.com" + allhref[0].attrib['href']
            t_id = link.rpartition('/')[2]
            if t_id not in saveList:
                resp_slots = requests.get(link)
                tree_slots = html.fromstring(resp_slots.content)
                slots_ul = tree_slots.xpath('//ul[@class="list-unstyled col-sm-4 col-xs-6"]')
                if len(slots_ul) > 1:
                    slots_li = slots_ul[1].xpath('.//li[@class="margin-40"]')
                    slots = slots_li[0].xpath('.//span[@class="light-gray"]/text()')
                else:
                    slots = ["Unbekannt"]

        else:
            link = "Unbekannt"
            slots = ["Unbekannt"]
            t_id = "Unbekannt"

        if t_id not in saveList and int(costs[0]) == 0:
            newtournament = Tournament(name[0], format(time,'%d/%m/%y - %H:%M Uhr'), costs[0] + ' Credits',link,slots[0],t_id)
            umg_tournaments.append(newtournament)
            #print(newtournament.id)
            #print(newtournament.name)
            #print(newtournament.time)
            #print(newtournament.costs)
            #print(newtournament.link)
            #print(newtournament.slots)


@bot.command(hidden=True, pass_context=True, name='exitBot', aliases=['exitbot'])
@commands.check(is_developer)
async def exitBot(ctx):
    logger.info('Command -exitBot from User: ' + str(ctx.message.author.id))
    logger.info("Bot Disconnecting...")
    embed = discord.Embed(title='Snipe', description='Bot disconnecting...', color=0xFF0000)
    embed.set_footer(text='made with <3 by th3infinity#6720')
    await ctx.send(embed=embed)
    await bot.logout()
    await bot.close()
    sys.exit()


@bot.command(pass_context=True, name='info', aliases=['Info', 'i'], help='Postet eine Info zum Bot')
async def info(ctx):
    logger.info('Command -info from User: ' + str(ctx.message.author.id))
    embed = discord.Embed(title='Info',
                          description='Fortnite Bot - Autom. WinRate Rollen | Turnier Crawler!',
                          url="https://github.com/th3infinity/Fortnite-Bot",
                          color=0x008CFF)
    embed.add_field(name='Developer', value='<@198844841977708545>')
    embed.add_field(name='Version', value=version)
    embed.add_field(name='Last Updated', value=lastupdated)
    embed.set_footer(text='made with <3 by th3infinity#6720')
    await ctx.send(embed=embed)


@bot.command(pass_context=True, name='changeLog', aliases=['changelog', 'clog'], help='Postet den aktuellen Bot '
                                                                                      'ChangeLog')
async def changeLog(ctx):
    logger.info('Command -changeLog from User: ' + str(ctx.message.author.id))
    embed = discord.Embed(title='Change Log', description=changelog, color=0x008CFF)
    embed.add_field(name='Developer', value='<@198844841977708545>')
    embed.add_field(name='Version', value=version)
    embed.add_field(name='Last Updated', value=lastupdated)
    embed.set_footer(text='made with <3 by th3infinity#6720')
    await ctx.send(embed=embed)


def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    handler = logging.FileHandler('log_' + strftime("%Y-%m-%d_%H-%M-%S", localtime()) + '.txt', mode='w')
    handler.setFormatter(formatter)
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(screen_handler)
    return logger


@bot.event
async def on_command_error(ctx, error):
    if is_allowedchannel(ctx):
        if isinstance(error, commands.CommandNotFound):
            logger.error('Command not found: ' + ctx.message.content + ' from User: ' + ctx.message.author.name)
            embed = discord.Embed(title='Stats Bot',
                                  description='Command nicht gefunden. `-commandList` für eine Liste aller Commands',
                                  color=0xFF0000)
            embed.set_footer(text='made with <3 by th3infinity#6720')
            await ctx.send(embed=embed)

        if isinstance(error, commands.CheckFailure):
            logger.error('No Permission for Command: ' + ctx.message.content + ' from User: ' + ctx.message.author.name)
            embed = discord.Embed(title='Stats Bot',
                                  description='Keine Berechtigung für dieses Command!',
                                  color=0xFF0000)
            embed.set_footer(text='made with <3 by th3infinity#6720')
            await ctx.send(embed=embed)


@bot.event
async def on_ready():
    global logger
    logger = setup_custom_logger('Fortnite Bot')
    await bot.change_presence(activity=discord.Game(name='-info | -commandList'))
    logger.info('Logged in as:')
    logger.info(bot.user.name)
    logger.info(bot.user.id)
    print('-------------------------------------------------')

    embed = discord.Embed(title='Bot Just Restarted', description='Here is the current Change Log: \n' + changelog,
                          color=0x008CFF)
    embed.add_field(name='Developer', value='<@198844841977708545>')
    embed.add_field(name='Version', value=version)
    embed.add_field(name='Last Updated', value=lastupdated)
    embed.set_footer(text='made with <3 by th3infinity#6720')
    for guildID in botDatabase:
        if guildID not in ['testToken', 'realToken', 'trnKey']:
            await (bot.get_channel(botDatabase[guildID]['botspamID'])).send(embed=embed)


bot.run(TOKEN[0])
