
class ShopExistView(discord.ui.View):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @discord.ui.button(label="Add a product!", style=discord.ButtonStyle.primary, emoji="🛒")
    async def button_add_product(self, button, interaction):
        print("add product")

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

class ShopSettingsView(discord.ui.View):
    @discord.ui.button(label="Edit shop informations!", style=discord.ButtonStyle.primary, emoji="✏️")
    async def button_edit(self, button, interaction):
        pass
    @discord.ui.button(label="Delete shop", style=discord.ButtonStyle.danger,emoji="🗑️")
    async def button_delete(self,button,interaction):
        pass
class ShopNotExistView(discord.ui.View):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @discord.ui.button(label="Create Shop!", style=discord.ButtonStyle.green, emoji="🛒")
    async def button_add_product(self, button, interaction):
        await interaction.response.edit_message("test", view=shops.CreateShopView())

    @discord.ui.button(label="Select another shop!", style=discord.ButtonStyle.gray, emoji="📋")
    async def button_select_shop(self, button, interaction):
        print("Another Shop")


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
        await ctx.respond(embed=rep, view=ShopExistView())

        if not bot.shop.get(str(guildId) + ":" + str(channelId)):
            bot.shop[str(guildId) + ":" + str(channelId)] =shop_data
            await asyncio.sleep(120)
            bot.shop.pop(str(guildId) + ":" + str(channelId))
    else:
        rep = discord.Embed(title="ShopiCord", description="Sell on discord", color=0x5f00ff)
        rep.add_field(name="Info", value="There is no shop in this channel", inline=True)
        await ctx.respond(embed=rep, view=ShopNotExistView())