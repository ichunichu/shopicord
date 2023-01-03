import appwrite


from appwrite.client import Client
from appwrite.id import ID
from appwrite.services.databases import Databases
from appwrite.query import Query


discord ="63b40250a8cac7c962fd"
offersCollection = "63b402fe5c72118d86a6"
shopsCollection = "63b40271364e51952c74"

class Database:
    def __init__(self,apikey):
        self.client = Client()

        (self.client
         .set_endpoint('https://appwrite.senditeverywhere.com/v1')  # Your API Endpoint
         .set_project('63b4021b72c1369605fc')  # Your project ID
         .set_key(apikey)  # Your secret API key
         )
        self.database = Databases(self.client)

    def addShop(self, serverId, shopOwner, name="", description="",channelId=""):
        print(serverId, shopOwner, name, description)
        print(type(serverId), type(shopOwner), type(name), type(description))
        self.database.create_document(discord,shopsCollection,ID.unique(),{"serverId":str(serverId),"shopOwner":str(shopOwner),"name":name,"description":description,"channel":str(channelId)})

    def addOffer(self, shopId, price, name, description, imgUrl):
        self.database.create_document(discord,offersCollection,ID.unique(),{"shopId":shopId,"price":float(price),"name":name,"description":description,"imageUrl":imgUrl})

    def getShops(self, shopOwner, guildid):
        command = f'SELECT * FROM "main"."Shops" WHERE ShopOwner = "{shopOwner}" and ServerId = {guildid} ORDER BY Shopid;'
        self.cur.execute(command)
        res = self.cur.fetchall()
        #print("SHOPS", res, command)
        # SELECT * FROM "main"."Shops" WHERE ShopOwner = "697888128043581511" and ServerId = 702593985776058569;
        # SELECT * FROM "main"."Shops" WHERE ShopOwner = "697888128043581511" and ServerId = 697888128043581511;
        # 697888128043581511 715134352102653972
        return res

    def getOffers(self, shopid):
        mystr = f'SELECT * FROM "main"."Offers" WHERE ShopId = "{shopid}" ORDER BY Shopid;'
        self.cur.execute(mystr)
        res = self.cur.fetchall()
        return res

    def getShopByChannel(self,guildId,channelId):
        documents = self.database.list_documents(discord,shopsCollection,[
            Query.equal("channel",str(channelId)),
            Query.equal("serverId",str(guildId))
        ])
        print(documents)
        print(type(documents))
        if documents["total"] == 0:
            return False
        return documents["documents"][0]


    def getShop(self, shopOwner="", shopName="", guildid="", shopid=None):
        rep = 0
        if shopid is None:
            self.cur.execute(
                f'SELECT * FROM "main"."Shops" WHERE ShopOwner= "{shopOwner}" and Name = "{shopName}" and ServerId = "{guildid}" ORDER BY Shopid;')
            rep = self.cur.fetchone()
        elif type(shopid) == int:
            self.cur.execute(f'SELECT * FROM "main"."Shops" WHERE Shopid = {shopid} ORDER BY Shopid;')
            rep = self.cur.fetchone()
        return rep

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