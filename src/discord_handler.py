from discord_webhook import DiscordWebhook, DiscordEmbed






def send_zero_matches_backend( product: dict ) -> None:
    webhook = DiscordWebhook(url="https://discord.com/api/webhooks/1227630360553066526/nUAxToDsEeUglOauRvA03DbmtcIw_J7J9VRgOsB77AGR14cr-WigowSCwmz-k55venWF")
    print(product['name'])
    embed = DiscordEmbed(title=product['name'], color=0xF5851B)
    embed.add_embed_field(name="Price", value=f"{product['price']}")
    embed.add_embed_field(name="SKU", value=f"``{product['sku']}``")
    embed.add_embed_field(name="Part Number", value=f"``{product['part_number']}``")
    print(product['image'])
    embed.set_image(url=product['image'])
    embed.set_footer(text="AutoParts Monitor Powered by PriceErrors")
    webhook.add_embed(embed)

    response = webhook.execute()