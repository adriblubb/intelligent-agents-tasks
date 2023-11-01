import sys
import os

from spade.agent import Agent
from spade.message import Message
from spade.behaviour import FSMBehaviour, State

STATE_PREPARATION = "STATE_PREPARATION"
STATE_AWAIT_WELCOME = "STATE_AWAIT_WELCOME"
# adding state which listens to the auctioneers input
STATE_AWAIT_OFFER = "STATE_AWAIT_OFFER"
# TODO -- add states
STATE_END = "STATE_END"

#print(os.open('./corpus.txt', 1))
#articles_agent_owns = open("exercise1/corpus.txt", "r")
#articles_agent_can_buy = open("exercise1/data/sell.txt", "r")
#articles_agent_has_in_full_text = []
#print(articles_agent_owns)
#with articles_agent_can_buy as acb:
   # print(acb.readlines()[1:3])
# create finite state machine agent
class BidderStateMachine(FSMBehaviour):
    async def on_start(self):
        pass

    async def on_end(self):
        await self.agent.stop()


# load corpus, model and three query document
class PreparationState(State):
    async def run(self):
        print("State: Preparation", "(Auctioneer " + self.agent.get("name") + ")")
        self.set_next_state(STATE_AWAIT_WELCOME)


class AwaitWelcomeState(State):
    async def run(self):

        print("State: AwaitWelcome, " + self.agent.get("name") + "'")
        self.set_next_state(STATE_AWAIT_OFFER)

class AwaitOfferState(State):
    async def run(self):
        msg = await self.receive(timeout=sys.float_info.max)
        print("State: AwaitAuction, Got message '" + msg.body + " " + self.agent.get("name") + "'")
        self.set_next_state(STATE_END)
class EndState(State):
    async def run(self):
        print("State: END", "(Auctioneer " + self.agent.get("name") + ")")


class BidderAgent(Agent):
    async def setup(self):
        bsm = BidderStateMachine()

        bsm.add_state(name=STATE_PREPARATION, state=PreparationState(), initial=True)
        # TODO -- add states
        # adding offer state to bidder state management
        bsm.add_state(name=STATE_AWAIT_WELCOME, state=AwaitWelcomeState())
        bsm.add_state(name=STATE_AWAIT_OFFER, state=AwaitOfferState())
        bsm.add_state(name=STATE_END, state=EndState())

        bsm.add_transition(source=STATE_PREPARATION, dest=STATE_AWAIT_WELCOME)
        bsm.add_transition(source=STATE_AWAIT_WELCOME, dest=STATE_AWAIT_OFFER)
        bsm.add_transition(source=STATE_AWAIT_OFFER, dest=STATE_END)

        self.add_behaviour(bsm)