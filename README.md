# F1 Qualifying Predictor
 A neural net with the aim to predict qualifying performance (final position), based off of free practice lap times available online (can be found here: https://openf1.org/?python#introduction)

 Both Baseline models have not produced great results (sparse categorical accuracy of ~ 0.05 (equivalent to random))

 But this is due to the models being very barebone in their current state, as well as the times extracted perhaps being problematic (the z-score criteria for an outlier was arbitrarily set at 2, however this might not have removed all (or most) laps that were not considered "fast laps")

 In the future I will aim to implement:
1) Form indicators - for both driver and team (position in rankings, previous results etc...)
2) Tyre information that the lap time was generated from (soft tyre lap times will be more important)
3) Track data (different teams will perform differently depending on the properties of the circuit, will generate using PCA)

