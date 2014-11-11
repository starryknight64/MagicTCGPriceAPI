#
#   Scraping Utilities
#

import urllib
import logging
import json
import sys

#
#   Retrieves a URL to the card's image as represented by http://magiccards.info
#
def getCardImageURL(cardName, cardSet):
    magicInfoURL = "http://magiccards.info/query?q=" + urllib.quote(cardName)
    if cardSet:
        magicInfoURL += urllib.quote(" e:" + cardSet + "/en")
    htmlFile = urllib.urlopen(magicInfoURL)
    rawHTML = htmlFile.read()
    startURLIndex = rawHTML.find("http://magiccards.info/scans")
    endURLIndex = rawHTML.find("\"", startURLIndex)
    imageURL = rawHTML[startURLIndex:endURLIndex]
    return [imageURL]

#
#   Retrieves a cards current price on Channel Fireball
#
def getCFBPrice(cardName, cardSet):
    cfbURL = "http://store.channelfireball.com/products/search?q=" + urllib.quote(cardName)
    if cardSet:
        cfbURL += " " + urllib.quote(cardSet)
    htmlFile = urllib.urlopen(cfbURL)
    rawHTML = htmlFile.read()    
    tempIndex = rawHTML.find("grid-item-price")
    startPriceIndex = rawHTML.find("$", tempIndex)
    endPriceIndex = rawHTML.find("<", startPriceIndex)
    cfbPrice = rawHTML[startPriceIndex:endPriceIndex]
    return [cfbPrice]

#
#   Retrieves the lowest buy it now price for a card on ebay
#
def getEbayPrice(cardName, cardSet):
    ebayURL = "http://www.ebay.com/sch/i.html?_sacat=0&_sop=15&LH_BIN=1&_nkw=" + urllib.quote(cardName)
    if cardSet:
        ebayURL += urllib.quote(" " + cardSet)
    ebayURL += urllib.quote( " mtg nm")
    logging.info(ebayURL)
    htmlFile = urllib.urlopen(ebayURL)
    rawHTML = htmlFile.read()
    startPriceIndex = rawHTML.find('span  class="g-b">')
    startPriceIndex = rawHTML.find("$", startPriceIndex)
    endPriceIndex = rawHTML.find("<", startPriceIndex)
    lowestBIN = rawHTML[startPriceIndex:endPriceIndex]
    return [lowestBIN]

#
#   Retrieves the low, mid, and high prices of a card as shown on http://tcgplayer.com
#
def getTCGPlayerPrices(cardName, cardSet):
    deckBrewURL = "https://api.deckbrew.com/mtg/cards?name=" + urllib.quote(cardName)
    htmlFile = urllib.urlopen(deckBrewURL)
    jsonResults = json.loads(htmlFile.read())
    
    lowPrice = ""
    midPrice = ""
    highPrice = ""
    for jsonResult in jsonResults:
        if jsonResult["name"].lower() == cardName.lower():
            lowPrice = sys.maxint
            midPrice = 0
            highPrice = -1
            
            editions = jsonResult["editions"]
            if cardSet:
                for edition in jsonResult["editions"]:
                    if edition["set"].lower() == cardSet.lower():
                        editions = [edition]
                        break
            
            prices = len(editions)
            for edition in editions:
                if edition.has_key("price"):
                    price = edition["price"]
                    if lowPrice > int(price["low"]):
                        lowPrice = int(price["low"])
                    if highPrice < int(price["high"]):
                        highPrice = int(price["high"])
                    midPrice += int(price["median"])
                else:
                    prices -= 1
            
            if prices <= 0 or lowPrice == sys.maxint or highPrice < 0:
                lowPrice = ""
                midPrice = ""
                highPrice = ""
                break
            
            lowPrice = "$%.2f" % (lowPrice / 100.0)
            midPrice = "$%.2f" % ((midPrice / float(prices)) / 100.0)
            highPrice = "$%.2f" % (highPrice / 100.0)

    return [lowPrice, midPrice, highPrice]
