import requests
import trueskill

def getLadderImages(ladderID, startPage, numPages):
    baseURL = "https://www.warlight.net/LadderGames?ID="
    URL = baseURL + str(ladderID)
    offset = 50 * startPage
    numGames = numPages * 50 + offset
    images = list()
    while (offset < numGames):
        try:
            callURL = URL + "&Offset=" + str(offset)
            r = requests.get(callURL)
            if ("defeated" not in r.text): break
            images.append(r.text)
            offset += 50
        except: continue
    return images

def reverse(iterable):
    iterable.reverse()
    return iterable

def pullClan(sideData):
    keyPhrase = "/Clans/?ID="
    if (keyPhrase not in sideData):
        return unicode("(unclanned)")
    valuePhrase = '" title="'
    clan = sideData.split(valuePhrase)[1]
    clan = clan.split('"><')[0]
    return clan

def pullClanResults(ladderImages, diffOnly=False):
    results = list()
    for image in ladderImages:
        games = image.split('<tr style="background-color: inherit">')[1:]
        for game in games:
            winnerData, loserData = game.split("defeated")
            loserData = loserData.split("</td>")[0]
            winnerClan = pullClan(winnerData)
            loserClan = pullClan(loserData)
            if (winnerClan == "(unclanned)" or loserClan == "(unclanned)"):
                continue
            if not(diffOnly and winnerClan == loserClan):
                results.append((winnerClan, loserClan))
    return reverse(results)
            
def rateClans(ladderID, startPage, numPages):
    clans = dict()
    images = getLadderImages(ladderID, startPage, numPages)
    clanResults = pullClanResults(images, True)
    for result in clanResults:
        winnerClan, loserClan = result
        if (winnerClan not in clans):
            clans[winnerClan] = (0, trueskill.Rating())
        if (loserClan not in clans):
            clans[loserClan] = (0, trueskill.Rating())
        winnerCount, winnerRating = clans[winnerClan]
        loserCount, loserRating = clans[loserClan]
        winnerRating, loserRating = trueskill.rate_1vs1(winnerRating,
                                                        loserRating)
        clans[winnerClan] = (winnerCount+1, winnerRating)
        clans[loserClan] = (loserCount+1, loserRating)
    return len(clanResults), clans
