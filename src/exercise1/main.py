#!/usr/bin/env python3

import spade

from src.exercise1.agent_bidder import BidderAgent
from src.exercise1.agent_auctioneer import AuctioneerAgent
from src.utils.wikipedia import Wikipedia

async def main():
	# login
	auctioneer = AuctioneerAgent("auctioneer@localhost", "auctioneer")
	bidder1 = BidderAgent("bidder1@localhost", "bidder1")
	bidder2 = BidderAgent("bidder2@localhost", "bidder2")

	#preprocess: cut /n in sell
	with open("exercise1/data/sell.txt", "r") as acs:
		selltxt_mod = [line.rstrip() for line in acs]


#TODO load into corpus json by utils wiki into corpus. training
	# declaring names and ids
	bidder1.set("name", "Janine")
	bidder1.set("id", 1)
	bidder1.set("initialBids", 10)
	bidder1.set("articles_agent_can_buy", open("exercise1/corpus.txt", "r"))
	bidder1.set("articles_agent_can_sell", open("exercise1/data/sell.txt", "r"))

	bidder2.set("name", "June")
	bidder2.set("id", 2)
	bidder2.set("initialBids", 10)
	bidder2.set("articles_agent_can_buy", open("exercise1/corpus.txt", "r"))
	bidder2.set("articles_agent_can_sell", open("exercise1/data/sell.txt", "r"))

	# reference bidders
	auctioneer.set("name", "Fred")
	auctioneer.set("bidders_list", ['bidder1@localhost', 'bidder2@localhost'])
	auctioneer.set("id", 3)
	auctioneer.set("articles_agent_can_buy", open("exercise1/corpus.txt", "r"))
	auctioneer.set("articles_agent_can_sell", selltxt_mod)
	#print(selltxt_mod)

	auctioneer.set("raw_articles", (Wikipedia(), open("exercise1/data/sell.txt", "r")))

	#init
	await bidder1.start()
	await bidder2.start()
	await auctioneer.start()

if __name__ == "__main__":
	spade.run(main())
