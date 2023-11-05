import sys
import nltk
from spade.agent import Agent
from spade.message import Message
from spade.behaviour import FSMBehaviour, State
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import string
# adding go ahead with auction state
from src.utils.wikipedia import Wikipedia

STATE_START_AUCTION = "STATE_START_AUCTION"
STATE_MAKE_OFFER = "STATE_MAKE_OFFER"
STATE_ANALYZE_BID = "STATE_ANALYZE_BID"
STATE_DECLARE_WINNER = "STATE_DECLARE_WINNER"
STATE_END = "STATE_END"
STATE_AUCTION = "STATE_AUCTION"
#nltk.download("punkt")
#nltk.download("stopwords")

def preprocess_text(text):
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
class AuctioneerStateMachine(FSMBehaviour):
    async def on_start(self):
        pass
    async def on_end(self):
        await self.agent.stop()

class StartAuctionState(State):
    async def run(self):
        articles_agent_can_sell = self.agent.get("articles_agent_can_sell")
        example = str(articles_agent_can_sell[0:3])
        i = 0
        print(example)
        print(articles_agent_can_sell[0])
        print(Wikipedia.get(Wikipedia(), articles_agent_can_sell[0]))
        print(preprocess_text(Wikipedia.get(Wikipedia(), articles_agent_can_sell[0])))
        for token in preprocess_text(Wikipedia.get(Wikipedia(), articles_agent_can_sell[0])):
            if token == "car":
                i = i + 1
        print(i)




        # officially offering articles to bidders
        for count, auctioneer in enumerate(self.agent.get("bidders_list")):
            msg = Message(to=auctioneer)
            msg.body = "A: Welcome to the biggest Wiki-Auction in the world. We have the following titles to Sell: " \
                       + example + ". You can bid on each of the articles based on your choice."
            await self.send(msg)

        articles_agent_can_sell = self.agent.get("articles_agent_can_sell")
        for article in articles_agent_can_sell:
            pass
          # print(article)

        msg = await self.receive(timeout=sys.float_info.max)
        print("State: StartAuctionState, A: Got message '" + msg.body + " " + self.agent.get("name") + "'")
        self.set_next_state(STATE_MAKE_OFFER)

class MakeOfferState(State):
    async def run(self):
        print("State: MakeOfferState. A: " + self.agent.get("name"))

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
