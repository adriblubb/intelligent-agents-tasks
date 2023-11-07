import sys
import re
import ast
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
        print("msg1State: AwaitStart. B: Got message '" + msg.body + " " + "B: "+ self.agent.get("name") + " has "+str(self.agent.get("initialBids"))+ " bids left.'")

        self.set_next_state(STATE_AWAIT_OFFER)


class AwaitOfferState(State):
    async def run(self):
        tokencount = 0
        iterator = 0

        msg2 = await self.receive(timeout=sys.float_info.max)
        input_string = str(msg2)
        # Define a regular expression pattern to match the list part
        pattern = r"\[.*?\]"

        # Find the first match of the pattern in the string
        match = re.search(pattern, input_string)

        if match:
            # Extract the matched substring (the list)
            extracted_list = match.group(0)
            # Remove leading and trailing spaces and newlines
            extracted_list = extracted_list.strip()

            # Now, you have the list as a string, and you can convert it to an actual list
            result_list = eval(extracted_list)
            for token in result_list:
                if result_list[iterator] == self.agent.get("query"):
                    tokencount = tokencount + 1
                iterator = iterator + 1
            print("State: AwaitOfferState B: Got tokens '" + str(tokencount) + " " + "B: " + self.agent.get("name"))
           # print("State: AwaitOfferState. B: " + self.agent.get("name"))
        else:
            print("List not found in the input string")


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