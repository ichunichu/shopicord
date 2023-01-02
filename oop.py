import asyncio
import sqlite3
def serverCheck(severId):
    pass
def createServer(serverId):
    pass

class Server:
    def __init__(self,serverId) -> None:
        if serverCheck(serverId) == True:
            self.id = serverId
        else:
            if createServer(serverId):
                self.id = serverId
    def Check(self):
        if serverCheck(self.id):
            return(True)
        return(False)



class Database:
    def __init__(self):
        self.con = sqlite3.connect('discord.db')
        self.cur = self.con.cursor()

    async def addServer(self, serverId):
        self.cur.execute(f'INSERT INTO "main"."Servers"("id") VALUES ({serverId});')
        await self.con.commit()
    
    async def checkServer(self, serverId):
        await self.cur.execute(f'select count(*) from Servers WHERE id = {serverId};')
        return(self.cur.fetchall())


db = Database()
loop = asyncio.get_event_loop()
print( db.checkServer(1254))
while True:
    pass
