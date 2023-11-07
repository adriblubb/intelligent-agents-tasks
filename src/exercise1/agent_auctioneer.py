import sys
import nltk
from spade.agent import Agent
from spade.message import Message
from spade.behaviour import FSMBehaviour, State
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import string
import random
import time
# adding go ahead with auction state
from src.utils.wikipedia import Wikipedia

STATE_START_AUCTION = "STATE_START_AUCTION"
STATE_MAKE_OFFER = "STATE_MAKE_OFFER"
STATE_ANALYZE_BID = "STATE_ANALYZE_BID"
STATE_DECLARE_WINNER = "STATE_DECLARE_WINNER"
STATE_END = "STATE_END"
STATE_AUCTION = "STATE_AUCTION"

# list. list of rendered articles
rendered_articles = []
#list. list which will be filled in runtime
articles_auction = []
# integer, how many articles are auctioned
num_auctioned_articles = 3




class AuctioneerStateMachine(FSMBehaviour):
    async def on_start(self):
        # print(self.get_auction_articles(3))
        pass

    async def on_end(self):
        await self.agent.stop()

    #returns titles
    def getTitles(self):
        return articles_auction

    #return currently renderd articles
    def getRenderedArticles(self):
        return rendered_articles

    # returns list of *num_articles* headings, randomly chosen
    def create_auction_titles(self, num_articles):
        # prepare 3 wiki articles for the auction
        articles_agent_can_sell = self.agent.get("articles_agent_can_sell")
        # test print
        for article in range(num_articles):
            articles_auction.append(articles_agent_can_sell[random.randint(0, len(articles_agent_can_sell))])

        return articles_auction

    # turn wiki articles into td.idf input
    def render(self, text):
        # Tokenize the text
        tokens = word_tokenize(text)

        # Convert tokens to lowercase
        tokens = [token.lower() for token in tokens]

        # Remove punctuation from each token
        tokens = [token for token in tokens if token not in string.punctuation]

        # Filter out tokens that are not alphabetic
        tokens = [token for token in tokens if token.isalpha()]

        # Filter out stop words
        stop_words = set(stopwords.words("english"))
        tokens = [token for token in tokens if token not in stop_words]

        # Stem words with PorterStemmer
        stemmer = PorterStemmer()
        tokens = [stemmer.stem(token) for token in tokens]

        return tokens

    def article_rendered(self, article):
        return self.render(Wikipedia.get(Wikipedia(), article))

    def articles_rendered(self, titles):
        asm = AuctioneerStateMachine
        for article in titles:
            rendered_articles.append(asm.render(self, Wikipedia.get(Wikipedia(), article)))
        return rendered_articles


class StartAuctionState(State):

    async def run(self):
        asm = AuctioneerStateMachine
        titles = asm.create_auction_titles(self, 3)
        rendered_articles = asm.articles_rendered(self, titles)
        print(titles)
        #print("rendered first:")
        #print(asm.articles_rendered(self, titles)[1][1:200])

        # officially offering articles to bidders
        for count, bidder in enumerate(self.agent.get("bidders_list")):
            msg = Message(to=bidder)
            msg.body = "A: Welcome to the biggest Wiki-Auction in the world. We have the following titles to Sell: " \
                       + str(titles) + ". You can bid on each of the articles based on your choice."
            await self.send(msg)
        #msg3 = await self.receive(timeout=sys.float_info.max)
        #print("State: StartAuctionState, A: Got message '" + msg3.body + " " + self.agent.get("name") + "'")
        # Update the agent's data with the rendered articles
        self.agent.set("rendered_articles", rendered_articles)
        self.set_next_state(STATE_MAKE_OFFER)

class MakeOfferState(State):
    async def run(self):
        print("State: MakeOfferState. A: " + self.agent.get("name"))
        asm = AuctioneerStateMachine
        print("check")
        #temp test
        x = asm.getTitles(self)
        articles = asm.getRenderedArticles(self)


        for count, bidder in enumerate(self.agent.get("bidders_list")):
            msg2 = Message(to=bidder)
            print("current article being auctioned: "+ x[0])
            msg2.body = str("msg2test"+str(articles[0]))
            await self.send(msg2)

        self.set_next_state(STATE_ANALYZE_BID)

class AnalyzeBidState(State):
    async def run(self):
        self.set_next_state(STATE_END)

# auction ends, when als articles are sold
class EndState(State):
    async def run(self):
        print("State: EndState. A: "+self.agent.get("name"))



class AuctioneerAgent(Agent):
    async def setup(self):
        asm = AuctioneerStateMachine()

        asm.add_state(name=STATE_START_AUCTION, state=StartAuctionState(), initial=True)
        asm.add_state(name=STATE_MAKE_OFFER, state=MakeOfferState())
        asm.add_state(name=STATE_ANALYZE_BID, state=AnalyzeBidState())
        asm.add_state(name=STATE_END, state=EndState())


        # adding transitions prep -> start/welcome -> how will auction work ->
        asm.add_transition(source=STATE_START_AUCTION, dest=STATE_MAKE_OFFER)
        asm.add_transition(source=STATE_MAKE_OFFER, dest=STATE_ANALYZE_BID)
        asm.add_transition(source=STATE_ANALYZE_BID, dest=STATE_MAKE_OFFER)
        asm.add_transition(source=STATE_MAKE_OFFER, dest=STATE_END)
        # temp transition to test
        asm.add_transition(source=STATE_ANALYZE_BID, dest=STATE_END)

        self.add_behaviour(asm)
