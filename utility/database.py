import sqlite3


class Database:
    def __init__(self):
        self.con = sqlite3.connect('discord.db', isolation_level=None)
        self.cur = self.con.cursor()

    def addServer(self, serverId):
        self.cur.execute(f'INSERT INTO "main"."Servers"("id") VALUES ({serverId});')

    def checkServer(self, serverId):
        self.cur.execute(f'select count(*) from Servers WHERE id = {serverId} ORDER BY id;')
        if self.cur.fetchone()[0] == 1:
            # self.con.close()
            return True
        else:
            self.addServer(serverId)
            # self.con.close()
            return True

    def addShop(self, serverId, shopOwner, Name="", Description=""):
        print(serverId, shopOwner, Name, Description)
        self.cur.execute(
            f'INSERT INTO "main"."Shops"("ServerId", "ShopOwner", "Name", "Description")VALUES ({serverId}, "{shopOwner}", "{Name}", "{Description}") returning ServerId;')

        return self.numToShop(shopOwner, serverId, -1)[0]

    def addProduct(self, shopid, price, name, description, IMGURL):
        try:
            # print(f'INSERT INTO "main"."Offers"("ShopId", "Price", "Name", "Desc", "ImageUrl")VALUES ({shopid}, {price}, "{name}", "{description}", "{IMGURL}");')
            self.cur.execute(
                f'INSERT INTO "main"."Offers"("ShopId", "Price", "Name", "Desc", "ImageUrl")VALUES ({shopid}, {price}, "{name}", "{description}", "{IMGURL}");')
            return True
        except:
            return False

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

    def numToShop(self, shopOwner, guildid, num):
        return self.getShops(shopOwner, guildid)[num]

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