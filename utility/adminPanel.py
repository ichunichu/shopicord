import asyncio

import discord

from main import bot



import discord
from discord.ui import InputText
from discord import default_permissions

from main import bot, database


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



class AdminView(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
    @discord.ui.button(label="Click me!", style=discord.ButtonStyle.primary, emoji="🛒")
    async def button_destruct(self,button,interaction):
        await interaction.response.edit_message(content="select the channel", view=CreateShopView())

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
    rep = discord.Embed(title="Your admin panel", description="Desc", color=0x5f00ff)
    rep.add_field(name="Create", value="🛒: create a new shop\n 📦: create a new product", inline=True)
    rep.add_field(name="Modify", value="⚙: modify a shop\n 📜: modify a product", inline=False)
    rep = await ctx.respond(embed=rep,view=AdminView())
    await asyncio.sleep(300)
    bot.messages.pop(rep.id)

    await ctx.delete_original_response()