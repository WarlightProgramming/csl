import api
import clanAPI
import random
import copy
import time
import requests

print "This is the elite one!"
requests.packages.urllib3.disable_warnings()
clans = set([9, 73, 11, 188, 33, 156, 80, 15, 170, 20, 82])
print "All clans obtained!"
templates = [763479, 763480, 763481, 763482, 763483, 763485, 763486, 763487,
             763488, 763489]

class Session(object):

    def __init__(self, clans, templates):
        self.email = "REDACTED"
        self.password = "REDACTED"
        self.title = "Real-Time Matchmaking | Test Game"
        self.message = "This is a test of an automated real-time\
 matchmaking system. Currently it's being run on your clan and a few others. \n\n\
The templates used are the same as those of the Real-Time Ladder and are\
 randomized for each game. If you don't want to be part of this experiment or\
 want to quit at any time, simply hit the decline button and you will be taken\
 out of the system for the remainder of this round of the experiment.\n\n\
I apologize in advance for any bugs (especially the duplicate games- I'm just\
 restarting the system as I catch bugs). This is just the first test.\n\n\
If you have feedback, don't hesitate to PM me. Thanks. -knyte\n\n\
UPDATE: Self-removal is now fully working. If it doesn't, PM me ASAP. \n\
UPDATE2: Small modifications (no OP/OD cards, no attack by percentage)\
 have been made to the templates\
 so that more players are able to participate. They're also RT now.\n\
UPDATE3: This is opt-out. I apologize\
 if this is spammy- PM me if it's too big of an issue.\n\n\
\
Also, this is supposed to be a system which pairs two people who are\
 both currently online. If your partner is not online but you want to stay\
 in the system, don't hit Decline (unless you want to leave)- it should be handled automatically if\
 they go offline. Thanks."
        self.blacklist = set([3022124041, 536388049, 4940310287])
        self.token = api.getAPIToken(self.email, self.password)
        self.activeGames = set()
        self.clans = clans
        self.templates = templates
        self.playerPool = self.getAllPlayers()
        print "setup complete!"

    def getAllPlayers(self):
        players = list()
        for clan in self.clans:
            playerList = clanAPI.getClanData(clan)["members"]
            players += playerList
        return players

    def getPlayers(self):
        self.xplayers = list()
        self.examined = list()
        for player in self.playerPool:
            if (clanAPI.getPlayerData(player)["lastSeen"] == 0):
                self.xplayers.append(player)
            self.examined.append(player)
        for player in copy.copy(self.xplayers):
            if player in self.blacklist:
                self.xplayers.remove(player)
        print "players retrieved!"
        return self.xplayers

    def makeGames(self):
        self.players = self.getPlayers()
        print "Running with", len(self.players), "players"
        random.shuffle(self.players)
        player1List = self.players[:len(self.players)/2]
        player2List = self.players[len(self.players)/2:]
        for x in xrange(len(player1List)):
            player1 = player1List[x]
            player2 = player2List[x]
            template = self.templates[random.randint(0, len(self.templates)-1)]
            try:
                game = api.createGame(self.email, self.token, template=template,
                                      gameName=self.title, message=self.message,
                                      teams=[player1, player2])
                self.activeGames.add(game)
                self.blacklist.add(player1)
                self.blacklist.add(player2)
            except:
                print "Failure on template", template, "with", player1, player2
        print self.activeGames
        print self.players

    def updateGames(self):
        for game in copy.copy(self.activeGames):
            try:
                gameFailed = False
                queryData = api.queryGame(self.email, self.token, game)
                if queryData['state'] == unicode("Finished"):
                    self.activeGames.remove(game)
                    for player in queryData['players']:
                        playerID = int(player['id'])
                        self.blacklist.remove(playerID)
                    continue
                for player in queryData['players']:
                    if player['state'] == "Declined":
                        try:
                            self.playerPool.remove(int(player['id']))
                        except:
                            print "removal failure for", player['id']
                        gameFailed = True
                    elif (playper['state'] == "Invited"):
                        for playa in queryData['players']:
                          if (clanAPI.getPlayerData(int(playa['id']))['lastSeen']
                              >= 0.25):
                              gameFailed = True
                if gameFailed:
                    for player in queryData['players']:
                        try:
                            self.blacklist.remove(int(player['id']))
                        except: print "deblacklist failure for", player['id']
                    try:
                        api.deleteGame(self.email, self.token, game)
                        self.activeGames.remove(game)
                    except: continue
            except:
                print "Failure at game", game
                try: self.activeGames.remove(game)
                except: continue
                continue
        print "update", self.activeGames, self.players

    def run(self):
        while True:
            try:
                self.makeGames()
                self.updateGames()
                time.sleep(1)
            except KeyboardInterrupt:
                print "Okay, okay, I get it!"
                for game in copy.copy(self.activeGames):
                    try: api.deleteGame(self.email, self.token, game)
                    except: pass
                    self.activeGames.remove(game)
                print "There! All cleaned up!"
                break
            except: continue


if __name__ == "__main__":
    s = Session(clans, templates)
    s.run()
