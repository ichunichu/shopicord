import appwrite

from dotenv import load_dotenv
load_dotenv()
import os
from pocketbase import PocketBase # Client also works the same

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
mail: str = os.environ.get("SERVICE_MAIL")
password: str = os.environ.get("SERVICE_PASS")
print(mail)


discord ="63b40250a8cac7c962fd"
offersCollection = "63b402fe5c72118d86a6"
shopsCollection = "63b40271364e51952c74"

class Database:
    def __init__(self):
         self.client = PocketBase('https://database.senditeverywhere.com')
         self.client.admins.auth_with_password(mail, password)


    def addShop(self, guild_id, shop_owner_id, name="", description="",channel_id=""):
        print(guild_id, shop_owner_id, name, description)
        print(type(guild_id), type(shop_owner_id), type(name), type(description))


        data = {
            "name": name,
            "description": description,
            "guild_id": guild_id,
            "channel_id": channel_id,
            "admins": [
                shop_owner_id
            ]
        };
        data = self.client.collection('shops').create(data);
        return data
    def addOffer(self, shop_id, price, name, description, img_url=None):

        data = {
            "name": name,
            "shop_id": shop_id,
            "description": description,
            "img_url": img_url,
            "price": price
        };

        record = self.client.collection('offers').create(data);
        return record

    def editOffer(self, offer_id, price, name, description, imgUrl):
        return self.client.collection("offers").update(offer_id,{"price":float(price),"name":name,"description":description,"imageUrl":imgUrl})

    #def getShops(self, shopOwner, guildid):
        #self.cur.execute(command)
        #res = self.cur.fetchall()
        #print("SHOPS", res, command)
        # SELECT * FROM "main"."Shops" WHERE ShopOwner = "697888128043581511" and ServerId = 702593985776058569;
        # SELECT * FROM "main"."Shops" WHERE ShopOwner = "697888128043581511" and ServerId = 697888128043581511;
        # 697888128043581511 715134352102653972
        #return res

    def getOffers(self, shop_id):
        data = self.client.collection("offers").get_list(1,50, {"filter":f"shop_id == {shop_id}"})
        print(data)
        return data.items
    def getOffer(self, offer_id):
        offer = self.client.collection('shops').getOne(offer_id);
        if offer:
            print(offer)
            return offer
        return False

    def getShopByChannel(self,guild_id,channel_id):
        print("getting shop")
        data = self.client.collection("shops").get_list(1,2,{"filter": f'channel_id = {channel_id}'})
        print("requested")
        print(data)
        if data.total_items == 0:
            return False
        return data.items[0]

    def getShopByOffer(self,offer):
        print(offer)
        data =self.client.collection("shops").get_one(offer["shop_id"])

        return data


    def updateCurrentChannel(self, channelid, shopid):
        COMMAND = f'UPDATE "main"."Shops" SET "ActualChannel"="{channelid}" WHERE Shopid = "{shopid}"'
        self.cur.execute(COMMAND)

    def updateShop(self, shopOwner,guildid,num,NAME,DESC):
        shop = self.numToShop(shopOwner,guildid,num)
        COMMAND = f'UPDATE "main"."Shops" SET "Name"="{NAME}" , "Description"="{DESC}"  WHERE "Shopid"="{shop[0]}"'
        self.cur.execute(COMMAND)

    def createUser(self,user_id):
        self.supabase.table("discord_user").insert({"user_id":user_id})