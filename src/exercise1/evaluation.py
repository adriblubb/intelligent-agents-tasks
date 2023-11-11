# in the following ideas and code fragments are presented

# Task 6 describes 2 different evaluation functions
# first these two will be shown how to implement
# second: an alternative eval function will be presented


#EVAL FCT ONE

# evaluation ist bound to tracking of each agents' actions (and potentially the auctions steps itself)

# idea:
# which documents were missed, which were aquired
# how valuable are aquired docs against non-aquired

# main.py

# we create a list for each of the bidding agents, where the aquired docs are stored
# we could also use the corpus.txt by itself in the end and substract,
# but if we later want to compare which article got chosen against another this version will show more solid
# we could also work with timestamps, like in which iteration which article got chosen (later: over which?)

auctioneer.set("bought_articles", [])
auctioneer.set("bought_articles", [])


#agent_bidder.py

#START
localvar_bought_articles = []
# after announcement or declaration of auctions' step winner
localvar_bought_articles.append(title_of_currently_auctioned_article)

#END
# update agents boughts articles list for later comparison
self.agent.set("bought_articles", localvar_bought_articles)
available_articles = getSellList()

#iterate through all articles to sell in opposition to articles aquired -> list of articles not aquired
non_bought_articles = [ele for ele in available_articles if ele not in localvar_bought_articles]
# chosen 3 article input query for tfidf, already done?
query = []
#eval fct
score_of_own_docs = getTotalScore(self.agent.get("bought_articles"), query)
score_of_other_docs = getTotalScore(non_bought_articles, query)

#naive eval fct
print("score_of_own_docs: "+ str(score_of_own_docs))
print("score_of_other_docs: " + str(score_of_other_docs))

if score_of_own_docs > score_of_other_docs:
    print("Relatively, the score of the chosen docs is greater than the score of all other docs")
else:
    print("Relatively, the score of the not chosen docs is greater or equal than the score of the chosen ones")
#possibilities to improve the evaluation
print("by: " + str(getPercentage(score_of_own_docs,score_of_other_docs)))

#build average of 3 ( or x) different random queries on documents to put into perspective current run
comparison_scores = []
x = 3
averagescore = 0
for i in range(10):
    random_articles = []
    for j in range(x):
        random_articles.append(available_articles[random.randint(0, len(available_articles))])
    comparison_scores.append(getTotalScore(available_articles, random_articles))

for score in comparison_scores:
    averagescore = averagescore + score

averagescore = averagescore/ len(comparison_scores)

relationalscore_own = score_of_own_docs-averagescore
relationalscore_other = score_of_other_docs-averagescore

# same as above, but with elimination of  noise through averaging
if score_of_own_docs > score_of_other_docs:
    print("Relatively, the score of the chosen docs is greater than the score of all other docs")
else:
    print("Relatively, the score of the not chosen docs is greater or equal than the score of the chosen ones")
#possibilities to improve the evaluation
print("by: " + str(getPercentage(relationalscore_own,relationalscore_other)))




#percentage: return - ,xx if B is bigger A and + ,xx if A is bigger B
getPercentage(score_docA, score_docB):

    if score_docA >= score_docB:
        # A bigger B -> percentage would be 0,xx
        percentage = score_docB/score_docA
    else:
        # if B bigger A, then make it minus
        percentage = -(score_docA/score_docB)

    # maybe handler for correct inputs eg minus etc. possibly won't happen with tfidf
    return percentage
# helpers;
# have somewhere a fct which transfers txt to list-type
getSellList():
    with open("exercise1/data/sell.txt", "r") as acs:
        sellList = [line.rstrip() for line in acs]
    return sellList

# add up the scores of a given articles list and given query(e.g. set/list input articles on which tfidf is used)
getTotalScore(article_list, input_query):
    total_score = 0
    for ele in article_list:
         total_score = total_score + ele.tfidf(input_query)
    #normalize in regard to number of elements in list
    total_score = total_score/ len(article_list)
    return total_score


#EVAL FCT TWO

#main.py
auctioneer.set("bids_given_bidder1", [])
auctioneer.set("bids_given_bidder2", [])

#agent_bidder.py
bids_given_bidder1 = []
bids_given_bidder2 = []

# implement into each iteration, as auctioneer gets bids by agents:
current_bid_given = 0

bids_given_bidder1.append(current_bid_given)
bids_given_bidder2.append(current_bid_given)
# END
auctioneer.set("bids_given_bidder1", bids_given_bidder1)
auctioneer.set("bids_given_bidder2", bids_given_bidder2)

# loss count
overpay_bidder1 = 0
overpay_bidder2 = 0
#bidder 1 loss: calculating how much must not have been bidden
for i in range(len(bids_given_bidder1)):
    if bids_given_bidder1[i] > bids_given_bidder2[i]:
        # loss is the added up overpay
        overpay_bidder1 = overpay_bidder1 + ((bids_given_bidder1[i] - bids_given_bidder2[i]) - 1)
    else:
        print("no overpay")

# then in next iteration load from agent "bids_given_bidder1"; as memory so to speak

# improvement would be: calc how often or strong downsizing on bidding
# strategy can be made in respect to getting a high tfidf score

# now these functions could be integrated in TASK 5 also.
# if bidding by standard is always too high, then in next iteration bid 1 less.