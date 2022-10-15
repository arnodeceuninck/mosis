import os

import numpy as np
import pandas as pd
from tqdm import tqdm

modelname = "ptr_pid_system"

# Setup the working directory
# Copy paste Tools > Options > Working Directory here
#path_to_exec_dir = "C:/Users/arnod/AppData/Local/Temp/OpenModelica/OMEdit"
path_to_exec_dir = "/private/var/folders/kr/mzglbsnx2sl3v4vsmfv_3vq40000gn/T/OpenModelica_dogukan/OMEdit"

os.chdir(f"{path_to_exec_dir}/{modelname}")

kp_values = np.arange(300, 351, 10)
ki_values = np.arange(0.5, 1.6, 0.1)
kd_values = np.arange(0, 71, 10)

combinations = np.array(np.meshgrid(kp_values, ki_values, kd_values)).T.reshape(-1, 3)


class MinCost:
    def __init__(self):
        self.cost = float("inf")
        self.ki = None
        self.kp = None
        self.kd = None


minCost = MinCost()

# Iterate over all possible value combinations, not really efficient, but there aren't that much iteration (+-15min)
# Use tqdm to display a progress bar
for combination in tqdm(combinations, desc="Testing combinations", total=combinations.shape[0]):
    kp = combination[0]
    ki = combination[1]
    kd = combination[2]

    os.system(f"./{modelname} -override Ki={ki},Kp={kp},Kd={kd}")
    #os.system(f"{modelname}.exe -override Ki={ki},Kp={kp},Kd={kd}")
    results_file = f"{modelname}_res.csv"

    df = pd.read_csv(results_file)

    # # Drop all results with
    # df = df.drop(df[df["costFunction.cost"] == 100000].index)

    # Don't know what we should do with the data
    # Currently calculate the entire cost by summing all values in the cost function
    # And the ki, kp, kd combination with the lowest cost will probably be the best

    cost_sum = df["costFunction.cost"].sum()

    if cost_sum < minCost.cost:
        tqdm.write(f"Found a lower cost: {cost_sum} < {minCost.cost}")
        minCost.ki = ki
        minCost.kd = kd
        minCost.kp = kp
        minCost.cost = cost_sum

    del df  # Weird solution proposed by Mateo to fix the cost value staying the same each iteration

print(f"Lowest cost of {minCost.cost} found with parameters ki={minCost.ki}, kd={minCost.kd}, kp={minCost.kp}")
