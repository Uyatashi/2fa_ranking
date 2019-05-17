#!/usr/bin/env python
# coding: utf-8

# In[41]:


from simanneal import Annealer
from decimal import *
import pandas as pd
import random


#Simulated Annealing
class RankingWeightCalibration(Annealer):
    def __init__(self, state, target_ranking, scheme_names, step):
        self.target_ranking = target_ranking
        self.scheme_names = scheme_names
        self.step = step

        super(RankingWeightCalibration, self).__init__(state)
    
    #Adjust weights and try again
    def move(self):
        for dimension in range(len(self.state)):
            for i in range(len(self.state[dimension])):
                if random.random() >= 0.5:
                    self.state[dimension][i] = (self.state[dimension][i] + Decimal(self.step))%Decimal(1.0)
    
    #The loss value
    def energy(self):
        ranking = rankingFromWeights(self.state, self.target_ranking, self.scheme_names)
        return L(ranking, self.target_ranking)

def rankingFromWeights(W, target_ranking, scheme_names):
    ids = []
    for i in range(len(target_ranking)):
        ids.append(target_ranking[target_ranking["Scheme"] == scheme_names[i]].index[0])
    ranking = pd.DataFrame({"id": ids, "Scheme": scheme_names, "Score": getScores(W)}).sort_values(by=['Score'], ascending=False).reset_index(drop=True)
    return ranking
    
#Scoring functions
def score(W, scheme_index, dimension=0):
    usability_score = 0
    for i in range(len(W[0])):
        usability_score += W[0][i]*Decimal(u[i][scheme_index])
    
    if dimension==1:
        return usability_score
    
    deployability_score = 0
    for i in range(len(W[1])):
        deployability_score += W[1][i]*Decimal(d[i][scheme_index])
        
    if dimension==2:
        return deployability_score
        
    security_score = 0
    for i in range(len(W[2])):
        security_score += W[2][i]*Decimal(s[i][scheme_index])
    
    if dimension==3:
        return security_score
    
    score = usability_score + deployability_score + security_score
    #return [score, [usability_score, deployability_score, security_score]]
    return score

#Used for ranking the schemes
def getScores(W, dimension=0):
    scores = []
    for i in range(len(scheme_names)):
        scores.append(score(W, i, dimension))
    return scores


#Loss functions
def f(target_ranking, scheme_index):
    return len(target_ranking) - target_ranking[target_ranking['id'] == scheme_index].index[0]

def l(ranking, scheme_index):
    return len(ranking) - ranking[ranking['id'] == scheme_index].index[0]

def L(ranking, target_ranking):
    total_loss = 0
    for i in range(len(target_ranking)):
        loss = (f(target_ranking, i) - l(ranking, i))**2
        total_loss += loss
    return total_loss

#Randomizing the weight vector
def getRandomWeights():
    W = [[1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
    for i in range(USABILITY_BENEFIT_COUNT):
        W[0][i] = Decimal(random.random())
    for i in range(DEPLOYABILITY_BENEFIT_COUNT):
        W[1][i] = Decimal(random.random())
    for i in range(SECURITY_BENEFIT_COUNT):
        W[2][i] = Decimal(random.random())
    return W 


# In[42]:


#Settings
USABILITY_BENEFIT_COUNT = 8
DEPLOYABILITY_BENEFIT_COUNT = 6
SECURITY_BENEFIT_COUNT = 11

scheme_names = ["Password + SMS/VoiceCall",
                "Password + Push notification",
                "Password + OTP USB",
                "Password + UAF",
                "Password + U2F HID",
                "Password + U2F NFC/BLE",
                "Password + TOTP device",
                "Password + TOTP app"]


# Benefit satisfiabilility
# Usability
u = [[0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
     [1, 1, 1, 1, 1, 1, 1, 1],
     [0.5, 0.5, 0, 0.5, 0, 0, 0, 0.5],
     [0, 0, 0, 0, 0, 0, 0, 0],
     [1, 1, 0, 1, 0, 0, 1, 1],
     [0, 1, 1, 1, 1, 1, 0, 0],
     [0.5, 0.5, 0.5, 1, 1, 1, 0.5, 0.5],
     [1, 0.5, 0, 0, 0, 0, 0, 0.5]]

#Deployability
d = [[0, 1.0, 1.0, 1.0, 1.0, 1.0, 0, 0],
     [1.0, 1.0, 0, 1.0, 0, 0, 0, 1.0],
     [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
     [1.0, 1.0, 1.0, 1.0, 0, 0, 1.0, 1.0],
     [1.0, 1.0, 0, 0, 0, 1.0, 1.0, 1.0],
     [1.0, 1.0, 0, 1.0, 1.0, 1.0, 1.0, 1.0]]

#Security
s = [[1, 1, 1, 1, 1, 1, 1, 1],
     [0.5, 0.5, 1, 1, 1, 1, 1, 0.5],
     [1, 1, 1, 1, 1, 1, 1, 1],
     [0.5, 1, 1, 1, 1, 1, 0.5, 0.5],
     [0.5, 0.5, 0, 0.5, 1, 1, 0, 0],
     [1, 1, 1, 1, 1, 1, 1, 1],
     [1, 1, 1, 1, 1, 1, 1, 1],
     [1, 1, 1, 1, 1, 1, 1, 1],
     [0, 0.5, 0, 1, 0, 0, 0, 1],
     [1, 1, 1, 1, 1, 1, 1, 1],
     [1, 1, 1, 1, 1, 1, 1, 1]]

#The ground truth/target ranking
schemes_target_order = [3, 1, 0, 7, 5, 4, 6, 2]
target_ranking = pd.DataFrame({"id": [0,1,2,3,4,5,6,7], "Scheme": [scheme_names[i] for i in schemes_target_order]})


# In[43]:


state = getRandomWeights()
rwc = RankingWeightCalibration(state, target_ranking, scheme_names, 0.01)
rwc.steps = 1000
rwc.Tmax = 50
rwc.Tmin = 1
rwc.copy_strategy = "deepcopy"

e = -1
while(e != 0):
    state, e = rwc.anneal()
    
print "Model Weight Vector:\n", state
print "Ranking using the MWV:\n", rankingFromWeights(state, target_ranking, scheme_names)
print "Target ranking:\n", target_ranking

