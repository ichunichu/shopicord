import asyncio


import discord
from discord import InputTextStyle, Interaction

from discord.embeds import EmptyEmbed
from discord.ext import commands
from discord.ui import InputText


from dotenv import load_dotenv


from utility.database import Database


load_dotenv()
import os

TOKEN=os.environ.get("TOKEN")
apikey = os.environ.get("DATABASE_API")
database = Database()



# noinspection PyBroadException
class MyClient(commands.Bot):
    def __init__(self,command_prefix) -> None:
        self.bot = super().__init__(command_prefix=command_prefix)
        self.db = database
        self.prefix = ";"
        self.followup = {}
        self.shop = {}
        self.product = []

    def add_followup(self,key="",type="",offer="",offer_data="",shop_id="",shop_data="",channel_id=""):
        if key:
            self.followup[key] = {"type":type,"shop_id":shop_id,"shop_data":shop_data,"offer":offer,"offer_data":offer_data,"channel_id":channel_id}
        else:
            print("YOU NEED TO ADD A KEY")

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def getCategories(self, guildid):
        guild = await self.fetch_guild(guildid)
        print(guild.categories)

    async def shopChannel(self, shop_id):
        print(shop_id)
        shop = self.db.getShop(shop_id=shop_id)
        # print(shop)
        cat = False
        guild = self.get_guild(shop[1])
        print(guild)
        print("CATEGORIES", guild.categories)
        for categorie in guild.categories:
            print(categorie.name)
            if categorie.name.upper() == "SHOP":
                cat = categorie
        if not cat:
            cat = await guild.create_category("Shop")
        for channel in cat.channels:
            if channel.id == shop[5]:
                await channel.send(f"**{shop[3]}** by <@{shop[2]}>\n{shop[4]}")
                return channel
        shopchannel = await cat.create_text_channel(shop[3])
        self.db.updateCurrentChannel(shopchannel.id, shop[0])
        await shopchannel.send(f"**{shop[3]}** by <@{shop[2]}>\n{shop[4]}")
        return shopchannel

    async def productsMess(self, shop_id, num=None):  # Display products in the shop channel
        shop = self.db.getShop(shop_id=shop_id)
        channel = self.get_channel(shop[5])
        products = self.db.getOffers(shop_id)
        if num is None: num = slice(0, len(products), 1)
        print(num)
        for product in products[num]:

            rep = discord.Embed(title=f"__**{product[3]}**__", color=0x5f00ff)
            rep.set_image(url=str(product[5]))
            rep.add_field(name=f"**Desc : **", value=f"{product[4]}", inline=False)
            rep.add_field(name=f"**Price : **", value=f"__{product[2]} €__", inline=True)

            try:
                rep = await channel.send(embed=rep)
                await rep.add_reaction("🪙")
            except:
                rep.set_image(url=EmptyEmbed)
                rep = await channel.send(embed=rep)
                await rep.add_reaction("🪙")
                dl = await channel.send(f"image of {product[3]} is not available")
                await asyncio.sleep(15)
                await dl.delete()


bot = MyClient(command_prefix="$")

"""
SHOP PANEL/OPTIONS
"""


class SelectOffer(discord.ui.Select):
    def __init__(self, offers,custom_id):
        super().__init__(
            placeholder='MENU',
            min_values=1,
            max_values=1,
            custom_id=custom_id,
            options=[
                discord.SelectOption(label=offer["name"], value=offer['id']) for offer in offers
            ]
        )

    async def callback(self, inter:discord.MessageInteraction):

        if bot.followup[inter.custom_id]:
            info = bot.followup[inter.custom_id]
        offer = database.getOffer(self.values[0])
        info["offer"] = offer
        await inter.response.send_modal(OfferModal(title="Edit your offer",custom_id=inter.custom_id,o_title=offer["name"],description=offer["description"],price=offer["price"],imageUrl=offer["imageUrl"]))
        print(offer)

class SelectOfferView(discord.ui.View):

    def __init__(self,offers,custom_id, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(
                SelectOffer(offers,custom_id=custom_id)
        )


async def refresh(guild_id,channel_id):
    shop = database.getShopByChannel(guild_id, channel_id)

    offers = database.getOffers(shop["id"])
    channel: discord.TextChannel = await bot.fetch_channel(shop["channel_id"])

    await channel.purge(limit=240)

    for offer in offers:
        await create_offer_messsage(offer, shop)




class ShopExistView(discord.ui.View):
    def __init__(self,shop_id) -> None:
        super().__init__()
        self.shop_id = shop_id
        self.offers = database.getOffers(self.shop_id)

    @discord.ui.button(label="Add a product!", style=discord.ButtonStyle.primary, emoji="🛒")
    async def button_add_offer(self, button, interaction):
        bot.add_followup(key=interaction.custom_id,type="add offer",shop_id=self.shop_id)
        await interaction.response.send_modal(OfferModal(title="Offer info",custom_id=interaction.custom_id))
        await asyncio.sleep(300)
        if bot.followup.get(interaction.custom_id):
            bot.followup.pop(interaction.custom_id)

    @discord.ui.button(label="Edit a product!", style=discord.ButtonStyle.primary, emoji="✏️")
    async def button_edit_offer(self, button, interaction:Interaction):
        bot.add_followup(key=interaction.custom_id,shop_id=self.shop_id,type="edit offer")
        await interaction.response.send_message("Select the offer you want to modify",view=SelectOfferView(offers=self.offers,custom_id=interaction.custom_id))
        await interaction.message.delete()


    @discord.ui.button(label="Edit Shop!", style=discord.ButtonStyle.primary, emoji="⚙️")
    async def button_shop_settings(self, button, interaction):
        channel_id = interaction.channel_id
        guildId = interaction.guild_id
        if bot.shop[str(guildId) + ":" + str(channel_id)]:
            shop_data = bot.shop[str(guildId) + ":" + str(channel_id)]
        else:
            shop_data = bot.db.getShopByChannel(str(guildId), str(channel_id))
        bot.add_followup(key=interaction.custom_id,type="edit shop",shop_id=shop_data["id"],shop_data=shop_data)
        rep = discord.Embed(title=shop_data["name"], description=shop_data["description"], color=0x5f00ff)
        await interaction.response.edit_message(embed=rep,view=ShopSettingsView())

    @discord.ui.button(label="Refresh the shop!", style=discord.ButtonStyle.gray, emoji="♻️")
    async def button_refresh_shop(self, button, interaction: Interaction):
        await interaction.response.send_message("This shop is beeing refreshed")
        await interaction.delete_original_response(delay=5)
        await refresh(guild_id=interaction.guild_id,channel_id=interaction.channel_id)

class ShopNotExistView(discord.ui.View):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @discord.ui.button(label="Create Shop!", style=discord.ButtonStyle.green, emoji="🛒")
    async def button_add_product(self, button, interaction):
        await interaction.response.edit_message(view=CreateShopView())

    @discord.ui.button(label="Select another shop!", style=discord.ButtonStyle.gray, emoji="📋")
    async def button_select_shop(self, button, interaction):
        print("Another Shop")
class ShopSettingsView(discord.ui.View):
    @discord.ui.button(label="Edit shop informations!", style=discord.ButtonStyle.primary, emoji="✏️")
    async def button_edit(self, button, interaction):
        interaction.response.send_modal(modal=ShopModal(name="",description=""))
    @discord.ui.button(label="Delete shop", style=discord.ButtonStyle.danger,emoji="🗑️")
    async def button_delete(self,button,interaction):
        pass
@bot.slash_command()
async def shop(ctx):
    """
    SHOW THE SHOP PANEL
    """
    channel_id = ctx.channel_id
    guildId = ctx.guild_id
    if bot.shop.get(str(guildId) + ":" + str(channel_id)):
        shop_data = bot.shop[str(guildId) + ":" + str(channel_id)]
    else:
        shop_data = bot.db.getShopByChannel(guildId,channel_id)
    if shop_data:

        rep = discord.Embed(title=shop_data.name, description=shop_data.description, color=0x5f00ff)
        rep.add_field(name="Add a product", value="🛒: ", inline=True)
        rep.add_field(name="Modify", value="⚙: modify a shop\n 📜: modify a product", inline=False)
        await ctx.respond(embed=rep, view=ShopExistView(shop_data.id))

        if not bot.shop.get(str(guildId) + ":" + str(channel_id)):
            bot.shop[str(guildId) + ":" + str(channel_id)] =shop_data
            await asyncio.sleep(120)
            bot.shop.pop(str(guildId) + ":" + str(channel_id))
    else:
        rep = discord.Embed(title="ShopiCord", description="Sell on discord", color=0x5f00ff)
        rep.add_field(name="Info", value="There is no shop in this channel", inline=True)
        await ctx.respond(embed=rep, view=ShopNotExistView())


"""
CREATING a SHOP
"""
#shop message
def createOfferMessage(offer):
    #shop=#getShop
    channelId = shop.channelId

    pass

#shop form
class ShopModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(InputText(label="title",required=True,placeholder="The title of your shop"))
        self.add_item(InputText(label="description", required=True,placeholder="The description of your shop"))

    async def callback(self, interaction: discord.Interaction):

        print(interaction.custom_id)
        data = bot.followup[interaction.custom_id]
        print(data.keys())
        guild = interaction.guild_id
        print(guild)
        user = interaction.user.id
        channel = data["channel_id"]
        name = self.children[0].value
        description = self.children[1].value
        embed = discord.Embed(title="Modal Results")
        embed.add_field(name="guild", value=guild)
        embed.add_field(name="user", value=user)
        embed.add_field(name="channel", value=channel.name)
        embed.add_field(name="name", value=name)
        embed.add_field(name="description", value=description)

        database.addShop(guild,user,name,description,channel.id)
        await interaction.response.edit_message(embeds=[embed])

#getting channel
class CreateShopView(discord.ui.View):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
    @discord.ui.channel_select(
        placeholder="test",
        channel_types=[discord.ChannelType.text]
    )
    async def callback(self,select,interaction: discord.Interaction):
        mod = ShopModal(title="Shop info",custom_id=interaction.custom_id)
        bot.followup[interaction.custom_id] = {"channel_id":select.values[0]}
        rep = await interaction.response.send_modal(mod)
        print(interaction.custom_id)
        print("submited")

"""
CREATING PRODUCT
"""
class OfferModal(discord.ui.Modal):
    def __init__(self,title,custom_id,o_title="",description="",price="",imageUrl="") -> None:
        super().__init__(title=title,custom_id=custom_id)
        self.add_item(InputText(label="title",required=True,placeholder="The title of your Offer",value=o_title))
        self.add_item(InputText(label="description", required=True,placeholder="The description of your Offer",value=description))
        self.add_item(InputText(label="price",required=True,style=InputTextStyle.short, placeholder="The price of your Offer in USD",value=price))
        self.add_item(InputText(label="imageUrl",required=False,placeholder="https://yourimage.com/yourimage",value=imageUrl))

    async def callback(self, interaction: discord.Interaction):
        print(interaction.custom_id)
        data = bot.followup[interaction.custom_id]
        print(data)
        shop_id = data["shop_id"]
        name = self.children[0].value
        description = self.children[1].value
        price = self.children[2].value
        imageUrl = self.children[3].value
        embed = discord.Embed(title="Modal Results")
        print(imageUrl)
        embed.add_field(name="price", value=price)
        embed.add_field(name="shop_id", value=shop_id)
        if imageUrl:
            embed.add_field(name="imageUrl", value=imageUrl)
        embed.add_field(name="name", value=name)
        embed.add_field(name="description", value=description)

        if data.get("type") == "edit offer":
            offer = database.editOffer(data["offer"]["id"],price, name, description, imageUrl)
        else:
            offer = database.addOffer(shop_id, price, name, description, imageUrl)
        await interaction.response.edit_message(embeds=[embed])
        await asyncio.sleep(15)
        await interaction.delete_original_response()
        shop = database.getShopByOffer(offer)
        await refresh(guild_id=shop["serverId"],channel_id=shop["channel"])


class OfferMessageView(discord.ui.View):
    def __init__(self,offer) -> None:
        super().__init__()
        self.add_item(discord.ui.Button(label="Buy",style=discord.ButtonStyle.green,url=f"https://senditeverywhere.com/{offer['id']}",  emoji="💲"))

async def create_offer_messsage(offer, shop):

    rep = discord.Embed(title=f"__**{offer['name']}**__", color=0x5f00ff)
    if offer.get("url"):
        rep.set_image(url=str(offer["url"]))
    rep.add_field(name=f"**Desc : **", value=f"{offer['description']}", inline=False)
    rep.add_field(name=f"**Price : **", value=f"__{offer['price']} €__", inline=True)
    channel = await bot.fetch_channel(shop["channel_id"])
    message = await channel.send(embed=rep,view=OfferMessageView(offer))


bot.run(TOKEN)
