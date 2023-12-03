import os
import sys

from spade.agent import Agent
from spade.message import Message
from spade.behaviour import FSMBehaviour, State

import src.utils.functions as functions
import src.utils.helpfunctions as helpfunc

STATE_PREPARATION = "STATE_PREPARATION"
STATE_END = "STATE_END"


class QuestionerStateMachine(FSMBehaviour):
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

class QuestionerAgent(Agent):
    async def setup(self):
        qsm = QuestionerStateMachine()

        # adding states
        qsm.add_state(name=STATE_PREPARATION, state=PreparationState(), initial=True)
        qsm.add_state(name=STATE_END, state=EndState())

        # declaring transitions of above states
        qsm.add_transition(source=STATE_PREPARATION, dest=STATE_END)


        self.add_behaviour(qsm)
