import asyncio

from transfermarkt_api import Transfermarkt

async def main() -> None:
    async with Transfermarkt() as tm:
        # squad = await tm.club_players("985")
        # for player in squad.players:
        #     print(player.shirt_number, player.name, player.position, player.market_value)
        # print(squad.model_dump(mode="json", by_alias=True))

        player = await tm.player_stats("278654")
        clean_json = player.model_dump_json(by_alias=True,indent=2)
        print("\n".join(clean_json.splitlines()[:60]))
        print("... [truncated] ...")
asyncio.run(main())