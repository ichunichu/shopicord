import appwrite


import os
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")



discord ="63b40250a8cac7c962fd"
offersCollection = "63b402fe5c72118d86a6"
shopsCollection = "63b40271364e51952c74"

class Database:
    def __init__(self,apikey):
         self.supabase = create_client("https://sxxcyvxxbsuxtqhmdwes.supabase.co", apikey)


    def addShop(self, guild_id, shopOwner, name="", description="",channel_id=""):
        print(guild_id, shopOwner, name, description)
        print(type(guild_id), type(shopOwner), type(name), type(description))
        data = self.supabase.table("shop").insert({"guild_id":str(guild_id),"name":name,"description":description,"channel_id":str(channel_id)}).execute()
        return data
    def addOffer(self, shop_id, price, name, description, img_url=None):
        return self.supabase.table("offer").insert({"shop_id":shop_id,"price":float(price),"name":name,"description":description,"img_url":None}).execute()

    def editOffer(self, offer_id, price, name, description, imgUrl):
        return self.supabase.table("offer").update({"price":float(price),"name":name,"description":description,"imageUrl":imgUrl}).eq("id",offer_id).execute()

    #def getShops(self, shopOwner, guildid):
        #self.cur.execute(command)
        #res = self.cur.fetchall()
        #print("SHOPS", res, command)
        # SELECT * FROM "main"."Shops" WHERE ShopOwner = "697888128043581511" and ServerId = 702593985776058569;
        # SELECT * FROM "main"."Shops" WHERE ShopOwner = "697888128043581511" and ServerId = 697888128043581511;
        # 697888128043581511 715134352102653972
        #return res

    def getOffers(self, shop_id):

        data = self.supabase.table("offer").select("*").filter("shop_id","eq",shop_id).execute()
        print(data)
        return data.data
    def getOffer(self, offerid):
        offer = self.database.get_document(discord,offersCollection,offerid)
        if offer:
            print(offer)
            return offer
        return False

    def getShopByChannel(self,guild_id,channel_id):
        print("getting shop")
        data = self.supabase.table("shop").select("*").filter("channel_id","eq",channel_id).execute()
        print("requested")
        print(data)
        return data.data[0]

    def getShopByOffer(self,offer):
        print(offer)
        data =self.supabase.table("shop").select("*").eq("id",offer["shop_id"]).execute()

        return data


    def updateCurrentChannel(self, channelid, shopid):
        COMMAND = f'UPDATE "main"."Shops" SET "ActualChannel"="{channelid}" WHERE Shopid = "{shopid}"'
        self.cur.execute(COMMAND)

    def getCategory(self, serverId):
        self.cur.execute(f'SELECT ShopCat FROM "main"."Servers" WHERE id = "{serverId}" ORDER BY id;')
        self.cur.fetchall()
        self.con.close()

    def updateShop(self, shopOwner,guildid,num,NAME,DESC):
        shop = self.numToShop(shopOwner,guildid,num)
        COMMAND = f'UPDATE "main"."Shops" SET "Name"="{NAME}" , "Description"="{DESC}"  WHERE "Shopid"="{shop[0]}"'
        self.cur.execute(COMMAND)

    def createUser(self,user_id):
        self.supabase.table("discord_user").insert({"user_id":user_id})