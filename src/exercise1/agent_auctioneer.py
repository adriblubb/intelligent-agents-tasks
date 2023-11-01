from spade.agent import Agent
from spade.message import Message
from spade.behaviour import FSMBehaviour, State
# adding go ahead with auction state
from src.utils.wikipedia import Wikipedia

STATE_START_AUCTION = "STATE_START_AUCTION"
STATE_WELCOME = "WELCOME_TO_AUCTION"
STATE_PREPARATION = "STATE_PREPARATION"
STATE_GIVE_OFFER = "STATE_GIVE_OFFER"
STATE_DECLARE_WINNER = "STATE_DECLARE_WINNER"
STATE_END = "STATE_END"
STATE_AUCTION = "STATE_AUCTION"



class AuctioneerStateMachine(FSMBehaviour):
    async def on_start(self):
        # load wiki articles into json
        pass
    async def on_end(self):
        await self.agent.stop()


class PreparationState(State):
    async def run(self):
        print("State: Preparation (Auctioner "+self.agent.get("name")+")")
        #for count, auctioneer in enumerate(self.agent.get("bidders_list")):
           # msg = Message(to=auctioneer)
           # msg.body = "This is the big auction."

            #str(Wikipedia(), "Alfa Romeo")

            #await self.send(msg)
        self.set_next_state(STATE_WELCOME)


class WelcomeToAuction(State):
    async def run(self):
       # temp_article = []
        #with self.agent.get("articles_agent_can_sell") as acs:
          #  temp_article.append(acs.readlines()[::1])
          #  print(temp_article)
          #  for i in temp_article:
           #     Wikipedia.get(Wikipedia(), temp_article[i])
        articles_agent_can_sell = self.agent.get("articles_agent_can_sell")
        example = articles_agent_can_sell[0]


        # loading the first 3 article titles
       # with self.agent.get("articles_agent_can_sell") as acs:
          #  example.append(acs[1])
            # load wiki articles into json


# are in list but with /n .. cancel out. load somwhere else
       #workin
       # print("hey"+ str(Wikipedia.get(Wikipedia(), example)))

        print("State: Welcome (Auctioner "+self.agent.get("name")+")")
        # officially offering articles to bidders
        for count, auctioneer in enumerate(self.agent.get("bidders_list")):
            msg = Message(to=auctioneer)
            msg.body = "Welcome to the biggest Wiki-Auction in the world. We have the following titles to Sell: " \
                       + example + ". You can bid on each of the articles based on your choice."
            await self.send(msg)
            self.set_next_state(STATE_START_AUCTION)

        #print("yo"+str(self.agent.get("articles_agent_can_sell")[1]))



class StartAuctionState(State):
    async def run(self):
        print("State: StartAuction (Auctioner "+self.agent.get("name")+")")

        articles_agent_can_sell = self.agent.get("articles_agent_can_sell")
        for article in articles_agent_can_sell:
         print(article)


         self.set_next_state(STATE_AUCTION)

# while articles are auctioned, state gets repeated
class AuctionStep(State):
    async def run(self):
        print("State: InAuction (Auctioner "+self.agent.get("name")+")")

        self.set_next_state(STATE_END)

# auction ends, when als articles are sold
class EndState(State):
    async def run(self):
        print("State: End (Auctioner "+self.agent.get("name")+")")



class AuctioneerAgent(Agent):
    async def setup(self):
        asm = AuctioneerStateMachine()

        asm.add_state(name=STATE_PREPARATION, state=PreparationState(), initial=True)
        asm.add_state(name=STATE_WELCOME, state=WelcomeToAuction())
        asm.add_state(name=STATE_START_AUCTION, state=StartAuctionState())
        asm.add_state(name=STATE_AUCTION, state=AuctionStep())
        asm.add_state(name=STATE_END, state=EndState())


        # adding transitions prep -> start/welcome -> how will auction work ->
        asm.add_transition(source=STATE_PREPARATION, dest=STATE_WELCOME)
        asm.add_transition(source=STATE_WELCOME, dest=STATE_START_AUCTION)
        asm.add_transition(source=STATE_START_AUCTION, dest=STATE_AUCTION)
        asm.add_transition(source=STATE_AUCTION, dest=STATE_AUCTION)
        asm.add_transition(source=STATE_AUCTION, dest=STATE_END)

        self.add_behaviour(asm)
