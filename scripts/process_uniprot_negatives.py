import pandas as pd
import random
from Bio import SeqIO
from Bio.SeqUtils.ProtParam import ProteinAnalysis

# input FASTA from UniProt
fasta_file = "../data/non_amp_uniprot.fasta"

# output file
output_file = "../data/non_amp_features_real.csv"

# parameters
MIN_LEN = 10
MAX_LEN = 60
FRAGMENTS_PER_PROTEIN = 3   # how many peptides to sample from each protein

sequences = []
features = []

print("Reading UniProt FASTA and generating peptide fragments...")

for record in SeqIO.parse(fasta_file, "fasta"):

    protein_seq = str(record.seq).strip()
    protein_length = len(protein_seq)

    if protein_length < MIN_LEN:
        continue

    for _ in range(FRAGMENTS_PER_PROTEIN):

        # choose random peptide length
        frag_len = random.randint(MIN_LEN, min(MAX_LEN, protein_length))

        start = random.randint(0, protein_length - frag_len)
        peptide = protein_seq[start:start + frag_len]

        try:
            analysis = ProteinAnalysis(peptide)

            length = len(peptide)
            charge = analysis.charge_at_pH(7)
            mw = analysis.molecular_weight()
            gravy = analysis.gravy()
            aromaticity = analysis.aromaticity()

            sequences.append(peptide)

            features.append([
                length,
                charge,
                mw,
                gravy,
                aromaticity
            ])

        except:
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
df["label"] = 0

df.to_csv(output_file, index=False)

print("Finished!")
print("Saved:", output_file)
print("Total negative peptides:", len(df))
print(df.head())