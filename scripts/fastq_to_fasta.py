from Bio import SeqIO

input_file = "../microbiome_data/SRR33766029.fastq"
output_file = "../microbiome_data/reads.fasta"

with open(output_file, "w") as out:
    for record in SeqIO.parse(input_file, "fastq"):
        SeqIO.write(record, out, "fasta")

print("Conversion complete!")