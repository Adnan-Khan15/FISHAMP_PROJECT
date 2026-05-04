import pandas as pd

# Load your validated results file
df = pd.read_csv("../microbiome_data/candidate_amps.csv")

# Filter only predicted AMPs (high confidence)
amps = df[df['amp_probability'] > 0.8]

# Save to FASTA
with open("../microbiome_data/predicted_amps.fasta", "w") as f:
    for i, row in amps.iterrows():
        f.write(f">AMP_{i}\n{row['sequence']}\n")

print("FASTA file created: predicted_amps.fasta")
print("Total AMPs:", len(amps))
