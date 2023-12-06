#!/usr/bin/env python3

import spade

# get your solution from exercise 1!
from src.exercise2.agent_ir import IRAgent # e.g., might rename bidder cause answering added
from src.exercise2.agent_auctioneer import AuctioneerAgent
# new agent type
from src.exercise2.agent_questioner import QuestionerAgent

async def main():
	# functionality to implement:
	'''
	testing: getting to know lda and playing with it

	building lda model
	tune lda hyperparams
	visualize an lda model
	create answer query by lda  -> hellinger distance (similar docs)
	evaluatie the performance: lda, tfidf
	create human aware behavior
	 -> calc discrepancy of self/query; combine lda and tfidf

	 then: integrate into agents

	 intermezzo of questioners and ir agents and auctioneer
	 update lda model
	 adjust bidding vals



	'''
	# IR agents
	ir1 = IRAgent("bidder1@localhost", "bidder1")
	ir1.set("corpus_file", "corpus")
	# defining some query as wikipedia article
	ir1.set("query", ["New York City", "Harrison Ford", "Choi Min-sik"])
	await ir1.start()

	ir2 = IRAgent("bidder2@localhost", "bidder2")
	ir2.set("corpus_file", "corpus")
	# defining some query as wikipedia article
	ir2.set("query", ["Honda", "Seattle", "Audi"])
	await ir2.start()

	# Auctioneer
	auctioneer = AuctioneerAgent("auctioneer@localhost", "auctioneer")
	auctioneer.set("bidders_list", ['bidder1@localhost', 'bidder2@localhost'])
	auctioneer.set("documents_file", "sell")
	await auctioneer.start()

	# Questioners
	questioner1 = QuestionerAgent("questioner1@localhost", "questioner1")
	questioner1.set("query_target", "bidder1@localhost")
	questioner1.set("queries_file", "queries_i")
	await questioner1.start()

	questioner2 = QuestionerAgent("questioner2@localhost", "questioner2")
	questioner2.set("query_target", "bidder2@localhost")
	questioner2.set("queries_file", "queries_ii")
	await questioner2.start()

if __name__ == "__main__":
	spade.run(main())
