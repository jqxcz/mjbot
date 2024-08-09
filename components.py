import interactions

riichi_submit = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Submit",
    custom_id="riichi_submit"
)
riichi_cancel = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="Cancel",
    custom_id="riichi_cancel"
)

riichi_score = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Set Score",
    custom_id="riichi_score"
)

hk_winner = interactions.SelectMenu(
    type=interactions.ComponentType.SELECT,
    options=[
        interactions.SelectOption(
            label=f"Player {i}",
            value=f"p{i}",
            description="",
        )
        for i in range(1, 5)
    ],
    custom_id="hk_winner",
    placeholder="Winner",
)
hk_dealer = interactions.SelectMenu(
    type=interactions.ComponentType.SELECT,
    options=[
        interactions.SelectOption(
            label=f"Player {i}",
            value=f"p{i}",
            description="",
        )
        for i in range(1, 5)
    ],
    custom_id="hk_dealer",
    placeholder="Loser",
)

hk_shape_values = [
    "All Chow/Blitz (+1)",
    "All Pong (+3)",
    "Half Flush (+3)",
    "Full Flush (+7)",
    "Terminals and Honours (+2)",
    "Little Three Dragons (5)",
    "Big Three Dragons (8)",
    "Special Hand",
]
            
hk_shapes = interactions.SelectMenu(
    type=interactions.ComponentType.SELECT,
    options=[
        *(interactions.SelectOption(
            label=v,
            value=v,
            description="",
        ) for v in hk_shape_values),
        interactions.SelectOption(
            label="Additional fan only (0)",
            value="<none>",
            description="",
        )
    ],
    custom_id="hk_shapes",
    placeholder="Combinable hands",
    max_values=7,
    min_values=0,
)

hk_special_values = [
    "Jade Dragon (10)",
    "Pearl Dragon (10)",
    "Ruby Dragon (10)",
    "Thirteen Orphans (13)",
    "All Honours (13)",
    "Hidden Treasures (13)",
    "All Terminals (13)",
    "Nine Gates (13)",
    "All Kongs (13)",
    "Little Four Winds (13)",
    "Big Four Winds (13)",
    "All 8 Flowers (13)",
    "East Initial Heavenly Hand (13)",
    "Non-East Earthly Hand off Discard (13)",
]

hk_special = interactions.SelectMenu(
    type=interactions.ComponentType.SELECT,
    options=[
        interactions.SelectOption(
            label=v,
            value=v,
            description=v,
        )
        for v in hk_special_values
    ],
    custom_id="hk_special",
    placeholder="Select special hand",
)

hk_additional_values = [
    "Pong of Jade Dragons (+1)",
    "Pong of Pearl Dragons (+1)",
    "Pong of Ruby Dragons (+1)",
    "Pong of Player's Own Wind (+1)",
    "Pong of Round Wind (+1)",
    "Own Flower (+1)",
    "Own Season (+1)",
    "No Flower/Season (+1)",
    "Set of 4 Flowers/Seasons (+2)",
    "Self-Draw (+1)",
    "Self-Draw off Last Tile of the Wall (+2)",
    "Win off Last Discard (+1)",
    "Win off Robbing a Kong (+1)",
    "Concealed Hand (+1)",
]
hk_additional = interactions.SelectMenu(
    type=interactions.ComponentType.SELECT,
    options=[
        *(interactions.SelectOption(
                label=v,
                value=v,
                description='',
            )
            for v in hk_additional_values
        ),
        interactions.SelectOption(
            label="Rinshan (Win off Kong Replacement Tile) (+1)",
            value="Win off Last Tile Drawn through a Kong (+1)",
            description="",
        ),
        interactions.SelectOption(
            label='None',
            value='<none>',
            description='',
        )
    ],
    min_values=0,
    max_values=len(hk_additional_values),
    custom_id="hk_additional",
    placeholder="Select additional fan",
)

hk_add_round = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Add Round",
    custom_id="hk_add_round"
)


hk_submit = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Submit Round",
    custom_id="hk_submit"
)

hk_cancel = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="Cancel Round",
    custom_id="hk_cancel"
)


