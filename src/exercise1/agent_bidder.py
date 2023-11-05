import sys
import os
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import string
from spade.agent import Agent
from spade.message import Message
from spade.behaviour import FSMBehaviour, State

STATE_AWAIT_START = "STATE_AWAIT_START"
# adding state which listens to the auctioneers input
STATE_AWAIT_OFFER = "STATE_AWAIT_OFFER"
STATE_ANALYZE_OFFER = "STATE_ANALYZE_OFFER"
STATE_END = "STATE_END"
#nltk.download("punkt")
#nltk.download("stopwords")

class BidderStateMachine(FSMBehaviour):
    async def on_start(self):
        pass

    async def on_end(self):
        await self.agent.stop()



class AwaitStartState(State):
    async def run(self):

        msg = await self.receive(timeout=sys.float_info.max)
        print("State: AwaitStart. B: Got message '" + msg.body + " " + "B: "+ self.agent.get("name") + " has "+str(self.agent.get("initialBids"))+ " bids left.'")
        self.set_next_state(STATE_AWAIT_OFFER)

class AwaitOfferState(State):
    async def run(self):
        print("State: AwaitOfferState. B: "+ self.agent.get("name"))
        msg = Message(to="auctioneer@localhost")
        msg.body = "BRO"
        await self.send(msg)
        self.set_next_state(STATE_ANALYZE_OFFER)

class AnalyzeOfferState(State):
    async def run(self):
        self.set_next_state(STATE_END)

class EndState(State):
    async def run(self):
        print("State: EndState. B: " + self.agent.get("name"))


class BidderAgent(Agent):
    async def setup(self):
        bsm = BidderStateMachine()

        # adding offer state to bidder state management
        bsm.add_state(name=STATE_AWAIT_START, state=AwaitStartState(), initial=True)
        bsm.add_state(name=STATE_AWAIT_OFFER, state=AwaitOfferState())
        bsm.add_state(name=STATE_ANALYZE_OFFER, state=AnalyzeOfferState())
        bsm.add_state(name=STATE_END, state=EndState())

        bsm.add_transition(source=STATE_AWAIT_START, dest=STATE_AWAIT_OFFER)
        bsm.add_transition(source=STATE_AWAIT_OFFER, dest=STATE_ANALYZE_OFFER)
        bsm.add_transition(source=STATE_ANALYZE_OFFER, dest=STATE_AWAIT_OFFER)
        bsm.add_transition(source=STATE_AWAIT_OFFER, dest=STATE_END)
        # temp transition to test
        bsm.add_transition(source=STATE_ANALYZE_OFFER, dest=STATE_END)

        self.add_behaviour(bsm)