from Bio import SeqIO

input_file = "../microbiome_data/proteins.faa"
output_file = "../microbiome_data/microbiome_peptides.fasta"

count = 0

with open(output_file, "w") as out:
    for record in SeqIO.parse(input_file, "fasta"):
        seq = str(record.seq)

        if 10 <= len(seq) <= 60:
            SeqIO.write(record, out, "fasta")
            count += 1

print("Peptides extracted:", count)