import pandas as pd
import re
from urllib.parse import unquote

BLAST_FILE   = "../blast_results.tsv"
GFF_FILE     = "../microbiome_data/rohu_genome.gff"
CANDS_FILE   = "../microbiome_data/candidate_amps.csv"
FASTA_FILE   = "../microbiome_data/predicted_amps.fasta"
OUT_FILE     = "../microbiome_data/rohu_amp_genome_map.csv"

BLAST_COLS = [
    "qseqid","sseqid","pident","length","mismatch","gapopen",
    "qstart","qend","sstart","send","evalue","bitscore","stitle"
]

# ── 1. Load BLAST – keep best hit per query (highest bitscore) ─────────────
print("Loading BLAST results...", flush=True)
blast = pd.read_csv(BLAST_FILE, sep="\t", header=None, names=BLAST_COLS)
blast_best = (
    blast.sort_values("bitscore", ascending=False)
         .groupby("qseqid", as_index=False)
         .first()
)
print(f"  Total hits: {len(blast)} | Unique AMPs with hits: {len(blast_best)}")

# ── 2. Parse GFF – CDS features only → protein_id → annotation ───────────
print("Parsing GFF annotation (CDS features)...", flush=True)
protein_map = {}   # protein_id → {gene, product, chrom, start, end, strand}

attr_re = re.compile(r'([^=;]+)=([^;]+)')

with open(GFF_FILE) as fh:
    for line in fh:
        if line.startswith("#"):
            continue
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 9 or parts[2] != "CDS":
            continue

        chrom, start, end, strand = parts[0], int(parts[3]), int(parts[4]), parts[6]
        attrs = dict(attr_re.findall(parts[8]))

        pid = attrs.get("protein_id", "")
        if not pid:
            continue

        if pid not in protein_map:
            gene    = attrs.get("gene", attrs.get("Name", "N/A"))
            product = unquote(attrs.get("product", "uncharacterized protein"))
            protein_map[pid] = {
                "gene_name": gene,
                "function":  product,
                "chromosome": chrom,
                "gene_start": start,
                "gene_end":   end,
                "strand":     strand,
            }
        else:
            # extend gene span if multi-exon
            protein_map[pid]["gene_start"] = min(protein_map[pid]["gene_start"], start)
            protein_map[pid]["gene_end"]   = max(protein_map[pid]["gene_end"],   end)

print(f"  Unique proteins indexed from GFF: {len(protein_map)}")

# ── 3. Load candidate AMP sequences (FASTA → dict) ───────────────────────
print("Loading AMP sequences from FASTA...", flush=True)
amp_seqs = {}
with open(FASTA_FILE) as fh:
    current_id = None
    for line in fh:
        line = line.strip()
        if line.startswith(">"):
            current_id = line[1:].split()[0]   # AMP_0, AMP_1 …
        elif current_id:
            amp_seqs[current_id] = line

# ── 4. Load candidate features ────────────────────────────────────────────
cands = pd.read_csv(CANDS_FILE)
# assign stable amp_id matching FASTA order
cands["amp_id"] = [f"AMP_{i}" for i in range(len(cands))]
cands["sequence"] = cands["amp_id"].map(amp_seqs)

# ── 5. Merge BLAST hits ───────────────────────────────────────────────────
print("Cross-referencing BLAST hits with GFF annotations...", flush=True)
merged = cands.merge(
    blast_best[["qseqid","sseqid","pident","evalue","bitscore","stitle"]],
    left_on="amp_id", right_on="qseqid", how="left"
)

# ── 6. Attach GFF gene info ───────────────────────────────────────────────
def lookup_gff(protein_id):
    if pd.isna(protein_id):
        return pd.Series({"gene_name":"N/A","function":"N/A",
                          "chromosome":"N/A","gene_start":None,
                          "gene_end":None,"strand":"N/A"})
    rec = protein_map.get(str(protein_id), {})
    return pd.Series({
        "gene_name":  rec.get("gene_name",  "N/A"),
        "function":   rec.get("function",   "N/A"),
        "chromosome": rec.get("chromosome", "N/A"),
        "gene_start": rec.get("gene_start", None),
        "gene_end":   rec.get("gene_end",   None),
        "strand":     rec.get("strand",     "N/A"),
    })

gff_cols = merged["sseqid"].apply(lookup_gff)
merged = pd.concat([merged, gff_cols], axis=1)

# fall back to stitle description when GFF function is N/A
mask = (merged["function"] == "N/A") & merged["stitle"].notna()
merged.loc[mask, "function"] = merged.loc[mask, "stitle"].str.replace(
    r"^XP_\S+\s+", "", regex=True
).str.replace(r"\s*\[Labeo rohita\]$", "", regex=True)

# ── 7. Final tidy output ──────────────────────────────────────────────────
out_cols = [
    "amp_id","sequence","length","charge","hydrophobicity","aromaticity",
    "amp_probability","sseqid","pident","evalue","bitscore",
    "gene_name","function","chromosome","gene_start","gene_end","strand"
]
out = merged[out_cols].rename(columns={"sseqid": "blast_hit_accession"})
out.to_csv(OUT_FILE, index=False)

print(f"\nSaved: {OUT_FILE}")
print(f"  Total AMPs:              {len(out)}")
print(f"  AMPs with BLAST hit:     {out['blast_hit_accession'].notna().sum()}")
print(f"  AMPs without hit:        {out['blast_hit_accession'].isna().sum()}")
print(f"  Hits mapped to GFF gene: {(out['gene_name'] != 'N/A').sum()}")
print("\nSample rows:")
print(out[out["blast_hit_accession"].notna()].head(5).to_string(index=False))
