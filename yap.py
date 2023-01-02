import asyncio
import sqlite3

import discord
import time

from discord import guild
def bigDict():
    
        pass

class Database:
    def __init__(self):
        self.con = sqlite3.connect('discord.db',isolation_level=None)
        self.cur = self.con.cursor()
        

    async def addServer(self, serverId):
        await self.cur.execute(f'INSERT INTO "main"."Servers"("id") VALUES ({serverId});')

    
    def checkServer(self, serverId):
        self.cur.execute(f'select count(*) from Servers WHERE id = {serverId};')
        if self.cur.fetchone()[0] == 1:
            #self.con.close()
            return(True)
        elif self.addServer(serverId) == True:
            #self.con.close()
            return(True)
        return(False)
        

    
    def addShop(self, serverId,shopOwner,Name="",Description=""):
        print(serverId, shopOwner, Name, Description)
        self.cur.execute(f'INSERT INTO "main"."Shops"("ServerId", "ShopOwner", "Name", "Description")VALUES ({serverId}, "{shopOwner}", "{Name}", "{Description}") returning ServerId;')

        
        return(True)

    def addProduct(self,shopid,price,name,description,IMGURL):
        try:
            #print(f'INSERT INTO "main"."Offers"("ShopId", "Price", "Name", "Desc", "ImageUrl")VALUES ({shopid}, {price}, "{name}", "{description}", "{IMGURL}");')
            self.cur.execute(f'INSERT INTO "main"."Offers"("ShopId", "Price", "Name", "Desc", "ImageUrl")VALUES ({shopid}, {price}, "{name}", "{description}", "{IMGURL}");')
            return(True)
        except:
            return(False)
    def getShops(self,shopOwner,guildid):
        mystr = f'SELECT * FROM "main"."Shops" WHERE ShopOwner = "{shopOwner}" and ServerId = {guildid};'
        self.cur.execute(mystr)
        res = self.cur.fetchall()
        print("SHOPS" , res, mystr)
        #SELECT * FROM "main"."Shops" WHERE ShopOwner = "697888128043581511" and ServerId = 702593985776058569;
        #SELECT * FROM "main"."Shops" WHERE ShopOwner = "697888128043581511" and ServerId = 697888128043581511;
        #697888128043581511 715134352102653972
        return(res)
    def getOffers(self,shopid):
        mystr = f'SELECT * FROM "main"."Offers" WHERE ShopId = "{shopid}";'
        self.cur.execute(mystr)
        res = self.cur.fetchall()
        return(res)
        print("SHOPS" , res, mystr)
        #SELECT * FROM "main"."Shops" WHERE ShopOwner = "697888128043581511" and ServerId = 702593985776058569;
        #SELECT * FROM "main"."Shops" WHERE ShopOwner = "697888128043581511" and ServerId = 697888128043581511;
        #697888128043581511 715134352102653972


    def numToShop(self,shopOwner,guildid,num):
        return(self.getShops(shopOwner,guildid)[num])

    def getShop(self,shopOwner="",shopName="",guildid="",shopid=None):
        if shopid is None:
            self.cur.execute(f'SELECT * FROM "main"."Shops" WHERE ShopOwner= "{shopOwner}" and Name = "{shopName}" and ServerId = "{guildid}";')
            rep = self.cur.fetchone()
        elif type(shopid) == int:
            self.cur.execute(f'SELECT * FROM "main"."Shops" WHERE Shopid = {shopid};')
            rep = self.cur.fetchone()
        return(rep)
    def updateCurrentChannel(self,channelid,shopid):
        mystr = f'UPDATE "main"."Shops" SET "ActualChannel"="{channelid}" WHERE Shopid = "{shopid}"'
        self.cur.execute(mystr)


    def getCategory(self,serverId):
        self.cur.execute(f'SELECT ShopCat FROM "main"."Servers" WHERE id = "{serverId}";')
        self.cur.fetchall()
        self.con.close()
        

        


class MyClient(discord.Client):
    def __init__(self) -> None:
        super().__init__()
        self.db = Database()
        self.prefix = ";"
        self.messages = {}
        self.react = ["0️⃣","1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]

        self.shop = []
        self.product = []
        #self.shop=[{"current":158,"NAME":None,"DESC":None,"AUTHOR":""},]
        #self.shop = {"messageid":{"preced":self.shop["messageid"],"content":"str","type":"NAME"}}
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def getCategories(self,guildid):
        guild = await self.fetch_guild(guildid)
        print(guild.categories)

    async def shopChannel(self,guild,shopid):
        print(guild,shopid)
        shop = self.db.getShop(shopid=shopid)
        #print(shop)
        cat = False
        guild = self.get_guild(guild)
        print(guild)
        print("CATEGORIES", guild.categories)
        for categorie in guild.categories:
            print(categorie.name)
            if categorie.name.upper() == "SHOP":
                cat = categorie
        if cat == False:
            cat = await guild.create_category("Shop")
        for channel in cat.channels:
            if channel.name == shop[3]:
                return(True)
        shopchannel = await cat.create_text_channel(shop[3])
        author = await self.fetch_user(shop[2])
        print("author: ", author)
        await shopchannel.send(f"**{shop[3]}** by <@{author.id}>\n{shop[4]}")
        return(shopchannel)


    async def createProduct(self,dico):
        shop = self.db.numToShop(dico["AUTHOR"],dico["CURRENT"].guild.id,dico["SHOPNUM"])
        print(shop)
        shopid = shop[0]
        price = dico["PRICE"]
        name = dico["NAME"]
        description = dico["DESC"]
        image = dico["IMGURL"]
        print(shopid,price,name,description,image)
        if self.db.addProduct(shopid,price,name,description,image):
            channel = self.get_channel(shop[5])
            await channel.send(f"{name},{description},{image}")

            print("SAVED")



        

    async def admin(self,message):
        """
        SHOW THE ADMIN PANEL
        """
        print(f'{message.author} asked for the adminpanel {message.content} on {message.guild.id}')
        rep = discord.Embed(title="Your admin panel", description="Desc", color=0x5f00ff)
        rep.add_field(name="Create", value="🛒: create a new shop\n 📦: create a new product", inline=True)
        rep.add_field(name="Modify", value="⚙: modify a shop\n 📜: modify a product", inline=False)
        #await message.channel.send(rep)
        rep = await message.reply(embed=rep)
        self.messages[rep.id] = {"object":message,"reponse":rep,"type":"ADMIN"}
        await rep.add_reaction('🛒')
        await rep.add_reaction('📦')
        await rep.add_reaction('⚙')
        await rep.add_reaction('📜')
        await rep.add_reaction('♻️')
        await asyncio.sleep(300)
        
        self.messages.pop(rep.id)
        await message.delete()
        await rep.delete()

    async def adminReact(self,reaction):
        """
        INTERPRETE REACTION OF THE ADMIN PANEL
        """
        print(reaction.emoji)
        if reaction.emoji == "🛒":
            try:
                self.db.checkServer(reaction.message.guild.id)
            except:
                reaction.emoji = reaction.message.channel.send("Exception with the database, please try again")
            rep = await reaction.message.channel.send("**REPLY** with the name of your shop")
            await rep.add_reaction('❌')
            self.shop.append({"CURRENT":rep,"NAME":None,"DESC":None,"AUTHOR":reaction.message.reference.cached_message.author})
            print(self.shop)
        elif reaction.emoji == "📦":
            await self.UserShops(reaction.message.reference.cached_message,"ProductCreate")
            #await reaction.message.channel.send("you want to create a product")
        elif reaction.emoji == "⚙":
            await self.UserShops(reaction.message.reference.cached_message)
        elif reaction.emoji == "📜":
            await reaction.message.channel.send("you want to edit a product")
        elif reaction.emoji == "♻️":
            pass


    async def UserShops(self,message,func=""):
        shops = self.db.getShops(message.author.id,message.guild.id)
        
        if func == "":
            rep = discord.Embed(title=f"You have {len(shops)} Shops", description="Cliquer pour actualiser votre channel", color=0x5f00ff)
        elif func=="ProductCreate":
            rep = discord.Embed(title=f"You have {len(shops)} Shops", description="Click on a shop to add a new product", color=0x5f00ff)
            

        for i in range(len(shops)):
            rep.add_field(name=f"**{shops[i][3]}**", value=f"{shops[i][4]}\n {self.react[i]}: Update this shop", inline=True)
            
        #await message.channel.send(rep)
        rep = await message.reply(embed=rep)
        if func == "":
            pass
        elif func=="ProductCreate":
            self.product.append({"CURRENT":rep,"AUTHOR":message.author.id,"SHOPNUM":None,"NAME":None,"PRICE":None,"DESC":None,"IMGURL":None})
            print(self.product)
        for i in range(len(shops)):
            await rep.add_reaction(self.react[i])
        #self.messages[rep.id] = {"object":message,"reponse":rep,"type":"ADMIN"}
    
    async def productsMess(self,shopid):
        shop =  self.db.getShop(shopid=shopid)
        channel = self.get_channel(shop[5])
        products = self.db.getOffers(shopid)
        for product in products:
            rep = discord.Embed(title=product[3], color=0x5f00ff)
            rep.add_field(name=f"**{product[5]}**", value=f"{product[4]}", inline=True)
            rep.add_field(name=f"**{product[1]}**", value=f"YEET", inline=True)
            
            channel.send(rep)

    async def debugMess(self,shopid):
        shop =  self.db.getShop(shopid=shopid)
        channel = self.get_channel(shop[5])
        while channel.last_message != None:
            channel.last_message.delete()

    async def on_message(self, message):
        #await self.shopChannel(702593985776058569,12)
        if message.content[0:len(self.prefix)] == self.prefix:
            message.content = message.content[len(self.prefix):].split(" ")
            if message.content[0].upper() == "ADMIN":
                await self.admin(message)
            elif message.content[0].upper() == "SHOP":
                await self.UserShops(message)
            elif message.content[0].upper() == "HELP":
                await self.UserShops(message)
        if message.reference != None:
            
            for i in range(len(self.shop)): #for the shop creation
                if message.reference.message_id == self.shop[i]["CURRENT"].id:
                    if self.shop[i]["NAME"] == None:
                        self.shop[i]["NAME"] = message.content
                        self.shop[i]["CURRENT"] == message
                        print(self.shop[i])
                        rep = await message.channel.send("**REPLY** with the description of your shop")
                        await rep.add_reaction("❌")
                        self.shop[i]["CURRENT"] = rep
                    elif self.shop[i]["DESC"] == None:
                        if message.content != "NONE":
                            self.shop[i]["DESC"] = message.content
                        self.db.addShop(message.guild.id,self.shop[i]["AUTHOR"].id,self.shop[i]["NAME"],self.shop[i]["DESC"])
                        
                        
                        await message.channel.send("Your shop has been created")
            for i in range(len(self.product)):
                if message.reference.message_id == self.product[i]["CURRENT"].id:
                    if self.product[i]["AUTHOR"] == message.author.id:
                        if self.product[i]["NAME"] == None:
                            self.product[i]["NAME"] = message.content
                            rep = await message.channel.send("**REPLY** with the price of the product")
                            self.product[i]["CURRENT"] = rep
                        elif self.product[i]["PRICE"] == None:
                            try:
                                self.product[i]["PRICE"] = float(message.content)
                                rep = await message.channel.send("**REPLY** with the description of the product")
                                self.product[i]["CURRENT"] = rep
                            except:
                                rep = await message.channel.send("**REPLY** with the price of the product (number only)")
                                self.product[i]["CURRENT"] = rep
                        elif self.product[i]["DESC"] == None:
                            self.product[i]["DESC"] = message.content
                            rep = await message.channel.send("**REPLY** with the image url for the product")
                            self.product[i]["CURRENT"] = rep
                        elif self.product[i]["IMGURL"] == None:
                            self.product[i]["IMGURL"] = message.content
                            print(self.product[i])
                            await self.createProduct(self.product[i])
                            await message.channel.send("Your product is good")


                            

                    
            
        #await self.cleanUp()
    async def on_reaction_add(self,reaction, user):
        if user.id != self.user.id:
            if reaction.message.id in self.messages:
            
                if self.messages[reaction.message.id]["object"].author == user:
                    if self.messages[reaction.message.id]["type"] == "ADMIN":
                        await self.adminReact(reaction)
                    print(self.messages[reaction.message.id]["type"])
            else:
                for i in range(len(self.product)):
                    
                    if self.product[i]["CURRENT"] == reaction.message:
                        for j in self.react:
                            if j == reaction.emoji:
                                rep = await reaction.message.channel.send("**REPLY** with the product name:")
                                self.product[i]["CURRENT"] = rep
                                self.product[i]["SHOPNUM"] = self.react.index(j)
                                print(self.product[i])
                        
                    #if self.shop[reaction.message.id]["type"] == "ASKNAME":
                    #    if reaction.emoji == "❌":
                    #        await reaction.message.delete()
                    #        self.messages.pop(reaction.message.id)
                    #    print("gdfigfdhugfehi")

                        

client = MyClient()
client.run('NzE1MTM0MzUyMTAyNjUzOTcy.Xs4yxA.Iw-wQAKWWoVawIs21YXwYR7yD64')
