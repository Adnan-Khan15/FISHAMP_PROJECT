import pandas as pd

amp = pd.read_csv("../data/amp_features.csv")
candidates = pd.read_csv("../microbiome_data/candidate_amps.csv")

print("Known AMPs:", len(amp))
print("Predicted AMPs:", len(candidates))
print("\n--- Candidate Summary ---")
print(candidates.describe())