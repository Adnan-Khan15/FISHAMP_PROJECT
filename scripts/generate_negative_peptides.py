import pandas as pd
import random
from Bio.SeqUtils.ProtParam import ProteinAnalysis

# amino acids
amino_acids = "ACDEFGHIKLMNPQRSTVWY"

# load AMP dataset
amp_data = pd.read_csv("../data/amp_features.csv")

negative_sequences = []
features = []

print("Generating non-AMP peptides...")

for length in amp_data["length"]:

    # generate random peptide of same length
    seq = "".join(random.choice(amino_acids) for _ in range(int(length)))

    try:
        analysis = ProteinAnalysis(seq)

        charge = analysis.charge_at_pH(7)
        mw = analysis.molecular_weight()
        gravy = analysis.gravy()
        aromaticity = analysis.aromaticity()

        negative_sequences.append(seq)

        features.append([
            length,
            charge,
            mw,
            gravy,
            aromaticity
        ])

    except:
        continue

df = pd.DataFrame(features, columns=[
    "length",
    "charge",
    "molecular_weight",
    "hydrophobicity",
    "aromaticity"
])

df["sequence"] = negative_sequences
df["label"] = 0

df.to_csv("../data/non_amp_features.csv", index=False)

print("Non-AMP dataset created!")
print("Total samples:", len(df))
print(df.head())