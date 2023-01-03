import asyncio
import discord

from discord.embeds import EmptyEmbed
from discord.ext import commands
from discord.ui import InputText

from dotenv import load_dotenv

from discord import default_permissions

from utility.database import Database

load_dotenv()
import os


def bigDict():
    pass
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

        self.shop = []
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
        await interaction.response.send_message(embeds=[embed])

class ChannelSelectView(discord.ui.View):
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



class AdminView(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
    @discord.ui.button(label="Click me!", style=discord.ButtonStyle.primary, emoji="🛒")
    async def button_destruct(self,button,interaction):
        view = ChannelSelectView()
        await interaction.response.send_message("test",view=view)

    @discord.ui.button(label="Click me!", style=discord.ButtonStyle.primary, emoji="📦")
    async def button_userShop(self,button,interaction):
        await bot.UserShops(interaction.message.reference.cached_message, "PRODUCTCREATE")
    # await reaction.message.channel.send("you want to create a product")


    @discord.ui.button(label="Click me!", style=discord.ButtonStyle.primary, emoji="⚙")
    async def button_settings(self,button,interaction):

        await bot.UserShops(interaction.message.reference.cached_message, "UPDATE")

    @discord.ui.button(label="Click me!", style=discord.ButtonStyle.primary, emoji="📜")
    async def button_settings(self, button, interaction):
        await self.UserShops(interaction.message.reference.cached_message, "UPDATES")
        pass

    @discord.ui.button(label="Click me!", style=discord.ButtonStyle.primary, emoji="♻️")
    async def button_settings(self, button, interaction):
        await self.UserShops(interaction.message.reference.cached_message, "DEBUG")



@bot.slash_command()
async def admin(ctx):
    """
    SHOW THE ADMIN PANEL
    """
    #print(f'{ctx.author} asked for the adminpanel on {ctx.guild.id}')
    rep = discord.Embed(title="Your admin panel", description="Desc", color=0x5f00ff)
    rep.add_field(name="Create", value="🛒: create a new shop\n 📦: create a new product", inline=True)
    rep.add_field(name="Modify", value="⚙: modify a shop\n 📜: modify a product", inline=False)
    # await message.channel.send(rep)
    rep = await ctx.respond(embed=rep,view=AdminView())
    await asyncio.sleep(300)
    bot.messages.pop(rep.id)

    await ctx.delete_original_response()

TOKEN=os.environ.get("TOKEN")


bot.run(TOKEN)


