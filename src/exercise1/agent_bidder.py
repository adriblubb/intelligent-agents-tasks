import os
import sys

from spade.agent import Agent
from spade.message import Message
from spade.behaviour import FSMBehaviour, State

import src.utils.functions as functions
import src.utils.helpfunctions as helpfunc

STATE_PREPARATION = "STATE_PREPARATION"
# Added states
STATE_AWAIT_DOC = "STATE_AWAIT_DOC"
STATE_CALCULATE_VAL = "STATE_CALCULATE_VAL"
STATE_AWAIT_WIN = "STATE_AWAIT_WIN"
# Added states
STATE_END = "STATE_END"


# TODO: put into helpfunction
def getSellList():
    with open("./exercise1/data/sell_xs.txt", "r") as acs:
        sellList = [line.rstrip() for line in acs]
    print(sellList)
    return sellList


# percentage: return - ,xx if B is bigger A and + ,xx if A is bigger B
def getPercentage(score_docA, score_docB):
    # if score_docA >= score_docB:
    # A bigger B -> percentage would be 0,xx
    percentage = score_docA / score_docB
    # else:
    # if B bigger A, then make it minus
    # percentage = -(score_docA/score_docB)

    # maybe handler for correct inputs eg minus etc. possibly won't happen with tfidf
    return percentage


# Set behaviour of bidder on start and end, create finite state machine agent
class BidderStateMachine(FSMBehaviour):
    async def on_start(self):
        print("Start bidding (", self.agent.name, ")")

    async def on_end(self):
        print("End bidding (", self.agent.name, ")")
        await self.agent.stop()


# State of bidder to prepare for the auction: load and preprocess corpus
class PreparationState(State):
    async def run(self):
        # Load corpus in the knowledge base of agent
        corpus_list = functions.read_file("./exercise1/data/corpus_xs.txt")
        corpus_list = corpus_list.split("\n")

        self.agent.set("corpus_list", corpus_list[1:])

        cache_file_path = "./utils/cache/wiki_tokenized.json"
        if os.path.exists(cache_file_path):
            # if cache exists, load it, skip with reload
            database_processed = functions.read_json_file(cache_file_path)
        else:
            # Load database, preprocess the database for better performance and store tokens in knowledge base of agent
            database = functions.read_json_file("./utils/cache/wikipedia.json")
            database_processed = {}
            for key in database:
                database_processed[key] = helpfunc.preprocessing(database[key])
            functions.write_json_file(cache_file_path, database_processed)

        self.agent.set("database_processed", database_processed)

        # Move to next state
        self.set_next_state(STATE_AWAIT_DOC)


# State of bidder to wait for the document of the auctioneer. Calculates the tf_idf based on the corpus and this
# document. If the bidder gets the message that the auction ends it goes to the end state. Beginning of the loop
class AwaitDocState(State):
    async def run(self):
        """ For debugging purpose or to keep track on the current state:
        print("Await Doc State") """
        # Wait for a message to receive from the auctioneer
        msg = await self.receive(timeout=sys.float_info.max)
        # If the message contains closing auction, then goto the end state
        if "Closing Auction" in msg.body:
            self.set_next_state(STATE_END)
        else:
            # Filter out the selling document
            buy_doc = str(msg.body).split("'")[1]
            self.agent.set("buy_doc", buy_doc)
            # Append the document to the corpus_list
            self.agent.get("corpus_list").append(buy_doc)

            # Calculate the tf_idf on the corpus with the new document
            database = self.agent.get("database_processed")
            self.agent.set("tf.idf_docs", helpfunc.calc_tf_idf(database, self.agent.get("corpus_list")))

            # Move to next state
            self.set_next_state(STATE_CALCULATE_VAL)


# State of the bidder to calculate a value and a price for the item based on the tf_idf. Sends this price to the
# auctioneer. In this auction the bidder has to send a message, even if he doesn't want to bid for the document.
class CalcValState(State):
    async def run(self):
        """ For debugging purpose or to keep track on the current state:
        print("CalcVal State") """
        # Valuating the item based on the tf_idf score
        value = helpfunc.valuating(self.agent.get("database_processed"), self.agent.get("query"),
                                   self.agent.get("tf.idf_docs"), self.agent.get("buy_doc"))
        # TODO - strategie for opponent
        # Calculate the price for the item based on the value
        price = helpfunc.get_price_for_value(value)
        self.agent.get("bought_articles_x_value").append([[self.agent.get("buy_doc")], price])
        self.agent.get("non_bought_articles_x_value").append([[self.agent.get("buy_doc")], price])
        # Send message with the price to the auctioneer
        msg = Message(to=self.agent.get("auctioneer"))
        msg.body = str(price)

        await self.send(msg)

        # Move to next state
        self.set_next_state(STATE_AWAIT_WIN)


# State of bidder to get the announcement of the winner. If the bidder is the winner, the document gets in his corpus
class AwaitWinState(State):
    async def run(self):
        """ For debugging purpose or to keep track on the current state:
        print("Await win state") """
        # Wait for announcement of the winner
        msg = await self.receive(timeout=sys.float_info.max)
        # The bidder not the winner -> remove document from the corpus_list
        if self.agent.name not in msg.body:
            self.agent.get("corpus_list").pop()
            self.agent.get("bought_articles_x_value").pop()
        else:
            # adding article|valuation price to agents' nonbought-list
            self.agent.get("non_bought_articles_x_value").pop()
        # TODO: strategie for better price than the opponent: see which docs he gets -> change price calc (increase by 1/2)
        # Move to next state
        self.set_next_state(STATE_AWAIT_DOC)


# State of bidder to end bidding
class EndState(State):
    async def run(self):
        """ For debugging purpose or to keep track on the current state:
        print("End state: Goodbye to auction") """
        print("\nEnd state; EVALUATION STATE Bidder(", self.agent.get("id"), ")\n")
        #
        #### EVALUATION ####
        #
        # idea:
        # which documents were missed, which were acquired
        # how valuable are acquired docs against non-acquired

        # STEP ONE -> define basic score logic

        # Sum up valuations of bought documents and potential valuations
        bought_valuation_sum = sum([item[1] for item in self.agent.get("bought_articles_x_value")])
        missed_valuation_sum = sum([item[1] for item in self.agent.get("non_bought_articles_x_value")])

        # print("non-bought/val/valmissed" + str(self.agent.get("id")))
        # print(non_bought_articles)
        # print(bought_valuation_sum)
        # print(missed_valuation_sum)

        # check if article num is positive, if yes define
        total_bought_articles = len(self.agent.get("bought_articles_x_value")) if len(
            self.agent.get("bought_articles_x_value")) > 0 else 1
        total_missed_articles = len(self.agent.get("non_bought_articles_x_value")) if len(
            self.agent.get("non_bought_articles_x_value")) > 0 else 1

        # calculating score, avoiding div by zero through arg max
        # score of bought vs not aquired articles
        quality_score = (bought_valuation_sum / total_bought_articles) / max(
            (missed_valuation_sum / total_missed_articles), 1)
        # score of bought vs all given articles
        quality_score_all = (bought_valuation_sum / total_bought_articles) / max(
            ((missed_valuation_sum + bought_valuation_sum) / (total_missed_articles + total_bought_articles)), 1)

        # STEP TWO -> interpret and visualize calculated logic
        # idea: reduce noise of calculated measures. make measures more easily interpretable and understandable

        '''print("Quality Score (bought docs vs not acquired docs) by bidder ", self.agent.get("id"), "is: ",
              quality_score)
        print(
            "calculated based on the total value of bought (normalized) articles:",
            (bought_valuation_sum / total_bought_articles))
        print(
            "correlated with the total value of missed (normalized) articles:",
            max((missed_valuation_sum / total_missed_articles), 1))'''

        x_not_bought = (getPercentage((bought_valuation_sum / total_bought_articles),
                                  (
                                      missed_valuation_sum if missed_valuation_sum > 0 else 1) / total_missed_articles) - 1) * 100

        # get the percentage of bought valuation against not-bought valuation
        '''print("score of bought article-value is by", x_not_bought,
              "% higher than the score of not-acquired articles(normalized average).")

        print("Quality Score (bought docs against all docs) by bidder ", self.agent.get("id"), "is: ",
              quality_score_all)'''

        x_all = (getPercentage((bought_valuation_sum / total_bought_articles),
                               ((missed_valuation_sum + bought_valuation_sum) if (
                                                                                         missed_valuation_sum + bought_valuation_sum) > 0 else 1) / (
                                       total_missed_articles + total_bought_articles)) - 1) * 100
        # get the percentage of bought valuation against all articles' valuation
        '''print("score of bought article-value is by",
              x_all,
              "% higher than the score of all articles(normalized average).")'''
        # STEP THREE: draw a conclusion on given data
        # define a metric to evaluate
        print("The improvement of the chosen documents against the ones, which have not been aquired is as high as",
              x_not_bought, "%.")
        if 0 <= x_all < 20:
            print("With TFIDF, the agent's corpus and given query:", self.agent.get("query"), "by agent:", self.agent.get("id"),
                  " an improvement of: ", x_all, "%could be measured. It could be shown that the chosen documents show greater correlation with the agents query than the set of all documents given. Therefore the algorithm has worked.")
        elif x_all >= 20:
            print("With TFIDF, the agent's corpus and given query:", self.agent.get("query"), "by agent:", self.agent.get("id"),
                  " an significant improvement of: ", x_all, "%could be measured. It could be shown that the chosen documents show greater correlation with the agents query than the set of all documents given. Therefore the algorithm has worked.")
        else:
            print("With TFIDF and given query:", self.agent.get("query"), "by agent: ", self.agent.get("id"), "no improvement could be shown")

        print("The updated corpus of", self.agent.get("id"), " is now: ", self.agent.get("corpus_list"), ".")
        print("Agent", self.agent.get("id"), "has aquired the following docs through the auction: ", [item[0] for item in self.agent.get("bought_articles_x_value")], ".")






# Defines states and transitions of the bidder agent
class BidderAgent(Agent):
    async def setup(self):
        bsm = BidderStateMachine()

        bsm.add_state(name=STATE_PREPARATION, state=PreparationState(), initial=True)
        # Added states
        bsm.add_state(name=STATE_AWAIT_DOC, state=AwaitDocState())
        bsm.add_state(name=STATE_CALCULATE_VAL, state=CalcValState())
        bsm.add_state(name=STATE_AWAIT_WIN, state=AwaitWinState())
        # Added states
        bsm.add_state(name=STATE_END, state=EndState())

        bsm.add_transition(source=STATE_PREPARATION, dest=STATE_AWAIT_DOC)
        # Added transitions
        bsm.add_transition(source=STATE_AWAIT_DOC, dest=STATE_CALCULATE_VAL)
        bsm.add_transition(source=STATE_CALCULATE_VAL, dest=STATE_AWAIT_WIN)
        bsm.add_transition(source=STATE_AWAIT_WIN, dest=STATE_AWAIT_DOC)
        # Added transitions
        bsm.add_transition(source=STATE_AWAIT_DOC, dest=STATE_END)

        self.add_behaviour(bsm)
