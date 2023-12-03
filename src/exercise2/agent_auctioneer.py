import os
import sys

from spade.agent import Agent
from spade.message import Message
from spade.behaviour import FSMBehaviour, State

import src.utils.functions as functions
import src.utils.helpfunctions as helpfunc

STATE_PREPARATION = "STATE_PREPARATION"
STATE_END = "STATE_END"


class AuctioneerStateMachine(FSMBehaviour):
    async def on_start(self):
        print("Start bidding (", self.agent.name, ")")

    async def on_end(self):
        print("End bidding (", self.agent.name, ")")
        await self.agent.stop()


class PreparationState(State):
    async def run(self):
        pass

class EndState(State):
    async def run(self):
       pass

class AuctioneerAgent(Agent):
    async def setup(self):
        asm = AuctioneerStateMachine()

        # adding states
        asm.add_state(name=STATE_PREPARATION, state=PreparationState(), initial=True)
        asm.add_state(name=STATE_END, state=EndState())

        # declaring transitions of above states
        asm.add_transition(source=STATE_PREPARATION, dest=STATE_END)


        self.add_behaviour(asm)
