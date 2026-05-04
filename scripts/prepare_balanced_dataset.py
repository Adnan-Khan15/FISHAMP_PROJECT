import pandas as pd

# load datasets
amp = pd.read_csv("../data/amp_features.csv")
non_amp = pd.read_csv("../data/non_amp_features_real.csv")

print("AMP samples:", len(amp))
print("Non-AMP samples:", len(non_amp))

# sample negatives equal to positives
non_amp_sampled = non_amp.sample(n=len(amp), random_state=42)

print("Sampled non-AMP:", len(non_amp_sampled))

# combine
dataset = pd.concat([amp, non_amp_sampled], ignore_index=True)

# shuffle dataset
dataset = dataset.sample(frac=1, random_state=42).reset_index(drop=True)

# save dataset
dataset.to_csv("../data/balanced_amp_dataset.csv", index=False)

print("Balanced dataset created!")
print("Total samples:", len(dataset))
print(dataset.head())