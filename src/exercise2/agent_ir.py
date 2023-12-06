import os
import sys

from spade.agent import Agent
from spade.message import Message
from spade.behaviour import FSMBehaviour, State
from gensim import corpora, models
from gensim.models import CoherenceModel
import pyLDAvis.gensim_models as gensimvis
import pyLDAvis

import src.utils.functions as functions
import src.utils.helpfunctions as helpfunc

STATE_PREPARATION = "STATE_PREPARATION"
STATE_END = "STATE_END"


class IRStateMachine(FSMBehaviour):
    async def on_start(self):
        print("Start bidding (", self.agent.name, ")")

    async def on_end(self):
        print("End bidding (", self.agent.name, ")")
        await self.agent.stop()


class PreparationState(State):
    async def run(self):
        # Load corpus in the knowledge base of agent
        corpus_list = functions.read_file("./exercise2/data/corpus.txt")
        corpus_list = corpus_list.split("\n")

        self.agent.set("corpus_list", corpus_list[1:])

        # either 1) reading in or 2) creation of cache file of processed (tokenized+stemmed) wiki file
        # define path of cache, explicit for lda version
        cache_file_path = "./utils/cache/wiki_tokenized4lda.json"

        # 1) if cache exists, load it, skips creation
        if os.path.exists(cache_file_path):
            # load cache file into local database
            database_processed = functions.read_json_file(cache_file_path)
        # 2) if cache does not exist, create a new one to skip on next run + enhance performance
        else:
            # Load database..
            database = functions.read_json_file("./utils/cache/wikipedia.json")
            database_processed = {}
            # ..store tokens in knowledge base of agent..
            for key in database:
                database_processed[key] = helpfunc.preprocessing(database[key], True)
                #print(database_processed[key])
            # ...create the cache
            functions.write_json_file(cache_file_path, database_processed)
        # put data into agent
        self.agent.set("database_processed", database_processed)
        #  processed_docs_with_bigrams = [helpfunc.compute_bigrams(doc) for doc in database_processed]

        # below: test of functionality

        # Create a dictionary and a corpus
        dictionary = corpora.Dictionary(database_processed.values())
        print(dictionary)
        #test corpus
        #corpus = [dictionary.doc2bow(doc) for doc in dictionary]
        #print(corpus)

        # values of α, β, and K to find the best model

        # example values
        alpha_values = ['symmetric', 'asymmetric']
        beta_values = [0.01, 0.1, 0.5]
        num_topics_values = [5, 10, 15]

        best_model = None
        best_coherence = -1

        for alpha in alpha_values:
            for beta in beta_values:
                for num_topics in num_topics_values:
                    # LDA model training
                    lda_model = models.LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=15,
                                                alpha=alpha, eta=beta)
                    print("test")

                    # perplexity
                    perplexity = lda_model.log_perplexity(corpus)

                    # coherence score
                    coherence_model = CoherenceModel(model=lda_model, texts=database_processed, dictionary=dictionary,
                                                     coherence='c_v')
                    coherence_score = coherence_model.get_coherence()

                    # Print scores for each iteration
                    print(
                        f"Alpha: {alpha}, Beta: {beta}, Num Topics: {num_topics}, Perplexity: {perplexity}, Coherence: {coherence_score}")


                    # Check if the current model is better than the best one so far
                    if coherence_score > best_coherence:
                        best_model = lda_model
                        best_coherence = coherence_score
                        best_alpha = alpha
                        best_beta = beta
                        best_num_topics = num_topics
                        # Print the best hyperparameter values
                        print(f"Best Alpha: {best_alpha} Best Beta:  {best_beta} Best Num Topics: {best_num_topics}")


        #visualize
        # You can customize the visualization based on your preferences
        vis_data = gensimvis.prepare(best_model, corpus, dictionary)
        pyLDAvis.save_html(vis_data, 'lda_visualization.html')

        print("not gone into if")


        self.set_next_state(STATE_END)

class EndState(State):
    async def run(self):
       pass

class IRAgent(Agent):
    async def setup(self):
        irsm = IRStateMachine()

        # adding states
        irsm.add_state(name=STATE_PREPARATION, state=PreparationState(), initial=True)
        irsm.add_state(name=STATE_END, state=EndState())

        # declaring transitions of above states
        irsm.add_transition(source=STATE_PREPARATION, dest=STATE_END)


        self.add_behaviour(irsm)
