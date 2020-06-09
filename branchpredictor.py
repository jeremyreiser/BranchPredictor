#Jeremy Reiser
#CSE4302 Project #2
from array import array

class BranchPredictor : 

    # the default constructor
    # call configure functions to do real initialization
    def __init__(self):
        self.mode = -1

    # constructor for tournament predictor
    # nbts is the number of bits in index to select a counter in tournament predictor
    # there should be (2 ** nbts) 2-bit counters
    def configure_tournament(self, nbts, m0, n0, k0, m1, n1, k1):
        self.mode = 2   # two because we are using two predictors
        self.verbose = 0
        self.nbts = nbts
        self.mask_selector_index = (1 << nbts) - 1  # the mask for the selector
        self.tcounters = [1]*(2**nbts)      #array to store tournament counter
        self.predictor0 = BranchPredictor()
        self.predictor0.configure(m0, n0, k0)
        self.predictor1 = BranchPredictor()
        self.predictor1.configure(m1, n1, k1)
        self.num_branches = 0
        self.num_taken = 0
        self.num_mispredictions = 0
        self.num_selected0 = 0              #initialize to zero

    # constructor for bimodal predictor
    def configure(self, m, n, k):
        self.mode = 1   # one because we are using one predictor
        self.verbose = 0
        self.m = m
        self.n = n
        self.k = k
        self.num_branches = 0
        self.num_taken = 0
        self.num_mispredictions = 0
        self.g_hist= 0     
        self.num_entries = 2**(k+m)
        self.counters = [1]*self.num_entries    # array to store counters       
        self.mask_ghr = (1 << m) - 1            # global history
        self.mask_addr = (1 << (k)) - 1       # mask for address bits 
        self.counter_max = 2**n                 # maximum value for counter

    def set_verbose(self, v):
        if (self.mode == 1):
            self.verbose = v
        elif (self.mode == 2):
            self.verbose = v
            self.predictor0.set_verbose(v)
            self.predictor1.set_verbose(v)

    # outcome is either 1 or 0.
    # return the prediction.
    # 1 for taken, 0 for not-taken
    def predict(self, addr, outcome):
        self.num_branches += 1
        self.num_taken += outcome
        prediction = 0
        if (self.mode == 1):
            ghr = self.g_hist & self.mask_ghr
            index = addr & self.mask_addr
            index = index << self.m
            index = index | ghr
            if (self.counters[index] <= (self.counter_max/2)):  #if counter is low
                prediction = 0                                #predict not taken
            elif (self.counters[index] > (self.counter_max/2)): #if counter high
                prediction = 1                                 #predict taken
            if(outcome == 0):           #decrement counter if not taken
                self.counters[index] = max([1, self.counters[index] - 1])
            elif (outcome == 1):        #increment counter if taken
                self.counters[index] = min([self.counter_max, self.counters[index] + 1])
            if (outcome != prediction): #counts mispredictions
                self.num_mispredictions = self.num_mispredictions + 1
            # update global history
            self.g_hist = (self.g_hist << 1) + outcome
        elif self.mode == 2:
            # Predict, update, return 
            prediction0 = self.predictor0.predict(addr, outcome) 
            prediction1 = self.predictor1.predict(addr, outcome)
            tindex = addr & self.mask_selector_index
            if(self.tcounters[tindex] <= 2):  #if counter low, use predictor 0
                self.num_selected0 = self.num_selected0 + 1
                if(prediction0 != outcome):     #if predict wrong, mispredict++
                    self.num_mispredictions = self.num_mispredictions + 1
            elif(self.tcounters[tindex] > 2):   #else, use predictor 1
                if(prediction1 != outcome):     #if predict wrong, mispredict++
                    self.num_mispredictions = self.num_mispredictions + 1
            if((prediction0 == outcome) and (prediction1 != outcome)):  #if P0 correct, P1 wrong, decrement counter
                self.tcounters[tindex] = max([1, self.tcounters[tindex] - 1])
            if((prediction0 != outcome) and (prediction1 == outcome)):  #if P1 correct, P0 wrong, increment counter
                self.tcounters[tindex] = min([self.tcounters[tindex] + 1, 4])
        else:
            raise Exception('The predictor is not configured correctly.')
        return prediction

    # report the statistics
    def report(self):
        if self.num_branches == 0:
            print("Total number of branches   = {}".format(self.num_branches))
            return
        if self.mode == 1:
            print("Total number of branches   = {}".format(self.num_branches))
            print("Number of taken branches   = {}".format(self.num_taken))
            print("Number of untaken branches = {}".format(self.num_branches - self.num_taken))
            print("Number of mispredictions   = {}".format(self.num_mispredictions))
            if (self.num_branches):
                print("Misprediction rate         = {:.2f}%".format(self.num_mispredictions/self.num_branches * 100))
        elif self.mode == 2:
            print("Predictor 0:")
            self.predictor0.report()
            print("\nPredictor 1:")
            self.predictor1.report()
            print("\n")
            if (self.num_branches):
                print("Misprediction rate         = {:.2f}%".format(self.num_mispredictions/self.num_branches * 100))
                print("Percentage of using 0      = {:.2f}%".format(self.num_selected0/self.num_branches * 100))


# Time spent on project
#  
# Friday, April 26th - 0.5 hours
# Downloaded sample code, fixed errors, got sample code running
#
# Saturday, April 27th - 5 hours
# Finished configure_tournament constructor, configure constructor, index calculation, branch prediction, counter updating,
# Finished correlating predictor, finished tournament predictor, finished tournament prediction selector,
# finished updating mispredictions for report function
#
# Monday, April 29th - 1.5 hours
# Fixed bug with correlating predictor where mispredictions was off (assumed there were 2**k entries, changed so that
# there are 2**(k+m) entries)