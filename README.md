# Mahjong bot

## Usage:
Set `.env` to contain `DISCORD_TOKEN=[bot token here]`

Create `client_secret.json` like [here](https://pygsheets.readthedocs.io/en/stable/authorization.html)

Create `config.ini` as follows:

In `[general]` section: set `riichi_doc`, `riichi_sheet` and `riichi_players`, `hk_doc`, `hk_sheet` and `hk_players`.

Then set `[<server_id_here]` for `role_limit` and `channel_limit` as csv, for role id and channel id in discord.
