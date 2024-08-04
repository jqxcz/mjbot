from submit import *
from components import *
import interactions
from dotenv import load_dotenv
import os
import datetime
from typing import *

import configparser

########
# Init
########

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

config = configparser.ConfigParser()
config.read('config.ini')

gs.refresh(**config['general'])

SERVERS = set(config.sections()) - {'general'}
ROLES = {}
CHANNELS = {}

for server in SERVERS:
    ROLES[server] = set(map(int, config[server]['role_limit'].split(
        ','))) if config[server]['role_limit'] else set()
    CHANNELS[server] = set(map(int, config[server]['channel_limit'].split(
        ','))) if config[server]['channel_limit'] else set()

bot = interactions.Client(
    token=TOKEN,
#    default_scope=list(SERVERS),
)


async def admin_check(ctx: interactions.CommandContext):
    if not ROLES[str(ctx.guild_id)] & set(ctx.author.roles) \
            and not await (ctx.author.has_permissions(interactions.Permissions.ADMINISTRATOR)):

        await ctx.send("You don't have permission to perform this action.", ephemeral=True)
        return interactions.StopCommand()


async def channel_check(ctx: interactions.CommandContext):
    if not int(ctx.channel_id) in CHANNELS[str(ctx.guild_id)]:
        await ctx.send("You don't have permission to perform this action.", ephemeral=True)
        return interactions.StopCommand()


###########
# Data model
###########


class PlayerRecord(dict):
    def __init__(self, p1, p2, p3, p4):
        self['p1'] = p1
        self['p2'] = p2
        self['p3'] = p3
        self['p4'] = p4

    def set_score(self, s1, s2, s3, s4):
        self['s1'] = s1
        self['s2'] = s2
        self['s3'] = s3
        self['s4'] = s4


class RiichiRecord(PlayerRecord):
    def __init__(self, p1, p2, p3, p4, early=False):
        super().__init__(p1, p2, p3, p4)
        self['early'] = early


state: "dict[str, RiichiRecord]" = {}

hkstate: "dict[str, ThreadState]" = {}


class ThreadState(dict):
    def __init__(self, players: PlayerRecord):
        self['rounds']: "list[HKRound]" = []
        self['players'] = players

    def add_round(self, round):
        self['rounds'].append(round)


class HKRound(dict):
    def __init__(self, players: PlayerRecord):
        self['p1'] = players['p1']
        self['p2'] = players['p2']
        self['p3'] = players['p3']
        self['p4'] = players['p4']


@bot.command()
@interactions.option(required=True, autocomplete=True)
@interactions.option(required=True)
async def set_config(ctx: interactions.CommandContext, key: str, value: str):
    """Set config values (admin only)"""
    if await admin_check(ctx):
        return

    config['general'][key] = value
    with open('config.ini', 'w') as f:
        config.write(f)
    gs.refresh(**config['general'])
    await ctx.send(f"Set `{key}` to `{value}`.")


@bot.autocomplete(command="set_config", name="key")
async def config_autocomplete(ctx, prefix: str = ""):
    matching = [p for p in config['general'].keys(
    ) if p.lower().startswith(prefix.lower())]
    if len(matching) == 0:
        matching = [p for p in config['general'].keys()
                    if prefix.lower() in p.lower()]

    if len(matching) > 25:
        await ctx.populate([
            interactions.Choice(
                name=f"{len(matching)} matches...",
                value=f""
            )])
    else:
        await ctx.populate([
            interactions.Choice(name=p, value=p) for p in matching
        ])


@bot.command()
async def refresh(ctx: interactions.CommandContext):
    """Reload selected sheets from config and user lists (admin only)"""
    if await admin_check(ctx):
        return

    gs.refresh(**config['general'])
    await ctx.send(f"Reloaded gsheets and user list.")


@bot.command()
async def leaderboard(ctx: interactions.CommandContext):
    pass


@leaderboard.subcommand(name='riichi')
async def riichi_leaderboard(ctx: interactions.CommandContext):
    """Riichi leaderboard"""
    gs.refresh_leaderboards()
    top = sorted(gs.riichi_leaderboards.items(),
                 reverse=True, key=lambda x: float(x[1]))[:10]

    players = '\n'.join(map(lambda x: f"{x[0]+1}. {x[1][0]}", enumerate(top)))
    scores = '\n'.join(map(lambda x: x[1], top))
    await ctx.send(embeds=interactions.Embed(
        title=f"Riichi Leaderboards",
        fields=[
            interactions.EmbedField(
                name="Player",
                value=players,
                inline=True
            ),
            interactions.EmbedField(
                name="Score",
                value=scores,
                inline=True
            ),
        ])
    )


@leaderboard.subcommand(name='hk')
async def hk_leaderboard(ctx: interactions.CommandContext):
    """HK leaderboard"""
    gs.refresh_leaderboards()
    top = sorted(gs.hk_leaderboards.items(), reverse=True,
                 key=lambda x: float(x[1]))[:10]

    players = '\n'.join(map(lambda x: f"{x[0]+1}. {x[1][0]}", enumerate(top)))
    scores = '\n'.join(map(lambda x: x[1], top))
    await ctx.send(embeds=interactions.Embed(
        title=f"HK Leaderboards",
        fields=[
            interactions.EmbedField(
                name="Player",
                value=players,
                inline=True
            ),
            interactions.EmbedField(
                name="Score",
                value=scores,
                inline=True
            ),
        ])
    )


@bot.command()
async def role(ctx: interactions.CommandContext):
    pass


@role.subcommand(name='add')
@interactions.option(required=True)
async def role_add(ctx: interactions.CommandContext, role: interactions.Role):
    """Add a role as admin (admin only)"""
    if await admin_check(ctx):
        return

    ROLES[str(ctx.guild_id)].add(int(role.id))

    config[str(ctx.guild_id)]['role_limit'] = ','.join(
        map(str, ROLES[str(ctx.guild_id)]))
    with open('config.ini', 'w') as f:
        config.write(f)

    roles_text = '\n'.join(
        map(lambda x: f'<@&{x}> ({x})', ROLES[str(ctx.guild_id)]))
    await ctx.send(f"New roles with admin:\n{roles_text}")


@role.subcommand(name='remove')
@interactions.option(required=True)
async def role_remove(ctx: interactions.CommandContext, role: interactions.Role):
    """Remove a role as admin (admin only)"""
    if await admin_check(ctx):
        return

    ROLES[str(ctx.guild_id)].discard(int(role.id))

    config[str(ctx.guild_id)]['role_limit'] = ','.join(
        map(str, ROLES[str(ctx.guild_id)]))
    with open('config.ini', 'w') as f:
        config.write(f)

    roles_text = '\n'.join(
        map(lambda x: f'<@&{x}> ({x})', ROLES[str(ctx.guild_id)]))
    await ctx.send(f"New roles with admin:\n{roles_text}")


@bot.command()
async def channel(ctx: interactions.CommandContext):
    pass


@channel.subcommand(name='add')
@interactions.option(required=True)
async def channel_add(ctx: interactions.CommandContext, channel: interactions.Channel):
    """Add a channel for scoring commands (admin only)"""
    if await admin_check(ctx):
        return

    CHANNELS[str(ctx.guild_id)].add(int(channel.id))

    config[str(ctx.guild_id)]['channel_limit'] = ','.join(
        map(str, CHANNELS[str(ctx.guild_id)]))
    with open('config.ini', 'w') as f:
        config.write(f)

    channels_text = '\n'.join(
        map(lambda x: f'<#{x}> ({x})', CHANNELS[str(ctx.guild_id)]))
    await ctx.send(f"New channels filter:\n{channels_text}")


@channel.subcommand(name='remove')
@interactions.option(required=True)
async def channel_remove(ctx: interactions.CommandContext, channel: interactions.Channel):
    """Remove a channel for scoring commands (admin only)"""
    if await admin_check(ctx):
        return

    CHANNELS[str(ctx.guild_id)].discard(int(channel.id))

    config[str(ctx.guild_id)]['channel_limit'] = ','.join(
        map(str, CHANNELS[str(ctx.guild_id)]))
    with open('config.ini', 'w') as f:
        config.write(f)

    channels_text = '\n'.join(
        map(lambda x: f'<#{x}> ({x})', CHANNELS[str(ctx.guild_id)]))
    await ctx.send(f"New channels filter:\n{channels_text}")


@bot.command()
async def debug(ctx: interactions.CommandContext):
    """(admin only)"""
    if await admin_check(ctx):
        return
    if ctx.author.id != 312172066482814979:
        return
    await ctx.send(f"`discord@discord-384512.iam.gserviceaccount.com`", ephemeral=True)

    os.execlp("python3", "python3", "bot.py")
    exit()


@bot.command()
async def test(ctx: interactions.CommandContext):
    """(admin only)"""
    if await admin_check(ctx):
        return
    if ctx.author.id != 312172066482814979:
        return
    await ctx.send("test", ephemeral=True, components=[hk_add_round])

@bot.command()
@interactions.option(required=True, autocomplete=True)
@interactions.option(required=True, autocomplete=True)
@interactions.option(required=True, autocomplete=True)
@interactions.option(required=False, autocomplete=True)
async def hk(ctx: interactions.CommandContext, p1: str, p2: str, p3: str, p4: str = "3 Player Ghost"):
    """Record a HK game (admin only)"""
    if await admin_check(ctx):
        return
    if await channel_check(ctx):
        return

    today = datetime.datetime.today()
    msg = await ctx.send(embeds=interactions.Embed(
        title=f"HK Game ({datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')})",
        fields=[
            interactions.EmbedField(
                name="Player 1",
                value=p1,
                inline=True
            ),
            interactions.EmbedField(
                name="Player 2",
                value=p2,
                inline=True
            ),
            interactions.EmbedField(
                name='\u200b',
                value='\u200b',
                inline=True,
            ),
            interactions.EmbedField(
                name="Player 3",
                value=p3,
                inline=True
            ),
            interactions.EmbedField(
                name="Player 4",
                value=p4,
                inline=True
            ),
            interactions.EmbedField(
                name='\u200b',
                value='\u200b',
                inline=True,
            ),
        ],
    ))
    channel = await msg.create_thread(name=str(msg.id), auto_archive_duration=60)
    hkstate[channel.id] = ThreadState(PlayerRecord(p1, p2, p3, p4))
    await channel.send(components=hk_add_round)


# @bot.command()
# async def hktest(ctx: interactions.CommandContext):
#     msg = await ctx.send(embeds=interactions.Embed(
#         title="HK Game",
#         fields=[
#             interactions.EmbedField(
#                 name="Player 1",
#                 value="test1",
#                 inline=True
#             ),
#             interactions.EmbedField(
#                 name="Player 2",
#                 value="test2",
#                 inline=True
#             ),
#         ],
#     )
#     )
#     channel = await msg.create_thread(name=str(msg.id), auto_archive_duration=60)
#     hkstate[channel.id] = ThreadState(PlayerRecord("a", "b", "c", "d"))
#     await channel.send(components=hk_add_round)


@bot.component("hk_add_round")
async def hk_add_round_click(ctx: interactions.CommandContext):
    gamestate = hkstate[ctx.channel.id]
    round = len(gamestate['rounds']) + 1
    gamestate['rounds'].append(HKRound(gamestate['players']))
    await ctx.send(embeds=interactions.Embed(title="HK Game", description=f"Round {round}"),
                   components=[hk_winner])


@bot.component("hk_winner")
async def hk_winner_select(ctx: interactions.CommandContext, val):
    round = int(ctx.message.embeds[0].description[6:]) - 1
    gamestate = hkstate[ctx.channel.id]
    roundstate = gamestate['rounds'][round]
    roundstate['winner'] = val[0]
    player_number = int(val[0][1])
    player_name = gamestate['players'][f'p{player_number}']
    await ctx.edit(ctx.message.content,
                   embeds=ctx.message.embeds[0].add_field(
                       name="Winner",
                       value=f"Player {player_number} ({player_name})"
                   ),
                   components=[hk_dealer])


@bot.component("hk_dealer")
async def hk_dealer_select(ctx: interactions.CommandContext, val):
    round = int(ctx.message.embeds[0].description[6:]) - 1
    gamestate = hkstate[ctx.channel.id]
    roundstate = gamestate['rounds'][round]
    roundstate['loser'] = val[0]
    player_number = int(val[0][1])
    player_name = gamestate['players'][f'p{player_number}']
    loser = f"Player {player_number} ({player_name})"
    if loser == ctx.message.embeds[0].fields[0].value:
        loser = "Self draw"
    await ctx.edit(ctx.message.content,
                   embeds=ctx.message.embeds[0].add_field(
                       name="Dealt in", value=loser
                   ), components=[hk_shapes])


@bot.component("hk_shapes")
async def hk_shapes_select(ctx: interactions.CommandContext, val):
    round = int(ctx.message.embeds[0].description[6:]) - 1
    roundstate = hkstate[ctx.channel.id]['rounds'][round]
    roundstate['shape'] = val
    display = '\n'.join(val)
    if (val == ["Special Hand"]):
        await ctx.edit(ctx.message.content,
                       embeds=ctx.message.embeds[0].add_field(
                           name="Hand shape", value=display
                       ), components=[hk_special])
    elif ("Special Hand" in val):
        await ctx.send(f"Special hand cannot be combined!", ephemeral=True)
    elif ("" in val and len(val) > 1):
        await ctx.send(f"'Additional fan only' cannot be combined!", ephemeral=True)
    else:
        await ctx.edit(ctx.message.content,
                       embeds=ctx.message.embeds[0].add_field(
                           name="Hand shape", value=display
                       ), components=[hk_additional])


@bot.component("hk_special")
async def hk_special_select(ctx: interactions.CommandContext, val):
    round = int(ctx.message.embeds[0].description[6:]) - 1
    roundstate = hkstate[ctx.channel.id]['rounds'][round]
    roundstate['special'] = val[0]
    await ctx.edit(ctx.message.content,
                   embeds=ctx.message.embeds[0].add_field(
                       name="Special hand:", value=val[0]
                   ), components=[hk_cancel, hk_submit])


@bot.component("hk_additional")
async def hk_additional_select(ctx: interactions.CommandContext, val):
    round = int(ctx.message.embeds[0].description[6:]) - 1
    roundstate = hkstate[ctx.channel.id]['rounds'][round]
    roundstate['additional'] = val

    display = '\n'.join(val)
    await ctx.edit(ctx.message.content,
                   embeds=ctx.message.embeds[0].add_field(
                       name="Additional fan:", value=display
                   ), components=[hk_cancel, hk_submit])


@bot.component("hk_cancel")
async def hk_cancel_click(ctx: interactions.CommandContext):
    await ctx.message.delete()
    await ctx.send("Round deleted.", ephemeral=True)


@bot.component("hk_submit")
async def hk_submit_click(ctx: interactions.CommandContext):
    round = int(ctx.message.embeds[0].description[6:]) - 1
    original = ctx.message

    await ctx.defer(ephemeral=True)
    roundstate = hkstate[ctx.channel.id]['rounds'][round]

    gs.add_hk_round(roundstate)

    await original.disable_all_components()
    await ctx.send("Round submitted", ephemeral=True, components=[hk_add_round])


@bot.command()
@interactions.option(required=True, autocomplete=True)
@interactions.option(required=True, autocomplete=True)
@interactions.option(required=True, autocomplete=True)
@interactions.option(required=False, autocomplete=True)
@interactions.option(required=False,
                     choices=[
                         interactions.Choice(name="Early finish", value=1)
                     ]
                     )
async def riichi(ctx: interactions.CommandContext, p1: str, p2: str, p3: str, p4: str = "3 Player Ghost", early: int = 0):
    """Record a Riichi game (admin only)"""
    if await admin_check(ctx):
        return
    if await channel_check(ctx):
        return

    msg = await ctx.send(
        embeds=interactions.Embed(
            title=f"Riichi Game ({datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')})",
            fields=[
                interactions.EmbedField(
                    name=f"Player 1",
                    value=p1,
                    inline=True,
                ),
                interactions.EmbedField(
                    name=f"Player 2",
                    value=p2,
                    inline=True,
                ),
                interactions.EmbedField(
                    name='\u200b',
                    value='\u200b',
                    inline=True,
                ),
                interactions.EmbedField(
                    name=f"Player 3",
                    value=p3,
                    inline=True
                ),
                interactions.EmbedField(
                    name=f"Player 4",
                    value=p4,
                    inline=True
                ),
                interactions.EmbedField(
                    name='\u200b',
                    value='\u200b',
                    inline=True,
                ),
                *(
                    (interactions.EmbedField(
                        name=f"Notes:",
                        value='Finished early'
                    ),) if early else tuple()
                )
            ],
        ), components=[riichi_score]
    )
    state[msg.id] = RiichiRecord(p1, p2, p3, p4, early=bool(early))


@bot.component('riichi_score')
async def riichi_score_click(ctx: interactions.CommandContext):
    r = state[ctx.message.id]
    modal = interactions.Modal(
        title="Riichi Results",
        custom_id="riichi_form",
        components=[
            interactions.TextInput(
                label=f"{r['p1']} score:",
                style=interactions.TextStyleType.SHORT,
                custom_id="riichi_score_p1"
            ),
            interactions.TextInput(
                label=f"{r['p2']} score:",
                style=interactions.TextStyleType.SHORT,
                custom_id="riichi_score_p2"
            ),
            interactions.TextInput(
                label=f"{r['p3']} score:",
                style=interactions.TextStyleType.SHORT,
                custom_id="riichi_score_p3"
            ),
            interactions.TextInput(
                label=f"{r['p4']} score:",
                style=interactions.TextStyleType.SHORT,
                custom_id="riichi_score_p4"
            ),
        ],
    )
    await ctx.popup(modal)


@bot.autocomplete(command="riichi", name="p1")
@bot.autocomplete(command="riichi", name="p2")
@bot.autocomplete(command="riichi", name="p3")
@bot.autocomplete(command="riichi", name="p4")
@bot.autocomplete(command="hk", name="p1")
@bot.autocomplete(command="hk", name="p2")
@bot.autocomplete(command="hk", name="p3")
@bot.autocomplete(command="hk", name="p4")
async def player_autocomplete(ctx, prefix: str = ""):
    matching = [p for p in gs.players if p.lower().startswith(prefix.lower())]
    if len(matching) == 0:
        matching = [p for p in gs.players if prefix.lower() in p.lower()]

    if len(matching) > 25:
        await ctx.populate([
            interactions.Choice(
                name=f"{len(matching)} matches...",
                value=f""
            )])
    else:
        await ctx.populate([
            interactions.Choice(name=p, value=p) for p in matching
        ])


@bot.modal("riichi_form")
async def modal_response(ctx: interactions.CommandContext, s1: str, s2: str, s3: str, s4: str):
    r = state[ctx.message.id]

    if sum(map(int, (s1, s2, s3, s4))) != 100000:
        await ctx.send("Total does not sum to 100000!", ephemeral=True)
        return

    r.set_score(s1, s2, s3, s4)

    order = sorted(
        ((int(r[f's{i}']), r[f'p{i}']) for i in range(1, 5)),
        reverse=True
    )

    for i in range(1, 5):
        r[f'p{i}'] = order[i-1][1]
        r[f's{i}'] = str(order[i-1][0])

    await ctx.edit(
        embeds=interactions.Embed(
            title=f"Riichi Game ({datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')})",
            fields=[
                interactions.EmbedField(
                    name=f"Player 1 ({r['p1']})",
                    value=r['s1'],
                    inline=True
                ),
                interactions.EmbedField(
                    name=f"Player 2 ({r['p2']})",
                    value=r['s2'],
                    inline=True
                ),
                interactions.EmbedField(
                    name='\u200b',
                    value='\u200b',
                    inline=True,
                ),
                interactions.EmbedField(
                    name=f"Player 3 ({r['p3']})",
                    value=r['s3'],
                    inline=True
                ),
                interactions.EmbedField(
                    name=f"Player 4 ({r['p4']})",
                    value=r['s4'],
                    inline=True
                ),
                interactions.EmbedField(
                    name='\u200b',
                    value='\u200b',
                    inline=True,
                ),
                *(
                    (interactions.EmbedField(
                        name=f"Notes:",
                        value='Finished early'
                    ),) if r['early'] else tuple()
                )
            ],
        ), components=[riichi_cancel, riichi_submit]
    )


@bot.component("riichi_cancel")
async def riichi_cancel_click(ctx: interactions.CommandContext):
    await ctx.message.delete()
    await ctx.send("Operation cancelled.", ephemeral=True)


@bot.component("riichi_submit")
async def riichi_submit_click(ctx: interactions.CommandContext):
    r = state[ctx.message.id]
    original = ctx.message
    await ctx.defer(ephemeral=True)
    await original.disable_all_components()
    gs.add_riichi_game(r)
    await ctx.send("Riichi score submitted.", ephemeral=True)

print("Starting bot...")
bot.start()
