# Machine Learning-Based Discovery of Antimicrobial Peptides from Rohu Fish Gut Microbiome

A bioinformatics pipeline that combines metagenomics, machine learning, and genomic mapping to discover novel antimicrobial peptides (AMPs) from the gut microbiome of *Labeo rohita* (Rohu fish).

## Overview

Antimicrobial resistance is a growing global threat. This project mines the Rohu fish gut microbiome for novel AMPs using an XGBoost classifier trained on physicochemical features, then maps candidate peptides back to the Rohu reference genome to characterize their origins.

## Pipeline Summary

```
Raw reads (FASTQ) → Assembly → Protein prediction → Feature extraction
                                                            ↓
                                                   XGBoost classifier
                                                            ↓
                                            1226 candidate AMPs (prob > 0.8)
                                                            ↓
                                              BLASTP vs Rohu proteome
                                                            ↓
                                           rohu_amp_database.csv (final DB)
```

## Key Results

| Metric | Value |
|--------|-------|
| Model Accuracy | 82.5% |
| ROC-AUC | 0.902 |
| 5-fold CV AUC | 0.897 |
| Total AMP candidates | 1226 |
| Mapped to Rohu proteome | 758 (61.8%) |
| Novel (no BLAST hit) | 468 (38.2%) |
| Known (≥50% identity) | 84 (6.9%) |
| Mean BLAST identity | 39.3% |

## Repository Structure

```
fish_amp_project/
├── data/
│   ├── natural_amps.fasta          # 3306 known AMPs from APD3
│   ├── non_amp_uniprot.fasta       # Non-AMP negatives from UniProt
│   ├── balanced_amp_dataset.csv    # 6612-sample training dataset
│   ├── amp_features.csv
│   └── non_amp_features*.csv
├── scripts/
│   ├── train_amp_model.py          # XGBoost model training
│   ├── train_amp_model_proper.py   # Final model with proper validation
│   ├── extract_features.py         # Physicochemical feature extraction
│   ├── predict_microbiome_amps.py  # Run classifier on microbiome peptides
│   ├── extract_microbiome_peptides.py
│   ├── extract_microbiome_features.py
│   ├── fastq_to_fasta.py
│   ├── build_rohu_amp_database.py  # Build final AMP database
│   ├── map_to_genome.py            # BLASTP + GFF annotation
│   ├── shap_analysis.py            # Feature importance (SHAP)
│   ├── full_validation.py
│   ├── validate_results.py
│   ├── analysis_full.py
│   ├── analysis_summary.py
│   ├── generate_report.py
│   ├── prepare_balanced_dataset.py
│   ├── process_uniprot_negatives.py
│   ├── generate_negative_peptides.py
│   └── create_fasta_from_predictions.py
├── microbiome_data/
│   ├── candidate_amps.csv          # 1226 predicted AMPs with probabilities
│   ├── rohu_amp_database.csv       # Final annotated AMP resource
│   ├── rohu_amp_genome_map.csv     # AMP × BLAST hit × GFF annotation
│   ├── predicted_amps.fasta
│   ├── microbiome_peptides.fasta
│   ├── microbiome_features.csv
│   └── proteins.faa
├── rohu_protein_standard.fasta     # 47,455 Rohu XP_ proteins
├── blast_results.tsv               # BLASTP results (5411 hits)
└── models/                         # Saved model artifacts
```

## Methods

### Dataset
- **Positive**: 3306 AMPs from the Antimicrobial Peptide Database (APD3)
- **Negative**: 3306 non-AMPs from UniProt (balanced dataset)

### Features
Five physicochemical descriptors computed per peptide:
- Sequence length
- Net charge (pH 7)
- Molecular weight
- Hydrophobicity (GRAVY index)
- Aromaticity

### Model
XGBoost classifier with 5-fold cross-validation. Candidates selected at probability threshold > 0.8.

### Genomic Mapping
BLASTP against Rohu proteome (GCF_022985175.1, IGBB_LRoh.1.0) with relaxed parameters (BLOSUM45, e-value=10) to maximize detection of distant homologs. GFF annotations used to assign gene names and functions.

## Data Sources
- Metagenome reads: SRR33766029 (NCBI SRA)
- Rohu reference genome: GCF_022985175.1 (NCBI)
- AMP training data: Antimicrobial Peptide Database (APD3)
- Non-AMP data: UniProt Swiss-Prot

## Requirements

```bash
pip install xgboost scikit-learn biopython pandas numpy shap
# BLAST+ 2.17.0 required for genomic mapping
```

## Usage

```bash
# 1. Extract features
python scripts/extract_features.py

# 2. Train model
python scripts/train_amp_model_proper.py

# 3. Predict AMPs from microbiome
python scripts/predict_microbiome_amps.py

# 4. Map to genome and build database
python scripts/map_to_genome.py
python scripts/build_rohu_amp_database.py
```

## Output

**`microbiome_data/rohu_amp_database.csv`** — Final resource with columns:
`amp_id`, `sequence`, `length`, `charge`, `hydrophobicity`, `amp_probability`, `blast_hit`, `matched_protein`, `gene_name`, `function`, `novelty_status`

## Authors

Adnan Khan — Mini Project, 2026
