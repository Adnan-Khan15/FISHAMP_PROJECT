import pandas as pd
from Bio import SeqIO
from Bio.SeqUtils.ProtParam import ProteinAnalysis

input_file = "../microbiome_data/microbiome_peptides.fasta"

features = []
sequences = []

for record in SeqIO.parse(input_file, "fasta"):
    seq = str(record.seq).replace("*", "")  # remove stop codon if present

    if len(seq) == 0:
        continue

    try:
        analysis = ProteinAnalysis(seq)

        features.append([
            len(seq),
            analysis.charge_at_pH(7),
            analysis.molecular_weight(),
            analysis.gravy(),
            analysis.aromaticity()
        ])

        sequences.append(seq)

    except:
        continue

df = pd.DataFrame(features, columns=[
    "length",
    "charge",
    "molecular_weight",
    "hydrophobicity",
    "aromaticity"
])

df["sequence"] = sequences

df.to_csv("../microbiome_data/microbiome_features.csv", index=False)

print("Feature extraction complete!")
print("Total usable peptides:", len(df))
