# Mahjong bot

## Usage:
Set `.env` to contain `DISCORD_TOKEN=[bot token here]`

Create a google api account, and set `GOOGLE_API=<token here>` and `GOOGLE_APPLICATION_CREDENTIALS='./service.json'`
also in `.env`

Create `client_secret.json` like [here](https://pygsheets.readthedocs.io/en/stable/authorization.html)

Create `config.ini` as follows:

In `[general]` section: set `riichi_doc`, `riichi_sheet` and `riichi_players`, `hk_doc`, `hk_sheet` and `hk_players`.

`_doc` variant is google sheets url. `_sheet` is the id of the sheet for entry, `_players` is the id of the sheet for player autocomplete.

Then set `[<server_id_here]` for `role_limit` and `channel_limit` as csv, for role id and channel id in discord.

Make sure to give permissions to the google api account you created.