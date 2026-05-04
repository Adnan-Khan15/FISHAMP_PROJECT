import pandas as pd

MAP_FILE = "../microbiome_data/rohu_amp_genome_map.csv"
OUT_FILE = "../microbiome_data/rohu_amp_database.csv"

# Novelty thresholds
HIGH_IDENTITY   = 50.0   # >= 50% → Known (clearly homologous to a Rohu protein)
LOW_IDENTITY    = 50.0   # <  50% → Variant (low similarity, likely novel variant)

print("Building Rohu AMP Resource Database...", flush=True)
df = pd.read_csv(MAP_FILE)

# ── amp_id ────────────────────────────────────────────────────────────────
# already present

# ── blast_hit yes/no ──────────────────────────────────────────────────────
df["blast_hit"] = df["blast_hit_accession"].notna().map({True: "yes", False: "no"})

# ── matched_protein ───────────────────────────────────────────────────────
df["matched_protein"] = df["blast_hit_accession"].fillna("none")

# ── novelty_status ───────────────────────────────────────────────────────
def assign_novelty(row):
    if row["blast_hit"] == "no":
        return "Novel"
    if row["pident"] >= HIGH_IDENTITY:
        return "Known"
    return "Variant"

df["novelty_status"] = df.apply(assign_novelty, axis=1)

# ── final column selection & rename ──────────────────────────────────────
database = df[[
    "amp_id",
    "sequence",
    "length",
    "charge",
    "hydrophobicity",
    "amp_probability",
    "blast_hit",
    "matched_protein",
    "gene_name",
    "function",
    "novelty_status",
]].copy()

database.sort_values("amp_probability", ascending=False, inplace=True)
database.reset_index(drop=True, inplace=True)

database.to_csv(OUT_FILE, index=False)

# ── Summary ───────────────────────────────────────────────────────────────
total   = len(database)
mapped  = (database["blast_hit"] == "yes").sum()
novel   = (database["novelty_status"] == "Novel").sum()
known   = (database["novelty_status"] == "Known").sum()
variant = (database["novelty_status"] == "Variant").sum()

print(f"\nRohu AMP Database built: {OUT_FILE}")
print(f"  Total entries:    {total}")
print(f"  Mapped (BLAST):   {mapped} ({mapped/total*100:.1f}%)")
print(f"  Novel:            {novel}  ({novel/total*100:.1f}%)")
print(f"  Known (≥50% id):  {known}  ({known/total*100:.1f}%)")
print(f"  Variant (<50% id):{variant}  ({variant/total*100:.1f}%)")

print("\nTop 10 entries by AMP probability:")
top10 = database.head(10)
pd.set_option("display.max_colwidth", 50)
print(top10[[
    "amp_id","amp_probability","blast_hit","gene_name","function","novelty_status"
]].to_string(index=False))
