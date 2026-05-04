import pandas as pd

DB_FILE  = "../microbiome_data/rohu_amp_database.csv"
MAP_FILE = "../microbiome_data/rohu_amp_genome_map.csv"

db  = pd.read_csv(DB_FILE)
mp  = pd.read_csv(MAP_FILE)

total    = len(db)
mapped   = (db["blast_hit"] == "yes").sum()
novel    = (db["novelty_status"] == "Novel").sum()
known    = (db["novelty_status"] == "Known").sum()
variant  = (db["novelty_status"] == "Variant").sum()

# AMPs that have a named gene (not N/A or LOC-only) from GFF
named_genes = db[
    (db["gene_name"] != "N/A") &
    (~db["gene_name"].str.startswith("LOC", na=True))
]["gene_name"].nunique()

sep = "=" * 60

print(sep)
print("  ROHU AMP RESOURCE DATABASE — ANALYSIS SUMMARY")
print(sep)
print(f"\n  Total candidate AMPs:          {total}")
print(f"  Mapped to Rohu proteome:       {mapped} ({mapped/total*100:.1f}%)")
print(f"  Novel (no BLAST hit):          {novel}  ({novel/total*100:.1f}%)")
print(f"  Known (≥50% identity):         {known}  ({known/total*100:.1f}%)")
print(f"  Variant (<50% identity):       {variant}  ({variant/total*100:.1f}%)")
print(f"  Distinct named genes hit:      {named_genes}")

# identity distribution for mapped hits
hits = mp[mp["pident"].notna()]
if len(hits):
    print(f"\n  Identity stats (BLAST hits):")
    print(f"    Mean % identity:   {hits['pident'].mean():.1f}%")
    print(f"    Max  % identity:   {hits['pident'].max():.1f}%")
    print(f"    Min  % identity:   {hits['pident'].min():.1f}%")

# top 10 by probability with gene annotations
print(f"\n{sep}")
print("  TOP 10 AMPs BY PROBABILITY WITH GENE ANNOTATIONS")
print(sep)
top10 = db.head(10)[
    ["amp_id","amp_probability","sequence","novelty_status","gene_name","function"]
].copy()
top10["sequence"] = top10["sequence"].str[:30] + "..."   # truncate for display
top10["function"] = top10["function"].str[:45]

for _, row in top10.iterrows():
    print(f"\n  {row['amp_id']} | prob={row['amp_probability']:.4f} | {row['novelty_status']}")
    print(f"    Seq:      {row['sequence']}")
    print(f"    Gene:     {row['gene_name']}")
    print(f"    Function: {row['function']}")

# Top function categories
print(f"\n{sep}")
print("  TOP 10 FUNCTIONAL CATEGORIES (mapped AMPs)")
print(sep)
func_counts = (
    db[db["blast_hit"] == "yes"]["function"]
    .str.replace(r"\s*\[Labeo rohita\]\s*$", "", regex=True)
    .str.replace(r"\bisoform X\d+\b", "", regex=True)
    .str.strip()
    .value_counts()
    .head(10)
)
for func, cnt in func_counts.items():
    print(f"  {cnt:4d}  {func[:60]}")

# Chromosomal distribution
chrom_counts = mp[mp["chromosome"] != "N/A"]["chromosome"].value_counts()
if len(chrom_counts):
    print(f"\n{sep}")
    print("  CHROMOSOMAL DISTRIBUTION OF MAPPED AMPs (top 10)")
    print(sep)
    for chrom, cnt in chrom_counts.head(10).items():
        label = chrom.replace("NC_", "Chr ").replace(".1", "")
        print(f"  {label:20s}  {cnt} AMPs")

print(f"\n{sep}")
print("  Output files:")
print(f"    microbiome_data/rohu_amp_genome_map.csv")
print(f"    microbiome_data/rohu_amp_database.csv")
print(sep)
