
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

