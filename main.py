import asyncio


import discord
from discord import InputTextStyle

from discord.embeds import EmptyEmbed
from discord.ext import commands
from discord.ui import InputText

from dotenv import load_dotenv


from utility.database import Database


load_dotenv()
import os

TOKEN=os.environ.get("TOKEN")
apikey = os.environ.get("DATABASE_API")
database = Database(apikey=apikey)



# noinspection PyBroadException
class MyClient(commands.Bot):
    def __init__(self,command_prefix) -> None:
        self.bot = super().__init__(command_prefix=command_prefix)
        self.db = database
        self.prefix = ";"
        self.followup = {}
        self.react = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

        self.shop = {}
        self.product = []
        # self.shop=[{"current":158,"NAME":None,"DESC":None,"AUTHOR":""},]
        # self.shop = {"messageid":{"precede":self.shop["messageid"],"content":"str","TYPE":"NAME"}}






    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def getCategories(self, guildid):
        guild = await self.fetch_guild(guildid)
        print(guild.categories)

    async def shopChannel(self, shopid):
        print(shopid)
        shop = self.db.getShop(shopid=shopid)
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

    async def productsMess(self, shopid, num=None):  # Display products in the shop channel
        shop = self.db.getShop(shopid=shopid)
        channel = self.get_channel(shop[5])
        products = self.db.getOffers(shopid)
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

#"""
#ADMIN PANEL/OPTIONS
#"""
#class AdminView(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
#    @discord.ui.button(label="Click me!", style=discord.ButtonStyle.primary, emoji="🛒")
#    async def button_destruct(self,button,interaction):
#        await interaction.response.edit_message(content="select the channel", view=CreateShopView())
#
#    @discord.ui.button(label="Click me!", style=discord.ButtonStyle.primary, emoji="📦")
#    async def button_userShop(self,button,interaction):
#        await bot.UserShops(interaction.message.reference.cached_message, "PRODUCTCREATE")
#    # await reaction.message.channel.send("you want to create a product")
#
#
#    @discord.ui.button(label="Click me!", style=discord.ButtonStyle.primary, emoji="⚙")
#    async def button_settings(self,button,interaction):
#
#        await bot.UserShops(interaction.message.reference.cached_message, "UPDATE")
#
#    @discord.ui.button(label="Click me!", style=discord.ButtonStyle.primary, emoji="📜")
#    async def button_settings(self, button, interaction):
#        await self.UserShops(interaction.message.reference.cached_message, "UPDATES")
#        pass
#
#    @discord.ui.button(label="Click me!", style=discord.ButtonStyle.primary, emoji="♻️")
#    async def button_settings(self, button, interaction):
#        await self.UserShops(interaction.message.reference.cached_message, "DEBUG")
#@bot.slash_command()
#async def admin(ctx):
#    """
#    SHOW THE ADMIN PANEL
#    """
#    rep = discord.Embed(title="Your admin panel", description="Desc", color=0x5f00ff)
#    rep.add_field(name="Create", value="🛒: create a new shop\n 📦: create a new product", inline=True)
#    rep.add_field(name="Modify", value="⚙: modify a shop\n 📜: modify a product", inline=False)
#    rep = await ctx.respond(embed=rep,view=AdminView())
#    await asyncio.sleep(300)
#    bot.messages.pop(rep.id)
#
#    await ctx.delete_original_response()





"""
SHOP PANEL/OPTIONS
"""
class ShopExistView(discord.ui.View):
    def __init__(self,shopId=None) -> None:
        super().__init__()
        self.shopId = shopId

    @discord.ui.button(label="Add a product!", style=discord.ButtonStyle.primary, emoji="🛒")
    async def button_add_product(self, button, interaction):
        bot.followup[interaction.custom_id] = {"shopId":self.shopId}
        await interaction.response.send_modal(OfferModal(title="Offer info",custom_id=interaction.custom_id))
        await asyncio.sleep(300)
        if bot.followup.get(interaction.custom_id):
            bot.followup.pop(interaction.custom_id)


    @discord.ui.button(label="Go to Settings!", style=discord.ButtonStyle.primary, emoji="⚙️")
    async def button_shop_settings(self, button, interaction):
        channelId = interaction.channel_id
        guildId = interaction.guild_id
        if bot.shop[str(guildId) + ":" + str(channelId)]:
            shop_data = bot.shop[str(guildId) + ":" + str(channelId)]
        else:
            shop_data = bot.db.getShopByChannel(str(guildId), str(channelId))
        rep = discord.Embed(title=shop_data["name"], description=shop_data["description"], color=0x5f00ff)
        await interaction.response.edit_message(embed=rep,view=ShopSettingsView())
class ShopNotExistView(discord.ui.View):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @discord.ui.button(label="Create Shop!", style=discord.ButtonStyle.green, emoji="🛒")
    async def button_add_product(self, button, interaction):
        await interaction.response.edit_message("test", view=CreateShopView())

    @discord.ui.button(label="Select another shop!", style=discord.ButtonStyle.gray, emoji="📋")
    async def button_select_shop(self, button, interaction):
        print("Another Shop")
class ShopSettingsView(discord.ui.View):
    @discord.ui.button(label="Edit shop informations!", style=discord.ButtonStyle.primary, emoji="✏️")
    async def button_edit(self, button, interaction):
        pass
    @discord.ui.button(label="Delete shop", style=discord.ButtonStyle.danger,emoji="🗑️")
    async def button_delete(self,button,interaction):
        pass
@bot.slash_command()
async def shop(ctx):
    """
    SHOW THE SHOP PANEL
    """
    channelId = ctx.channel_id
    guildId = ctx.guild_id
    if bot.shop.get(str(guildId) + ":" + str(channelId)):
        shop_data = bot.shop[str(guildId) + ":" + str(channelId)]
    else:
        shop_data = bot.db.getShopByChannel(guildId,channelId)
    if shop_data:

        rep = discord.Embed(title=shop_data["name"], description=shop_data["description"], color=0x5f00ff)
        rep.add_field(name="Add a product", value="🛒: ", inline=True)
        rep.add_field(name="Modify", value="⚙: modify a shop\n 📜: modify a product", inline=False)
        await ctx.respond(embed=rep, view=ShopExistView(shop_data["$id"]))

        if not bot.shop.get(str(guildId) + ":" + str(channelId)):
            bot.shop[str(guildId) + ":" + str(channelId)] =shop_data
            await asyncio.sleep(120)
            bot.shop.pop(str(guildId) + ":" + str(channelId))
    else:
        rep = discord.Embed(title="ShopiCord", description="Sell on discord", color=0x5f00ff)
        rep.add_field(name="Info", value="There is no shop in this channel", inline=True)
        await ctx.respond(embed=rep, view=ShopNotExistView())


"""
CREATING a SHOP
"""
class ShopModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(InputText(label="title",required=True,placeholder="The title of your shop"))
        self.add_item(InputText(label="description", required=True,placeholder="The description of your shop"))

    async def callback(self, interaction: discord.Interaction):
        print(interaction.custom_id)
        data = bot.followup[interaction.custom_id]
        print(data)
        guild = interaction.guild_id
        print(guild)
        user = interaction.user.id
        channel = data["channel"]
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
class CreateShopView(discord.ui.View):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
    @discord.ui.channel_select(
        placeholder="test",
        channel_types=[discord.ChannelType.text]
    )
    async def callback(self,select,interaction: discord.Interaction):
        mod = ShopModal(title="Shop info",custom_id=interaction.custom_id)
        bot.followup[interaction.custom_id] = {"channel":select.values[0]}
        rep = await interaction.response.send_modal(mod)
        print(interaction.custom_id)
        print("submited")

"""
CREATING PRODUCT
"""
class OfferModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(InputText(label="title",required=True,placeholder="The title of your Offer"))
        self.add_item(InputText(label="description", required=True,placeholder="The description of your Offer"))
        self.add_item(InputText(label="price",required=True,style=InputTextStyle.short, placeholder="The price of your Offer in USD"))
        self.add_item(InputText(label="imageUrl",required=False,placeholder="https://yourimage.com/yourimage"))

    async def callback(self, interaction: discord.Interaction):
        print(interaction.custom_id)
        data = bot.followup[interaction.custom_id]
        print(data)
        shopId = data["shopId"]
        name = self.children[0].value
        description = self.children[1].value
        price = self.children[2].value
        imageUrl = self.children[3].value
        embed = discord.Embed(title="Modal Results")
        embed.add_field(name="price", value=price)
        embed.add_field(name="shopId", value=shopId)
        embed.add_field(name="imageUrl", value=imageUrl)
        embed.add_field(name="name", value=name)
        embed.add_field(name="description", value=description)

        database.addOffer(shopId, price, name, description, imageUrl)
        await interaction.response.edit_message(embeds=[embed])
        await asyncio.sleep(4)
        await interaction.delete_original_response()






bot.run(TOKEN)
