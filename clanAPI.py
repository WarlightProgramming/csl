import requests
import string
from decimal import Decimal

def getClans():
    URL = "https://www.warlight.net/Clans/List"
    r = requests.get(URL)
    clanSet = set()
    clanData = r.text.split("/Clans/?ID=")[1:]
    for clan in clanData:
        clanID = ""
        while clan[0] in string.digits:
            clanID += clan[0]
            clan = clan[1:]
        clanSet.add(int(clanID))
    return clanSet

def getValueFromBetween(text, before, after):
    value = text.split(before)[1]
    value = value.split(after)[0]
    return value

def getClanData(clanID):
    URL = "https://www.warlight.net/Clans/?ID=" + str(clanID)
    r = requests.get(URL)
    data = dict()
    clanName = getValueFromBetween(r.text, "<title>", " - Play Risk")
    data["name"] = clanName
    players = list()
    clanPlayers = r.text.split('<td><a href="/Profile?p=')[1:]
    for clanPlayer in clanPlayers:
        playerID = ""
        while clanPlayer[0] in string.digits:
            playerID += clanPlayer[0]
            clanPlayer = clanPlayer[1:]
        players.append(int(playerID))
    data["members"] = players
    numMembers = getValueFromBetween(r.text, 'members:</font> ', '<br />')
    data["size"] = int(numMembers)
    return data

def processLastSeen(lastSeen):
    if "less than 15 minutes" in lastSeen: return float(0)
    result = Decimal()
    lastSeenList = lastSeen.split(" ")
    if "days" in lastSeen:
        dayData = lastSeenList[lastSeenList.index("days")-1]
        dayData = dayData.replace(",", "")
        result += Decimal((int(dayData) * 24))
    elif "day" in lastSeen:
        dayData = lastSeenList[lastSeenList.index("day")-1]
        dayData = dayData.replace(",", "")
        result += Decimal((int(dayData) * 24))
    if "hours" in lastSeen:
        hourData = lastSeenList[lastSeenList.index("hours")-1]
        hourData = hourData.replace(",", "")
        result += Decimal((int(hourData)))
    elif "hour" in lastSeen:
        hourData = lastSeenList[lastSeenList.index("hour")-1]
        hourData = hourData.replace(",", "")
        result += Decimal((int(hourData)))
    if "minutes" in lastSeen:
        minData = lastSeenList[lastSeenList.index("minutes")-1]
        minData = minData.replace(",", "")
        result += Decimal(int(minData)) / Decimal(60)
    return float(result)

def getPlayerData(playerID):
    URL = "https://www.warlight.net/Profile?p=" + str(playerID)
    r = requests.get(URL)
    data = dict()
    data["name"] = getValueFromBetween(r.text, "<title>", " - Play Risk")
    pointInfo = (getValueFromBetween(r.text,
                                     "30 days:</font> ", "<br />"))
    data["points"] = int(pointInfo.replace(",", ""))
    lastSeen = getValueFromBetween(r.text, "Last seen </font>",
                                   "<font color")
    data["lastSeen"] = processLastSeen(lastSeen)
    if "1 v 1 ladder</a>" in r.text:
        data1v1 = r.text.split("1 v 1 ladder</a>:")[1]
        rating = int(getValueFromBetween(data1v1, "rating of", "."))
        data["1v1rating"] = rating
    return data

def main():
    requests.packages.urllib3.disable_warnings()
    clans = getClans()
    clanList = list()
    for clan in clans:
        clanData = getClanData(clan)
        name = clanData["name"]
        print "analyzing", name
        members = clanData["members"]
        size = clanData["size"]
        active = 0
        above1500 = 0
        pointSum = 0
        for member in members:
            memberData = getPlayerData(member)
            pointSum += memberData["points"]
            if memberData["lastSeen"] < 24:
                active += 1
            if ("1v1rating" in memberData and
                memberData["1v1rating"] >= 1500):
                above1500 += 1
        activityRate = float(Decimal(active) / Decimal(size))
        pointRate = float(Decimal(pointSum) / Decimal(size))
        clanList.append((name, size, active, activityRate, above1500,
                         pointSum, pointRate))
    clanList = sorted(clanList, key=lambda x: x[1])
    clanList.reverse()
    print ("Number of members")
    for x in xrange(len(clanList)):
        print (unicode(x) + ". " + unicode(clanList[x][0]) + ": " + unicode(clanList[x][1]))
    clanList = sorted(clanList, key=lambda x: x[2])
    clanList.reverse()
    print ("Members active in last 24 hours")
    for x in xrange(len(clanList)):
        print (unicode(x) + ". " + unicode(clanList[x][0]) + ": " + unicode(clanList[x][2]))
    clanList = sorted(clanList, key=lambda x: x[3])
    clanList.reverse()
    print ("Portion active in last 24 hours")
    for x in xrange(len(clanList)):
        print (unicode(x) + ". " + unicode(clanList[x][0]) + ": " + unicode(clanList[x][3]))
    clanList = sorted(clanList, key=lambda x: x[4])
    clanList.reverse()
    print ("Members with over 1500 points on the 1v1 ladder")
    for x in xrange(len(clanList)):
        print (unicode(x) + ". " + unicode(clanList[x][0]) + ": " + unicode(clanList[x][4]))
    clanList = sorted(clanList, key=lambda x: x[5])
    clanList.reverse()
    print ("Point sum in last 30 days")
    for x in xrange(len(clanList)):
        print (unicode(x) + ". " + unicode(clanList[x][0]) + ": " + unicode(clanList[x][5]))
    clanList = sorted(clanList, key=lambda x: x[6])
    clanList.reverse()
    print ("Average points per member")
    for x in xrange(len(clanList)):
        print (unicode(x) + ". " + unicode(clanList[x][0]) + ": " + unicode(clanList[x][6]))
