#!/usr/bin/env python3
import spade

from src.exercise1.agent_bidder import BidderAgent
from src.exercise1.agent_auctioneer import AuctioneerAgent


# Define main method of the auction. Create bidder and auctioneer agents and set initialized variables
async def main():
	# Create bidder agent 1
	bidder1 = BidderAgent("bidder1@localhost", "bidder1")
	await bidder1.start()
	# Give query to bidder 1, can be done randomly if wish
	bidder1.set("query", ["Honda", "BMW", "Audi"])
	# nested list, list tuple of bought articles and their calculated value on aquisition
	bidder1.set("bought_articles_x_value", [])
	# nested list, list tuple of non-bought articles and their calculated value on aquisition
	bidder1.set("non_bought_articles_x_value",[])
	# id of the bidder
	bidder1.set("id", 1)


	# Create bidder agent 2
	bidder2 = BidderAgent("bidder2@localhost", "bidder2")
	await bidder2.start()
	# Give query to bidder 2, can be done randomly if wish
	bidder2.set("query", ["Edward Norton", "Harrison Ford", "Johnny Depp"])
	# list articles which were aquired
	bidder2.set("bought_articles", [])
	# nested list, list tuple of bought articles and their calculated value on aquisition
	bidder2.set("bought_articles_x_value", [])
	# nested list, list tuple of non-bought articles and their calculated value on aquisition
	bidder2.set("non_bought_articles_x_value", [])
	# id of the bidder
	bidder2.set("id", 2)
	# possibly add later for better performance. - as cache file
	# bidder1.set("tf_idf_cache", {})
	# bidder2.set("tf_idf_cache", {})

	# Create auctioneer agent
	auctioneer = AuctioneerAgent("auctioneer@localhost", "auctioneer")
	auctioneer.set("bidders_list", ['bidder1@localhost', 'bidder2@localhost'])
	bidder1.set("auctioneer", "auctioneer@localhost")
	bidder2.set("auctioneer", "auctioneer@localhost")
	await auctioneer.start()


if __name__ == "__main__":
	spade.run(main())

# TODO - fragen auf dem Zettel beantworten in txt
# TODO - TODOs aus dem Code abarbeiten
# TODO - aufgabe 6
# TODO - valuierung und preisberechnung prüfen, gegebenenfalls tf_idf berechnung anpassen
# TODO - klären was passiert wenn beide das Dokument nicht haben wollen -> trotzdem vergeben?
# TODO - runtime Fehlermeldung am Ende beseitigen?
# Frage 1 : queries die eine eindeutige Mehrheit eines bestimmten Topics besitzen (so wird nicht einfach auf alles geboten)
