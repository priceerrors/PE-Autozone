from discord_webhook import DiscordWebhook, DiscordEmbed
import time
import requests
import os


def calculate_discount( original_price: float, sale_price: float ) -> float:
    deal_price_difference = round(float(float(original_price) - float(sale_price)), 2)
    deal_percent_off = float(deal_price_difference)/float(original_price)
    discount = round(deal_percent_off*100)
    return discount



def send_webhook( product: list ) -> None:
    print("sending hook")
    discount = calculate_discount(product['old_price'], product['price'])

    if int(discount) > 0 and int(discount) <= 49:
        webhook = "https://discord.com/api/webhooks/1245064631446278174/qoOZ8GsI589Mo3jc0-1mpQ8pnfk1yeZ9ovW3aOJ8M1VUrPB8ZYRF2Xmv6n3HrUJuB4H8"
    elif int(discount) > 50 and int(discount) <= 69:
        webhook = "https://discord.com/api/webhooks/1245064805413294131/Pr_okVT19I_VxRAI6YjWMJGcLPtylnphkhgxM7agoGEWmBj-0Svg8Vqb9806ST4TRcQW"
    elif int(discount) > 70:
        webhook = "https://discord.com/api/webhooks/1245064904432554128/n7qxm6gHBQNFivKwQmOg270Qc_8kY6MY2y7nn1n5-qFizhhm6aDR9u4ncLOU7brVyEof"
    else:
        webhook = "https://discord.com/api/webhooks/1245063761224667276/_0ZHc_lJyJaHdSzJ9Zs5OchgX_uA5xUV-e8qgmEQEX1ATsel6lxAlFtDKmLUlWCMgTHk"

    webhook = DiscordWebhook(url=webhook)
    embed = DiscordEmbed(title=product['name'], color=0xF5851B, url = f"https://www.autozone.com/searchresult?searchText={product['sku']}")
    embed.add_embed_field(name="Original Price", value=f"$~~{product['old_price']}~~")
    embed.add_embed_field(name="Price", value=f"${product['price']}")
    embed.add_embed_field(name="Discount", value=f"{discount}%")
    embed.add_embed_field(name="Part Number", value=f"``{product['part_number']}``")
    embed.add_embed_field(name="SKU", value=f"``{product['sku']}``")
    embed.add_embed_field(name="Online Stock", value=f"``{product['shipping_quantity']}``")

    # # Download the image locally
    # image_filename = os.path.basename(product['image'])
    # print(product['image'])
    # image_path = f"../database/images/{image_filename}"  # Replace with the desired save path
    # response = requests.get(product['image'])
    # with open(image_path, 'wb') as f:
    #     f.write(response.content)

    # # Attach the image to the embed
    # embed.set_image(url=f"attachment://{image_filename}")

    # # Delete the image from saved
    # os.remove(image_path)


    embed.set_footer(text="AutoZone Monitor Powered by PriceErrors")
    webhook.add_embed(embed)

    response = webhook.execute()
    time.sleep(1)
