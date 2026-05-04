import pandas as pd
from Bio import SeqIO
from Bio.SeqUtils.ProtParam import ProteinAnalysis

# Path to FASTA file
fasta_file = "../data/natural_amps.fasta"

sequences = []
features = []

print("Reading FASTA file...")

for record in SeqIO.parse(fasta_file, "fasta"):

    seq = str(record.seq).strip()

    # Skip empty sequences
    if len(seq) == 0:
        continue

    try:
        analysis = ProteinAnalysis(seq)

        length = len(seq)
        charge = analysis.charge_at_pH(7)
        mw = analysis.molecular_weight()
        gravy = analysis.gravy()
        aromaticity = analysis.aromaticity()

        sequences.append(seq)

        features.append([
            length,
            charge,
            mw,
            gravy,
            aromaticity
        ])

    except Exception as e:
        # Skip sequences causing errors
        print(f"Skipping sequence: {record.id}")
        continue

print("Creating dataframe...")

df = pd.DataFrame(features, columns=[
    "length",
    "charge",
    "molecular_weight",
    "hydrophobicity",
    "aromaticity"
])

df["sequence"] = sequences
df["label"] = 1  # all sequences from APD are AMPs

output_file = "../data/amp_features.csv"

df.to_csv(output_file, index=False)

print("Feature extraction complete!")
print("Saved file:", output_file)
print("Total peptides processed:", len(df))
print(df.head())