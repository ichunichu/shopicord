import sqlite3
class Database:
    def __init__(self):
        self.con = sqlite3.connect('discord.db')
        self.cur = self.con.cursor()

    def addServer(self, serverId):
        self.cur.execute(f'INSERT INTO "main"."Servers"("id") VALUES ({serverId});')
        self.con.commit()
        self.con.close()
    
    def checkServer(self, serverId):
        self.cur.execute(f'select count(*) from Servers WHERE id = {serverId};')
        if self.cur.fetchone()[0] == 1:
            return(True)
        elif self.addServer(serverId) == True:
            return(True)
        return(False)

    
    def addShop(self, serverId,shopOwner,Name="",Description=""):
        print(serverId, shopOwner, Name, Description)
        self.cur.execute(f'INSERT INTO "main"."Shops"("ServerId", "ShopOwner", "Name", "Description")VALUES ({serverId}, "{shopOwner}", "{Name}", "{Description}");')
        self.con.commit()
        self.con.close()
        
        return(True)

db = Database()

db.addShop(125,115515,"NAME","DESFY")