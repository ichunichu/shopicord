import asyncio
import discord

from discord.embeds import EmptyEmbed
from dotenv import load_dotenv

from utility.database import Database

load_dotenv()
import os


def bigDict():
    pass





# noinspection PyBroadException
class MyClient(discord.Client):
    def __init__(self) -> None:
        super().__init__()
        self.db = Database()
        self.prefix = ";"
        self.messages = {}
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

    async def createProduct(self, dico):
        shop = self.db.numToShop(dico["AUTHOR"], dico["CURRENT"].guild.id, dico["SHOPNUM"])
        shopid = shop[0]
        price = dico["PRICE"]
        name = dico["NAME"]
        description = dico["DESC"]
        image = dico["IMGURL"]
        self.db.addProduct(shopid, price, name, description, image)
        # shop = self.db.getShops(dico["AUTHOR"],dico["CURRENT"].guild.id)
        await self.productsMess(shopid, slice(len(shop), len(shop) + 1))

    async def admin(self, message):
        """
        SHOW THE ADMIN PANEL
        """
        print(f'{message.author} asked for the adminpanel {message.content} on {message.guild.id}')
        rep = discord.Embed(title="Your admin panel", description="Desc", color=0x5f00ff)
        rep.add_field(name="Create", value="🛒: create a new shop\n 📦: create a new product", inline=True)
        rep.add_field(name="Modify", value="⚙: modify a shop\n 📜: modify a product", inline=False)
        # await message.channel.send(rep)
        rep = await message.reply(embed=rep)
        self.messages[rep.id] = {"OBJECT": message, "response": rep, "TYPE": "ADMIN"}
        await rep.add_reaction('🛒')
        await rep.add_reaction('📦')
        await rep.add_reaction('⚙')
        await rep.add_reaction('📜')
        await rep.add_reaction('♻️')
        await asyncio.sleep(300)

        self.messages.pop(rep.id)
        await message.delete()
        await rep.delete()

    async def adminReact(self, reaction):
        """
        INTERPRETE REACTION OF THE ADMIN PANEL
        """
        match reaction.emoji:
            case "🛒":
                # try:
                #    self.db.checkServer(reaction.message.guild.id)
                # except:
                #    reaction.emoji = reaction.message.channel.send("Exception with the database, please try again")
                rep = await reaction.message.channel.send("**REPLY** with the name of your shop")
                await rep.add_reaction('❌')
                self.shop.append({"CURRENT": rep, "NAME": None, "DESC": None,
                                  "AUTHOR": reaction.message.reference.cached_message.author})
            case "📦":
                await self.UserShops(reaction.message.reference.cached_message, "PRODUCTCREATE")
                # await reaction.message.channel.send("you want to create a product")
            case "⚙":
                await self.UserShops(reaction.message.reference.cached_message,"UPDATE")
            case "📜":
                await self.UserShops(reaction.message.reference.cached_message,"UPDATES")
            case "♻️":
                await self.UserShops(reaction.message.reference.cached_message, "DEBUG")




    async def UserShops(self, message,func=""):  # Display the shops of the user (same panel for modify shop and debug and add new products)
        shops = self.db.getShops(message.author.id, message.guild.id)
        rep=0
        if func[0:5] == "UPDATE":
            rep = discord.Embed(title=f"You have {len(shops)} Shops",
                                description="Cliquer pour actualiser votre channel", color=0x5f00ff)
        elif func == "UPDATES":
            rep = discord.Embed(title=f"You have {len(shops)} Shops",
                                description="Dans quel shop ce trouve l'offre a modifier ?", color=0x5f00ff)
        elif func == "PRODUCTCREATE":
            rep = discord.Embed(title=f"You have {len(shops)} Shops",
                                description="Click on a shop to add a new product", color=0x5f00ff)
        elif func == "DEBUG":
            rep = discord.Embed(title=f"You have {len(shops)} Shops",
                                description="Click on a shop to add a new product", color=0x5f00ff)
        for i in range(len(shops)):
            rep.add_field(name=f"**{shops[i][3]}**", value=f"{shops[i][4]}\n {self.react[i]}: Update this shop",
                          inline=True)

        # await message.channel.send(rep)
        rep = await message.reply(embed=rep)

        if func == "UPDATE":

            self.product.append(
                {"CURRENT": rep, "NAME": None, "DESC": None,"AUTHOR": message.author.id,"FUNC":"UPDATE"})
        elif func == "UPDATES":

            self.product.append(
                {"CURRENT": rep, "NAME": None, "DESC": None,"AUTHOR": message.author.id,"FUNC":"UPDATES"})
        else:
            self.product.append(
                {"CURRENT": rep, "AUTHOR": message.author.id, "SHOPNUM": None, "NAME": None, "PRICE": None,
                 "DESC": None, "IMGURL": None, "FUNC": func})
        for i in range(len(shops)):
            await rep.add_reaction(self.react[i])
        # self.messages[rep.id] = {"OBJECT":message,"response":rep,"TYPE":"ADMIN"}

    async def debugMess(self, shopid):  # purge channel and rewrite all messages
        shop = self.db.getShop(shopid=shopid)
        channel = self.get_channel(shop[5])
        print(channel)
        try:
            await channel.purge()
            await channel.send()
            await channel.send(f"**{shop[3]}** by <@{shop[2]}>\n{shop[4]}")
        except:
            await self.shopChannel(shopid)
        await self.productsMess(shopid)

    async def on_message(self, message):
        # await self.shopChannel(702593985776058569,12)
        if message.content[0:len(self.prefix)] == self.prefix:  # message avec prefix
            message.content = message.content[len(self.prefix):].split(" ")
            if message.content[0].upper() == "ADMIN":
                await self.admin(message)
            elif message.content[0].upper() == "SHOP":
                await self.UserShops(message)
            elif message.content[0].upper() == "HELP":
                await self.UserShops(message)

        if message.reference is not None:  # message en .reply
            for i in range(len(self.shop)):  # for the shops
                if message.reference.message_id == self.shop[i]["CURRENT"].id:
                    if self.shop[i]["NAME"] is None:
                        self.shop[i]["NAME"] = message.content
                        self.shop[i]["CURRENT"] == message
                        rep = await message.channel.send("**REPLY** with the description of your shop")
                        if "OLD" in self.shop[i].keys():
                            await rep.add_reaction("⏭️")
                        else:
                            await rep.add_reaction("❌")
                        await self.shop[i]["CURRENT"].delete()
                        self.shop[i]["CURRENT"] = rep
                    elif self.shop[i]["DESC"] is None:
                        if message.content != "NONE":
                            await self.shop[i]["CURRENT"].delete()
                            self.shop[i]["DESC"] = message.content
                        if "OLD" in self.shop[i].keys():
                            #print(self.shop[i]["AUTHOR"])
                            #print(self.shop[i]["CURRENT"].guild.id)
                            #print(self.shop[i]["NUM"])
                            #print(self.shop[i]["NAME"])
                            #print(self.shop[i]["DESC"])
                            try:

                                self.db.updateShop(self.shop[i]["AUTHOR"],self.shop[i]["CURRENT"].guild.id,self.shop[i]["NUM"],self.shop[i]["NAME"],self.shop[i]["DESC"])
                                await message.channel.send("**The Shop has been updated.")
                                print("UPDATER")
                            except:
                                print("excepted")
                                #print(shopid)
                                #if shopid != 0:
                                #    await self.shopChannel(shopid)

                        else:

                            try:
                                shopid = self.db.addShop(message.guild.id, self.shop[i]["AUTHOR"].id, self.shop[i]["NAME"],
                                                         self.shop[i]["DESC"])
                                await message.channel.send("Your shop has been created")
                            except:
                                shopid = 0
                                await message.channel.send(
                                    "**ERROR**: The Database is not accessible. Please try again later. If the probleme is not resolved, please contact the support (;support)")
                            print(shopid)
                            if shopid != 0:
                                await self.shopChannel(shopid)
                    await message.delete()

            for i in range(len(self.product)):  # for the products
                if message.reference.message_id == self.product[i]["CURRENT"].id:
                    if self.product[i]["AUTHOR"] == message.author.id:
                        if self.product[i]["NAME"] is None:
                            self.product[i]["NAME"] = message.content
                            await self.product[i]["CURRENT"].delete()
                            rep = await message.channel.send("**REPLY** with the price of the product")
                            self.product[i]["CURRENT"] = rep
                            await rep.add_reaction("❌")
                        elif self.product[i]["PRICE"] is None:
                            try:
                                self.product[i]["PRICE"] = float(message.content)
                                await self.product[i]["CURRENT"].delete()
                                rep = await message.channel.send("**REPLY** with the description of the product")
                                self.product[i]["CURRENT"] = rep
                                await rep.add_reaction("❌")
                            except:
                                await self.product[i]["CURRENT"].delete()
                                rep = await message.channel.send(
                                    "**REPLY** with the price of the product (number only)")
                                self.product[i]["CURRENT"] = rep
                                await rep.add_reaction("❌")
                        elif self.product[i]["DESC"] is None:
                            self.product[i]["DESC"] = message.content
                            rep = await message.channel.send("**REPLY** with the image url for the product")
                            await rep.add_reaction("⏭️")
                            await rep.add_reaction("❌")
                            await self.product[i]["CURRENT"].delete()
                            self.product[i]["CURRENT"] = rep
                        elif self.product[i]["IMGURL"] is None:
                            if "http" in message.content or "https" in message.content:
                                self.product[i]["IMGURL"] = message.content
                                # print(self.product[i])
                                await self.createProduct(self.product[i])
                                await self.product[i]["CURRENT"].delete()
                                await message.channel.send("Your product is good")
                            else:
                                rep = await message.channel.send(
                                    "**REPLY** with the image url for the product (start with http(s))")
                                await self.product[i]["CURRENT"].delete()
                                self.product[i]["CURRENT"] = rep
                                await rep.add_reaction("⏭️")
                                await rep.add_reaction("❌")

                    await message.delete()

        # await self.cleanUp()

    async def on_reaction_add(self, reaction, user):
        if reaction.emoji == "⏭️":
            for shop in self.shop:
                #print(self.shop)
                if reaction.message.id == shop["CURRENT"].id:
                    async for user in reaction.users():
                        if shop["AUTHOR"] == user.id:
                            print("k")
                            #for j in self.shop:
                            print(reaction.message.id ,shop["CURRENT"].id)
                            if reaction.message.id == shop["CURRENT"].id:
                                print('K')
                                if "OLD" in shop.keys():
                                    print('K')
                                    if shop["NAME"] is None:
                                        shop["NAME"] = shop["OLD"][3]
                                        rep = await reaction.message.channel.send("**REPLY** with the description of your shop")
                                        await rep.add_reaction("⏭️")
                                        shop["CURRENT"] = rep
                                    elif shop["DESC"] is None:
                                        shop["DESC"] = shop["OLD"][4]
                                        self.db.updateShop(shop["AUTHOR"],shop["CURRENT"].guild.id,shop["NUM"],shop["NAME"],shop["DESC"])
                                        await reaction.message.channel.send("**The Shop has been updated.")
                                        await reaction.message.delete()
                                        #print("SHOP UPDATER",shop)


        if user.id != self.user.id:
            if reaction.message.id in self.messages:

                if self.messages[reaction.message.id]["OBJECT"].author == user:
                    if self.messages[reaction.message.id]["TYPE"] == "ADMIN":
                        await self.adminReact(reaction)
                    # print(self.messages[reaction.message.id]["TYPE"])
            else:
                for i in range(len(self.product)):
                    if self.product[i]["CURRENT"] == reaction.message:
                        if self.product[i]["FUNC"] == "UPDATE":
                            for j in self.react:
                                if j == reaction.emoji:
                                    rep = await reaction.message.channel.send("**REPLY** with the name of your shop or click on ⏭️ to skip")
                                    await rep.add_reaction("⏭️")
                                    self.shop.append({"CURRENT": rep, "NAME": None, "DESC": None,
                                                                       "AUTHOR": self.product[i]["AUTHOR"],
                                                                       "OLD": self.db.numToShop(
                                                                           self.product[i]["AUTHOR"],
                                                                           self.product[i]["CURRENT"].guild.id,
                                                                           self.react.index(j)),"NUM":self.react.index(j)})

                        elif self.product[i]["FUNC"] == "UPDATES":
                            shop = self.db.numToShop(self.product[i]["AUTHOR"],self.product[i]["CURRENT"].guild.id,self.react.index(reaction.emoji))
                            shopid = shop[0]
                            offers = self.db.getOffers(shopid)
                            rep = discord.Embed(title=f"You have {len(offers)} offers",
                                                description="Click on a shop to add a new product", color=0x5f00ff)
                            print(offers)
                            for offer in range(len(offers)):
                                print(offer)
                                rep.add_field(name=f"**{offers[offer][3]}**",
                                              value=f"{offers[offer][4]}\n {self.react[offer]}: Update this shop",
                                              inline=True)
                            rep =await self.product[i]["CURRENT"].channel.send(embed=rep)
                            for j in range(len(offers)):
                                await rep.add_reaction(self.react[j])

                        elif self.product[i]["FUNC"] == "PRODUCTCREATE":
                            for j in self.react:
                                if j == reaction.emoji:
                                    rep = await reaction.message.channel.send("**REPLY** with the product name:")
                                    await self.product[i]["CURRENT"].delete()
                                    await rep.add_reaction("❌")
                                    self.product[i]["CURRENT"] = rep
                                    self.product[i]["SHOPNUM"] = self.react.index(j)
                                    # print(self.product[i])
                            if reaction.emoji == "⏭️":
                                await self.createProduct(self.product[i])
                                await self.product[i]["CURRENT"].channel.send("Your product is good")
                                await self.product[i]["CURRENT"].delete()
                                self.product.pop(i)
                        elif self.product[i]["FUNC"] == "DEBUG":
                            for j in self.react:
                                if j == reaction.emoji:
                                    self.product[i]["SHOPNUM"] = self.react.index(j)
                                    # print(self.product[i])
                                    shop = self.db.numToShop(self.product[i]["AUTHOR"],
                                                             self.product[i]["CURRENT"].guild.id,
                                                             self.product[i]["SHOPNUM"])
                                    await self.debugMess(shop[0])
                                    # print("DONE")
                if reaction.emoji == "❌":
                    for i in range(len(self.shop)):
                        if reaction.message == self.shop[i]["CURRENT"]:
                            async for author in reaction.users():
                                if author.id == self.shop[i]["AUTHOR"].id:
                                    await self.shop[i]["CURRENT"].delete()
                                    self.shop.pop(i)

                    # if self.shop[reaction.message.id]["TYPE"] == "ASKNAME":
                    #    if reaction.emoji == "❌":
                    #        await reaction.message.delete()
                    #        self.messages.pop(reaction.message.id)
                    #    print("gdfigfdhugfehi")
TOKEN=os.environ.get("TOKEN")

client = MyClient()
client.run(TOKEN)
