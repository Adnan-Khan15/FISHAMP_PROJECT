#!/usr/bin/env python3
"""
Generate Mini Project Report:
'Machine Learning-Based Discovery of Antimicrobial Peptides from
 Rohu (Labeo rohita) Microbiome'
C.R.C.E., Bandra (W), Mumbai — Semester V, 2024-2025
"""
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ═══════════════════════════════════════════════════════════
#  CONSTANTS
# ═══════════════════════════════════════════════════════════
FONT         = "Times New Roman"
SZ_BODY      = 12
SZ_CHAPTER   = 14
SZ_SECTION   = 12
LS_BODY      = 360   # 1.5× in twips (240 = 1.0×)
LS_SINGLE    = 240
LS_ONEFIVE   = 360

# ═══════════════════════════════════════════════════════════
#  LOW-LEVEL HELPERS
# ═══════════════════════════════════════════════════════════
def _set_spacing_xml(p, line_twips=LS_BODY, before_pt=0, after_pt=6):
    pPr = p._p.get_or_add_pPr()
    for el in pPr.findall(qn('w:spacing')):
        pPr.remove(el)
    sp = OxmlElement('w:spacing')
    sp.set(qn('w:before'), str(int(before_pt * 20)))  # 1pt = 20 twips
    sp.set(qn('w:after'),  str(int(after_pt  * 20)))
    sp.set(qn('w:line'),   str(line_twips))
    sp.set(qn('w:lineRule'), 'auto')
    pPr.append(sp)

def _rf(r, size=SZ_BODY, bold=False, italic=False, name=FONT):
    r.font.name  = name
    r.font.size  = Pt(size)
    r.font.bold  = bold
    r.font.italic= italic


def add_p(doc, text='', align=WD_ALIGN_PARAGRAPH.JUSTIFY,
          sz=SZ_BODY, bold=False, italic=False,
          before=0, after=6, ls=LS_BODY):
    p = doc.add_paragraph()
    p.alignment = align
    _set_spacing_xml(p, ls, before, after)
    if text:
        r = p.add_run(text)
        _rf(r, sz, bold, italic)
    return p

def page_break(doc):
    doc.add_page_break()

def chapter_head(doc, n, title):
    add_p(doc, f'Chapter {n}', WD_ALIGN_PARAGRAPH.CENTER,
          SZ_CHAPTER, True, before=0, after=0, ls=LS_SINGLE)
    add_p(doc, title, WD_ALIGN_PARAGRAPH.CENTER,
          SZ_CHAPTER, True, before=0, after=14, ls=LS_SINGLE)

def section_head(doc, text, before=12, after=6):
    add_p(doc, text, WD_ALIGN_PARAGRAPH.LEFT,
          SZ_SECTION, True, before=before, after=after, ls=LS_SINGLE)

def body(doc, text, before=0, after=6):
    add_p(doc, text, WD_ALIGN_PARAGRAPH.JUSTIFY,
          SZ_BODY, False, before=before, after=after, ls=LS_BODY)

def add_bullet(doc, text, before=0, after=3):
    p = doc.add_paragraph(style='List Bullet')
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    _set_spacing_xml(p, LS_BODY, before, after)
    r = p.add_run(text)
    _rf(r, SZ_BODY)

def add_number(doc, text, before=0, after=3):
    p = doc.add_paragraph(style='List Number')
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    _set_spacing_xml(p, LS_BODY, before, after)
    r = p.add_run(text)
    _rf(r, SZ_BODY)

def add_code(doc, text):
    p = doc.add_paragraph()
    _set_spacing_xml(p, LS_SINGLE, 0, 0)
    r = p.add_run(text)
    _rf(r, 10, name='Courier New')

def tbl_cap(doc, text, before=12):
    add_p(doc, text, WD_ALIGN_PARAGRAPH.CENTER,
          SZ_BODY, True, before=before, after=4, ls=LS_SINGLE)

def fig_cap(doc, text):
    add_p(doc, text, WD_ALIGN_PARAGRAPH.CENTER,
          SZ_BODY, italic=True, before=4, after=12, ls=LS_SINGLE)

def roman_num(doc, num):
    add_p(doc, num, WD_ALIGN_PARAGRAPH.RIGHT,
          SZ_BODY, before=12, after=0, ls=LS_SINGLE)

def add_footer_page_num(section):
    footer = section.footer
    for p in footer.paragraphs:
        p._element.getparent().remove(p._element)
    p = footer.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_spacing_xml(p, LS_SINGLE, 0, 0)
    r = p.add_run()
    _rf(r, SZ_BODY)
    fld1 = OxmlElement('w:fldChar')
    fld1.set(qn('w:fldCharType'), 'begin')
    inst = OxmlElement('w:instrText')
    inst.set(qn('xml:space'), 'preserve')
    inst.text = ' PAGE '
    fld2 = OxmlElement('w:fldChar')
    fld2.set(qn('w:fldCharType'), 'end')
    r._r.append(fld1)
    r._r.append(inst)
    r._r.append(fld2)

def make_table(doc, hdrs, rows, col_widths=None, hdr_sz=10, row_sz=9):
    t = doc.add_table(rows=1 + len(rows), cols=len(hdrs))
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    # header row
    for i, h in enumerate(hdrs):
        c = t.rows[0].cells[i]
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _set_spacing_xml(p, LS_SINGLE, 2, 2)
        r = p.add_run(h)
        _rf(r, hdr_sz, True)
        # header cell shading
        tc = c._tc
        tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), 'D9D9D9')
        tcPr.append(shd)
    # data rows
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            c = t.rows[ri + 1].cells[ci]
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            _set_spacing_xml(p, LS_SINGLE, 2, 2)
            r = p.add_run(str(val))
            _rf(r, row_sz)
    # column widths
    if col_widths:
        for ci, w in enumerate(col_widths):
            for row in t.rows:
                row.cells[ci].width = Inches(w)
    return t


# ═══════════════════════════════════════════════════════════
#  DOCUMENT SETUP
# ═══════════════════════════════════════════════════════════
def setup_doc():
    doc = Document()
    # Remove the default empty paragraph
    for p in list(doc.paragraphs):
        p._element.getparent().remove(p._element)
    sec = doc.sections[0]
    sec.page_width    = Inches(8.27)
    sec.page_height   = Inches(11.69)
    sec.top_margin    = Inches(1.0)
    sec.bottom_margin = Inches(1.0)
    sec.left_margin   = Inches(1.25)
    sec.right_margin  = Inches(1.0)
    return doc


# ═══════════════════════════════════════════════════════════
#  COVER PAGE
# ═══════════════════════════════════════════════════════════
def cover_page(doc):
    add_p(doc, '', before=0, after=0, ls=LS_SINGLE)  # top spacer

    add_p(doc, 'Fr. Conceicao Rodrigues College of Engineering',
          WD_ALIGN_PARAGRAPH.CENTER, 14, True, before=0, after=0, ls=LS_SINGLE)
    add_p(doc, '(Affiliated to University of Mumbai)',
          WD_ALIGN_PARAGRAPH.CENTER, 12, False, before=0, after=0, ls=LS_SINGLE)
    add_p(doc, 'Bandra (W), Mumbai - 400 050',
          WD_ALIGN_PARAGRAPH.CENTER, 12, False, before=0, after=20, ls=LS_SINGLE)

    add_p(doc,
          'Machine Learning-Based Discovery of Antimicrobial Peptides from '
          'Rohu (Labeo rohita) Microbiome',
          WD_ALIGN_PARAGRAPH.CENTER, 16, True, before=0, after=20, ls=LS_ONEFIFE_or_single())

    add_p(doc, 'A Mini-Project Report Submitted',
          WD_ALIGN_PARAGRAPH.CENTER, SZ_BODY, before=0, after=0, ls=LS_SINGLE)
    add_p(doc, 'For', WD_ALIGN_PARAGRAPH.CENTER, SZ_BODY, before=0, after=0, ls=LS_SINGLE)
    add_p(doc, 'Partial Fulfilment of the Requirements of the',
          WD_ALIGN_PARAGRAPH.CENTER, SZ_BODY, before=0, after=0, ls=LS_SINGLE)
    add_p(doc, 'Degree of    Bachelor of Engineering',
          WD_ALIGN_PARAGRAPH.CENTER, SZ_BODY, before=0, after=0, ls=LS_SINGLE)
    add_p(doc, 'In', WD_ALIGN_PARAGRAPH.CENTER, SZ_BODY, before=0, after=0, ls=LS_SINGLE)
    add_p(doc, 'COMPUTER ENGINEERING',
          WD_ALIGN_PARAGRAPH.CENTER, SZ_BODY, True, before=0, after=0, ls=LS_SINGLE)
    add_p(doc, '(Semester V)', WD_ALIGN_PARAGRAPH.CENTER, SZ_BODY,
          before=0, after=18, ls=LS_SINGLE)

    add_p(doc, 'By', WD_ALIGN_PARAGRAPH.CENTER, SZ_BODY, before=0, after=6, ls=LS_SINGLE)
    add_p(doc, 'Adnan Khan (10254)',
          WD_ALIGN_PARAGRAPH.CENTER, SZ_BODY, before=0, after=0, ls=LS_SINGLE)
    add_p(doc, 'Kshant Carvalho (10232)',
          WD_ALIGN_PARAGRAPH.CENTER, SZ_BODY, before=0, after=0, ls=LS_SINGLE)
    add_p(doc, 'Vishwaa Bhende (10230)',
          WD_ALIGN_PARAGRAPH.CENTER, SZ_BODY, before=0, after=18, ls=LS_SINGLE)

    add_p(doc, 'Under the guidance of',
          WD_ALIGN_PARAGRAPH.CENTER, SZ_BODY, before=0, after=6, ls=LS_SINGLE)
    add_p(doc, 'Prof. Ashwini Pansare',
          WD_ALIGN_PARAGRAPH.CENTER, SZ_BODY, True, before=0, after=0, ls=LS_SINGLE)
    add_p(doc, 'Department of Computer Engineering',
          WD_ALIGN_PARAGRAPH.CENTER, SZ_BODY, before=0, after=24, ls=LS_SINGLE)

    add_p(doc, 'Department of Computer Engineering',
          WD_ALIGN_PARAGRAPH.CENTER, SZ_BODY, True, before=0, after=0, ls=LS_SINGLE)
    add_p(doc, 'Fr. Conceicao Rodrigues College of Engineering',
          WD_ALIGN_PARAGRAPH.CENTER, SZ_BODY, True, before=0, after=0, ls=LS_SINGLE)
    add_p(doc, 'Bandra (W), Mumbai - 400 050',
          WD_ALIGN_PARAGRAPH.CENTER, SZ_BODY, before=0, after=12, ls=LS_SINGLE)

    add_p(doc, '2024 - 2025',
          WD_ALIGN_PARAGRAPH.CENTER, SZ_BODY, True, before=0, after=0, ls=LS_SINGLE)


def LS_ONEFIFE_or_single():
    return LS_ONEFIVE


# ═══════════════════════════════════════════════════════════
#  CERTIFICATE
# ═══════════════════════════════════════════════════════════
def certificate(doc):
    add_p(doc, '', before=0, after=0)
    add_p(doc, 'Fr. Conceicao Rodrigues College of Engineering',
          WD_ALIGN_PARAGRAPH.CENTER, 14, True, before=0, after=0, ls=LS_SINGLE)
    add_p(doc, 'Department of Computer Engineering',
          WD_ALIGN_PARAGRAPH.CENTER, SZ_BODY, before=0, after=0, ls=LS_SINGLE)
    add_p(doc, 'Bandra (W), Mumbai - 400 050',
          WD_ALIGN_PARAGRAPH.CENTER, SZ_BODY, before=0, after=20, ls=LS_SINGLE)

    add_p(doc, 'CERTIFICATE', WD_ALIGN_PARAGRAPH.CENTER, 14, True,
          before=0, after=12, ls=LS_SINGLE)

    body(doc,
         'This is to certify that the mini-project entitled "Machine Learning-Based '
         'Discovery of Antimicrobial Peptides from Rohu (Labeo rohita) Microbiome" is a '
         'bonafide work of Adnan Khan (10254), Kshant Carvalho (10232), and Vishwaa Bhende '
         '(10230) submitted in partial fulfilment of the requirements for the Degree of '
         'Bachelor of Engineering in Computer Engineering (Semester V) of the University of '
         'Mumbai, during the academic year 2024-2025. They have completed this project under '
         'the guidance of Prof. Ashwini Pansare.')

    add_p(doc, '', before=24, after=0)

    t = doc.add_table(rows=2, cols=2)
    t.style = 'Table Grid'
    # Remove borders
    for row in t.rows:
        for cell in row.cells:
            tc = cell._tc
            tcPr = tc.get_or_add_tcPr()
            tcBorders = OxmlElement('w:tcBorders')
            for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
                tag = OxmlElement(f'w:{edge}')
                tag.set(qn('w:val'), 'none')
                tcBorders.append(tag)
            tcPr.append(tcBorders)

    for ri, (lbl, val) in enumerate([
        ('Prof. Ashwini Pansare', 'Dr. Sujata Deshmukh'),
        ('Project Guide', 'HOD, Computer Engineering')
    ]):
        for ci, txt in enumerate([lbl, val]):
            c = t.rows[ri].cells[ci]
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            _set_spacing_xml(p, LS_SINGLE, 4, 4)
            r = p.add_run(txt)
            _rf(r, SZ_BODY, ri == 0)

    add_p(doc, '', before=30, after=0)
    add_p(doc, 'Date: ___________                    Place: Mumbai',
          WD_ALIGN_PARAGRAPH.LEFT, SZ_BODY, before=0, after=0, ls=LS_SINGLE)
    roman_num(doc, 'i')


# ═══════════════════════════════════════════════════════════
#  APPROVAL SHEET
# ═══════════════════════════════════════════════════════════
def approval_sheet(doc):
    add_p(doc, 'Approval Sheet', WD_ALIGN_PARAGRAPH.CENTER, 14, True,
          before=0, after=8, ls=LS_SINGLE)
    add_p(doc, 'Mini Project Report Approval for T.E. (Semester-V)',
          WD_ALIGN_PARAGRAPH.CENTER, SZ_BODY, True,
          before=0, after=12, ls=LS_SINGLE)

    body(doc,
         'This mini-project report entitled "Machine Learning-Based Discovery of '
         'Antimicrobial Peptides from Rohu (Labeo rohita) Microbiome" submitted by '
         'Adnan Khan (10254), Kshant Carvalho (10232), and Vishwaa Bhende (10230) is '
         'approved for the degree of Bachelor of Engineering in Computer Engineering of the '
         'University of Mumbai.')

    add_p(doc, '', before=20, after=0)
    add_p(doc, 'Examiner 1.  ____________________________',
          WD_ALIGN_PARAGRAPH.LEFT, SZ_BODY, before=0, after=8, ls=LS_SINGLE)
    add_p(doc, 'Examiner 2.  ____________________________',
          WD_ALIGN_PARAGRAPH.LEFT, SZ_BODY, before=0, after=30, ls=LS_SINGLE)
    add_p(doc, 'Date:  ___________',
          WD_ALIGN_PARAGRAPH.LEFT, SZ_BODY, before=0, after=4, ls=LS_SINGLE)
    add_p(doc, 'Place: Mumbai',
          WD_ALIGN_PARAGRAPH.LEFT, SZ_BODY, before=0, after=0, ls=LS_SINGLE)
    roman_num(doc, 'ii')


# ═══════════════════════════════════════════════════════════
#  DECLARATION
# ═══════════════════════════════════════════════════════════
def declaration(doc):
    add_p(doc, 'Declaration', WD_ALIGN_PARAGRAPH.CENTER, 14, True,
          before=0, after=12, ls=LS_SINGLE)

    body(doc,
         "We declare that this written submission represents our ideas in our own words and "
         "where others' ideas or words have been included, we have adequately cited and "
         "referenced the original sources. We also declare that we have adhered to all "
         "principles of academic honesty and integrity and have not misrepresented or "
         "fabricated or falsified any idea/data/fact/source in this submission. We "
         "understand that any violation of the above will be cause for disciplinary action "
         "by the Institute and can also evoke penal action from the sources which have thus "
         "not been properly cited or from whom proper permission has not been taken when "
         "needed.")

    add_p(doc, '', before=30, after=0)
    for name_roll in [
        'Adnan Khan (10254)             Sign: ___________',
        'Kshant Carvalho (10232)        Sign: ___________',
        'Vishwaa Bhende (10230)         Sign: ___________',
    ]:
        add_p(doc, name_roll, WD_ALIGN_PARAGRAPH.LEFT, SZ_BODY,
              before=0, after=10, ls=LS_SINGLE)

    add_p(doc, '', before=12, after=0)
    add_p(doc, 'Date: ___________',
          WD_ALIGN_PARAGRAPH.LEFT, SZ_BODY, before=0, after=0, ls=LS_SINGLE)
    roman_num(doc, 'iii')


# ═══════════════════════════════════════════════════════════
#  ABSTRACT
# ═══════════════════════════════════════════════════════════
def abstract(doc):
    add_p(doc, 'Abstract', WD_ALIGN_PARAGRAPH.CENTER, 14, True,
          before=0, after=12, ls=LS_SINGLE)

    body(doc,
         'Antimicrobial resistance (AMR) is one of the most critical public health '
         'challenges of the 21st century, rendering conventional antibiotics ineffective '
         'against a growing number of bacterial pathogens. Aquaculture, which contributes '
         'significantly to global food security, is particularly vulnerable to bacterial '
         'infections, especially in high-value species such as Rohu (Labeo rohita), a '
         'freshwater carp of major economic importance in South Asia. Antimicrobial peptides '
         '(AMPs) are naturally occurring short peptides that disrupt bacterial membranes '
         'through physicochemical mechanisms, making them promising candidates for '
         'next-generation therapeutics resistant to conventional resistance mechanisms.')

    body(doc,
         'This project presents a fully computational, machine-learning-based pipeline for '
         'the systematic discovery of novel AMPs from the gut microbiome of Labeo rohita. '
         'A balanced binary classification dataset was constructed by combining 3,306 '
         'natural AMPs from the Antimicrobial Peptide Database version 3 (APD3) with 3,306 '
         'non-AMP peptide fragments extracted from UniProt, yielding 6,612 labelled '
         'sequences. Five physicochemical features — sequence length, net charge at pH 7, '
         'molecular weight, hydrophobicity (GRAVY index), and aromaticity — were extracted '
         'using BioPython and used to train four classical machine learning classifiers: '
         'XGBoost, Random Forest, Support Vector Machine, and Logistic Regression. XGBoost '
         'achieved the highest performance, with an accuracy of 82.5%, a ROC-AUC of 0.902, '
         'and a 5-fold cross-validation AUC of 0.897, and was selected as the final model.')

    body(doc,
         'SHapley Additive exPlanations (SHAP) analysis revealed that net charge '
         '(importance score 0.279) was the most influential feature for AMP prediction, '
         'followed by hydrophobicity (0.224), sequence length (0.217), aromaticity (0.170), '
         'and molecular weight (0.108). Rohu gut microbiome raw sequencing data '
         '(NCBI SRA accession SRR33766029) was assembled using SPAdes, translated to '
         'protein sequences with Prodigal, and screened using the trained XGBoost model. '
         'A total of 1,226 high-confidence candidate AMPs (AMP probability > 0.80) were '
         'identified from the microbiome proteome.')

    body(doc,
         'To functionally annotate these candidates, a relaxed BLASTP search '
         '(BLOSUM45, e-value threshold 10) was conducted against 47,455 Rohu reference '
         'proteins (GCF_022985175.1, IGBB_LRoh.1.0), yielding 5,411 hits spanning 758 '
         'unique AMPs. BLAST results were cross-referenced with the Rohu genome GFF '
         'annotation file to extract gene names, product descriptions, and chromosomal '
         'coordinates. The final Rohu AMP Resource Database classifies all 1,226 candidates '
         'as Novel (468, 38.2%), Known (84, 6.9%), or Variant (674, 55.0%) based on BLAST '
         'identity thresholds. This resource constitutes the first species-specific '
         'computational AMP database for Labeo rohita and lays the groundwork for '
         'targeted experimental validation and sustainable aquaculture therapeutics.')

    add_p(doc, '', before=6, after=4)
    add_p(doc, 'Keywords:', WD_ALIGN_PARAGRAPH.LEFT, SZ_BODY, True,
          before=0, after=0, ls=LS_SINGLE)
    body(doc,
         'Antimicrobial peptides, machine learning, XGBoost, SHAP, Labeo rohita, '
         'microbiome, BLAST, aquaculture, AMR, bioinformatics, APD3, genomic annotation')
    roman_num(doc, 'iv')


# ═══════════════════════════════════════════════════════════
#  ACKNOWLEDGMENTS
# ═══════════════════════════════════════════════════════════
def acknowledgments(doc):
    add_p(doc, 'Acknowledgments', WD_ALIGN_PARAGRAPH.CENTER, 14, True,
          before=0, after=12, ls=LS_SINGLE)

    body(doc,
         'We take great pleasure in presenting this mini-project report on '
         '"Machine Learning-Based Discovery of Antimicrobial Peptides from Rohu '
         '(Labeo rohita) Microbiome." We take this opportunity to express our sincere '
         'gratitude to all individuals who guided and supported us throughout this project.')

    body(doc,
         'We are deeply grateful to our project guide, Prof. Ashwini Pansare, Department of '
         'Computer Engineering, C.R.C.E., for her invaluable guidance, consistent '
         'motivation, constructive feedback, and for introducing us to the exciting '
         'intersection of machine learning and bioinformatics. Her expertise and dedication '
         'shaped the direction and quality of this work.')

    body(doc,
         'We sincerely thank Dr. Sujata Deshmukh, Head of the Department of Computer '
         'Engineering, and the Principal and management of Fr. Conceicao Rodrigues College '
         'of Engineering, Mumbai, for providing the necessary infrastructure, computational '
         'resources, and a stimulating academic environment that made this research possible.')

    body(doc,
         'We also thank the open-source community behind Python, BioPython, XGBoost, SHAP, '
         'scikit-learn, and NCBI tools, whose freely available software made this entirely '
         'computational project feasible. The APD3, UniProt, and NCBI SRA databases '
         'provided essential biological data without which this project would not have been '
         'possible.')

    body(doc,
         'Finally, we are thankful to our family and friends for their unwavering support '
         'and encouragement throughout this project. We also thank all non-teaching staff '
         'for their valuable support in completing our project.')

    add_p(doc, '', before=18, after=0)
    add_p(doc, 'Date: ___________',
          WD_ALIGN_PARAGRAPH.LEFT, SZ_BODY, before=0, after=12, ls=LS_SINGLE)
    for name in ['Adnan Khan (10254)', 'Kshant Carvalho (10232)', 'Vishwaa Bhende (10230)']:
        add_p(doc, name, WD_ALIGN_PARAGRAPH.LEFT, SZ_BODY, before=0, after=4, ls=LS_SINGLE)
    roman_num(doc, 'v')


# ═══════════════════════════════════════════════════════════
#  TABLE OF CONTENTS
# ═══════════════════════════════════════════════════════════
def toc(doc):
    add_p(doc, 'Table of Contents', WD_ALIGN_PARAGRAPH.CENTER, 14, True,
          before=0, after=12, ls=LS_SINGLE)

    entries = [
        ('Certificate', 'i'),
        ('Approval Sheet', 'ii'),
        ('Declaration', 'iii'),
        ('Abstract', 'iv'),
        ('Acknowledgments', 'v'),
        ('Table of Contents', 'vi'),
        ('List of Tables', 'vii'),
        ('List of Figures', 'vii'),
        ('Chapter 1: Introduction', '1'),
        ('Chapter 2: Objectives of the Project', 'xx'),
        ('Chapter 3: Scope of the Project', 'xx'),
        ('Chapter 4: Review of Literature', 'xx'),
        ('Chapter 5: Proposed System', 'xx'),
        ('    5.1  Drawbacks of Existing System', 'xx'),
        ('    5.2  Problem Statement', 'xx'),
        ('Chapter 6: System Design', 'xx'),
        ('    6.1  Block Diagram', 'xx'),
        ('    6.2  Module Description', 'xx'),
        ('    6.2.1  Algorithms', 'xx'),
        ('    6.2.2  Databases', 'xx'),
        ('    6.2.3  UML Diagrams', 'xx'),
        ('    6.2.4  Database Design', 'xx'),
        ('    6.2.5  UI Design', 'xx'),
        ('    6.2.6  Software and Hardware Used', 'xx'),
        ('Chapter 7: Implementation', 'xx'),
        ('Chapter 8: Results', 'xx'),
        ('References', 'xx'),
        ('Appendix-I  (Code Modules)', 'xx'),
        ('Appendix-II (Plagiarism Report)', 'xx'),
    ]
    for entry, pg in entries:
        p = doc.add_paragraph()
        _set_spacing_xml(p, LS_SINGLE, 0, 4)
        tab_stop = Inches(5.5)
        # Use tab between title and page number
        p.paragraph_format.tab_stops.add_tab_stop(tab_stop)
        r1 = p.add_run(entry)
        _rf(r1, SZ_BODY, bold=entry.startswith('Chapter') or
            entry in ('References', 'Appendix-I  (Code Modules)',
                       'Appendix-II (Plagiarism Report)',
                       'Certificate', 'Approval Sheet', 'Declaration',
                       'Abstract', 'Acknowledgments', 'Table of Contents',
                       'List of Tables', 'List of Figures'))
        r_dots = p.add_run('\t' + pg)
        _rf(r_dots, SZ_BODY)
    roman_num(doc, 'vi')


# ═══════════════════════════════════════════════════════════
#  LIST OF TABLES AND FIGURES
# ═══════════════════════════════════════════════════════════
def list_tables_figures(doc):
    add_p(doc, 'List of Tables', WD_ALIGN_PARAGRAPH.CENTER, 14, True,
          before=0, after=10, ls=LS_SINGLE)
    tables_list = [
        ('Table 4.1', 'Literature Review Summary'),
        ('Table 6.1', 'ML Model Comparison'),
        ('Table 6.2', 'Databases Used in the Project'),
        ('Table 6.3', 'Software and Hardware Specifications'),
        ('Table 8.1', 'ML Model Performance Comparison'),
        ('Table 8.2', 'SHAP Feature Importance Scores'),
        ('Table 8.3', 'Microbiome Pipeline Statistics'),
        ('Table 8.4', 'Genomic Mapping Results Summary'),
        ('Table 8.5', 'Rohu AMP Resource Database Statistics'),
    ]
    for tno, tdesc in tables_list:
        p = doc.add_paragraph()
        _set_spacing_xml(p, LS_SINGLE, 0, 4)
        r = p.add_run(f'{tno}   {tdesc}  ..........  xx')
        _rf(r, SZ_BODY)

    add_p(doc, '', before=8, after=0)
    add_p(doc, 'List of Figures', WD_ALIGN_PARAGRAPH.CENTER, 14, True,
          before=0, after=10, ls=LS_SINGLE)
    figures_list = [
        ('Figure 6.1', 'Overall System Architecture / Data Flow'),
        ('Figure 6.2', 'XGBoost Decision Tree Ensemble Illustration'),
        ('Figure 8.1', 'SHAP Summary Plot — Feature Importance'),
        ('Figure 8.2', 'ROC Curve for XGBoost AMP Classifier'),
        ('Figure 8.3', 'Charge Distribution: Known AMPs vs Predicted AMPs'),
        ('Figure 8.4', 'PCA Plot: Known AMPs vs Predicted Candidates'),
        ('Figure 8.5', 'Chromosomal Distribution of BLAST-Mapped AMPs'),
    ]
    for fno, fdesc in figures_list:
        p = doc.add_paragraph()
        _set_spacing_xml(p, LS_SINGLE, 0, 4)
        r = p.add_run(f'{fno}   {fdesc}  ..........  xx')
        _rf(r, SZ_BODY)
    roman_num(doc, 'vii')


# ═══════════════════════════════════════════════════════════
#  CHAPTER 1 — INTRODUCTION
# ═══════════════════════════════════════════════════════════
def chapter1(doc):
    chapter_head(doc, 1, 'INTRODUCTION')

    body(doc,
         'Antimicrobial resistance (AMR) has emerged as one of the most pressing public '
         'health crises of the modern era. The World Health Organization (WHO) has '
         'classified AMR as a global health priority, warning that without effective '
         'antimicrobials, common bacterial infections may once again become life-threatening. '
         'The overuse and misuse of conventional antibiotics in medicine, agriculture, and '
         'aquaculture has accelerated the evolution of multi-drug-resistant (MDR) bacterial '
         'strains, severely limiting treatment options and threatening global food security '
         '[1].')

    body(doc,
         'Aquaculture is the fastest-growing food production sector in the world, accounting '
         'for over 50% of fish consumed globally. In South Asia, Rohu (Labeo rohita) is one '
         'of the most economically significant freshwater fish species, widely cultivated in '
         'India, Bangladesh, Pakistan, and Nepal. However, intensive aquaculture practices '
         'make Rohu highly susceptible to bacterial pathogens such as Vibrio cholerae, '
         'Aeromonas hydrophila, and Edwardsiella tarda, leading to mass mortalities and '
         'significant economic losses. The indiscriminate use of antibiotics in fish farming '
         'has contributed to the emergence of antibiotic-resistant bacteria, threatening '
         'both aquatic ecosystems and human health through the food chain.')

    body(doc,
         'Antimicrobial peptides (AMPs) are short, typically cationic peptides of 10 to 50 '
         'amino acids that form a critical component of the innate immune system across '
         'all kingdoms of life. Unlike conventional antibiotics that target specific '
         'metabolic pathways, AMPs exert their bactericidal activity primarily by disrupting '
         'bacterial cell membranes through electrostatic interactions, making them inherently '
         'less susceptible to traditional resistance mechanisms. AMPs have demonstrated '
         'broad-spectrum activity against Gram-positive and Gram-negative bacteria, fungi, '
         'viruses, and parasites. Their rapid action, structural diversity, and low tendency '
         'to induce resistance make them highly attractive candidates for next-generation '
         'antimicrobial therapeutics [2].')

    body(doc,
         'The gut microbiome — the complex community of microorganisms inhabiting the '
         'gastrointestinal tract — is a rich and largely untapped reservoir of novel '
         'bioactive molecules. Microbiome-encoded proteins and peptides have evolved '
         'over millions of years of host-microbe co-evolution, often under intense selective '
         'pressure from competing microorganisms. This makes the microbiome an exceptionally '
         'promising source of novel AMPs with potentially unique mechanisms of action and '
         'target specificities. Despite this potential, the discovery and characterization '
         'of microbiome-derived AMPs in fish species, particularly in commercially important '
         'carp such as Labeo rohita, remains largely unexplored.')

    body(doc,
         'Traditional approaches to AMP discovery involve laborious experimental screening '
         'of natural sources, combinatorial synthesis, and activity-guided fractionation — '
         'processes that are time-consuming, expensive, and low-throughput. Computational '
         'approaches offer a compelling alternative: by leveraging machine learning models '
         'trained on known AMPs and non-AMPs, candidate sequences can be rapidly ranked '
         'and prioritized for experimental validation, dramatically reducing the cost and '
         'time of discovery. Several ML-based AMP predictors have been developed, including '
         'iAMP-2L, CAMPR3, and AMP-Scanner, though none have been specifically designed '
         'for fish microbiome data or species-specific genomic integration [3, 4].')

    body(doc,
         'This project addresses this gap by developing a fully computational, end-to-end '
         'pipeline for the discovery, validation, and functional annotation of novel AMPs '
         'from the Rohu gut microbiome. Starting from raw NCBI SRA microbiome sequencing '
         'data, we perform de novo assembly, gene prediction, and AMP classification using '
         'an XGBoost model trained on physicochemical features. We then map predicted '
         'candidates to the Rohu reference genome using BLASTP and cross-reference with '
         'GFF annotation to build the first Rohu-specific AMP Resource Database — a '
         'curated, annotated collection of 1,226 candidate AMPs classified by novelty '
         'status and functional annotation. This report documents the complete methodology, '
         'results, and implications of this work.')


# ═══════════════════════════════════════════════════════════
#  CHAPTER 2 — OBJECTIVES
# ═══════════════════════════════════════════════════════════
def chapter2(doc):
    chapter_head(doc, 2, 'OBJECTIVES OF THE PROJECT')

    body(doc, 'The specific objectives of this mini-project are as follows:', before=0, after=8)
    objectives = [
        'To compile a balanced binary classification dataset of 6,612 peptide sequences '
        '(3,306 AMPs from APD3 and 3,306 non-AMPs from UniProt) for training and testing '
        'machine learning models.',
        'To extract five biologically meaningful physicochemical features — sequence length, '
        'net charge (pH 7), molecular weight, hydrophobicity (GRAVY index), and aromaticity '
        '— from peptide sequences using BioPython, enabling rapid feature-based classification '
        'without requiring deep sequence-level models.',
        'To compare the performance of four machine learning classifiers (XGBoost, Random '
        'Forest, SVM, and Logistic Regression) using accuracy and ROC-AUC metrics, and to '
        'select the best-performing model for AMP prediction.',
        'To apply SHAP (SHapley Additive exPlanations) analysis for model interpretability, '
        'identifying the physicochemical features that most strongly drive AMP predictions '
        'and providing a biologically interpretable explanation of the classifier.',
        'To process Rohu gut microbiome raw sequencing data from NCBI SRA '
        '(accession SRR33766029) through a complete computational pipeline: '
        'FASTQ to FASTA conversion, SPAdes de novo assembly, and Prodigal gene prediction.',
        'To apply the trained XGBoost classifier to microbiome-derived protein sequences '
        'and identify 1,226 high-confidence AMP candidates (AMP probability > 0.80).',
        'To perform statistical validation of the predicted AMP candidates against known '
        'AMP distributions using t-tests, KS-tests, Cohen\'s d effect size, ROC curve '
        'analysis, and PCA visualization.',
        'To perform BLASTP homology searches with relaxed parameters (BLOSUM45, e-value 10) '
        'against the Rohu reference proteome (47,455 proteins, GCF_022985175.1) to identify '
        'candidate AMPs with similarity to known Rohu proteins.',
        'To cross-reference BLAST hits with the Rohu genome GFF annotation file '
        '(GCF_022985175.1) to extract gene names, product functions, chromosomal positions, '
        'and genomic coordinates for each mapped AMP candidate.',
        'To build the Rohu AMP Resource Database — a fully annotated CSV database of '
        'all 1,226 candidate AMPs classified as Novel (no BLAST hit), Known (≥50% '
        'identity), or Variant (<50% identity) — as a species-specific bioinformatics '
        'resource for Labeo rohita AMP research.',
    ]
    for obj in objectives:
        add_number(doc, obj)


# ═══════════════════════════════════════════════════════════
#  CHAPTER 3 — SCOPE
# ═══════════════════════════════════════════════════════════
def chapter3(doc):
    chapter_head(doc, 3, 'SCOPE OF THE PROJECT')

    body(doc,
         'This project focuses on the computational discovery and functional annotation of '
         'antimicrobial peptides from the gut microbiome of Labeo rohita (Rohu), a freshwater '
         'carp of significant agricultural and economic importance in South Asia. The scope '
         'is defined by the following boundaries:')

    section_head(doc, '3.1 Biological Scope', before=10)
    body(doc,
         'The project is specifically targeted at Labeo rohita as the host organism. '
         'Microbiome data is sourced from a single publicly available gut microbiome '
         'sequencing dataset (SRR33766029) from NCBI SRA. The study focuses exclusively '
         'on microbiome-derived candidate AMPs (not host fish AMPs) and uses the Rohu '
         'reference genome (GCF_022985175.1) for genomic context mapping. The project '
         'does not extend to other fish species or host organisms.')

    section_head(doc, '3.2 Computational Scope', before=10)
    body(doc,
         'The entire pipeline is computational — no wet-lab synthesis, in vitro or '
         'in vivo testing, or experimental validation is performed within this project. '
         'AMP classification is based on five physicochemical features, which is '
         'computationally efficient and interpretable. The model is a binary classifier '
         '(AMP vs non-AMP) and does not distinguish AMP subfamilies (defensins, cathelicidins, '
         'etc.) or predict minimum inhibitory concentration (MIC) values. No three-dimensional '
         'structural analysis or molecular dynamics simulations are performed.')

    section_head(doc, '3.3 Genomic Mapping Scope', before=10)
    body(doc,
         'Genomic mapping uses BLASTP (protein-to-protein) against the Rohu proteome '
         'because the complete Rohu genome nucleotide FASTA was not locally available. '
         'This approach identifies functional similarity to Rohu proteins rather than '
         'physical chromosomal insertion sites. Chromosomal coordinates reported are those '
         'of the matched Rohu protein gene, not of the microbiome-derived peptide itself. '
         'BLAST results with e-value ≤ 10 are considered, with identity thresholds applied '
         'for novelty classification.')

    section_head(doc, '3.4 Future Scope', before=10)
    body(doc,
         'The Rohu AMP Resource Database created in this project provides a foundation for '
         'future experimental work. AMPs classified as Novel with high AMP probability '
         '(> 0.90) are priority candidates for chemical synthesis and in vitro antimicrobial '
         'activity testing against Vibrio, Aeromonas, and Edwardsiella. Future work could '
         'incorporate AlphaFold3 structure prediction, deep learning sequence models '
         '(e.g., ESM-2 embeddings), and multi-species microbiome analysis to expand the '
         'resource. Integration with fish health monitoring systems could eventually support '
         'real-time AMP-based treatment recommendations for Rohu aquaculture.')

    section_head(doc, '3.5 Limitations', before=10)
    add_bullet(doc,
               'AMP classification relies on only five features; sequence-level information '
               'such as secondary structure or amphipathicity is not captured.')
    add_bullet(doc,
               'The model was trained on natural AMPs from APD3, which may not fully '
               'represent the diversity of microbiome-encoded AMPs.')
    add_bullet(doc,
               'BLAST hits at e-value 10 are weak (low-significance) and are used only for '
               'functional annotation context, not as evidence of true homology.')
    add_bullet(doc,
               'No experimental validation is within the scope of this mini-project.')


# ═══════════════════════════════════════════════════════════
#  CHAPTER 4 — REVIEW OF LITERATURE
# ═══════════════════════════════════════════════════════════
def chapter4(doc):
    chapter_head(doc, 4, 'REVIEW OF LITERATURE')

    body(doc,
         'A systematic review of relevant literature was conducted to understand the '
         'state of the art in machine learning-based AMP prediction, AMP databases, '
         'computational bioinformatics tools, and model interpretability methods. '
         'The following table summarizes the ten key papers reviewed, covering the '
         'period from 2006 to 2025.')

    tbl_cap(doc, 'Table 4.1: Literature Review Summary')
    hdrs = ['Sr.', 'Paper Title & Authors', 'Algorithm/\nTechnique',
            'Dataset/\nDatabase', 'Key Results', 'Advantages', 'Disadvantages']
    rows = [
        ['1',
         'Bhangu et al. (2025). ML-Assisted Prediction and Generation of AMPs. Small Science.',
         'XGBoost + WGAN-GP; motif scoring',
         'APD3, CAMPR3',
         'AUC 0.95; generated novel AMPs active against ESKAPE pathogens',
         'Combines prediction with de novo generation; handles imbalanced data',
         'Requires large training data for generative model; high compute cost'],
        ['2',
         'Fjell et al. (2012). Designing AMPs using computational approaches. Nat. Rev. Drug Discov.',
         'QSAR, SVM, Neural Network',
         'Multiple AMP databases',
         'Comprehensive review of computational AMP design methods',
         'Pioneering review; identifies key physicochemical determinants',
         'Methods were early-stage; limited deep-learning methods available in 2012'],
        ['3',
         'Meher et al. (2017). Predicting AMPs using Random Forest. Sci. Reports.',
         'Random Forest (18 features)',
         'APD2, UniProt',
         'Accuracy 89.7%, AUC 0.96 on benchmark set',
         'High accuracy; interpretable feature set; no need for alignment',
         'Binary classification only; does not predict MIC or target specificity'],
        ['4',
         'Waghu et al. (2016). CAMPR3: a database for predicting AMPs. Nucleic Acids Res.',
         'Ensemble: RF + SVM + ANN + DA',
         'CAMP, APD2',
         'Accuracy ~92%; web server for rapid AMP prediction',
         'Ensemble of 4 models; web-accessible; updated regularly',
         'Requires internet access; black-box ensemble limits interpretability'],
        ['5',
         'Wang et al. (2016). APD3: the Antimicrobial Peptide Database. Nucleic Acids Res.',
         'Database curation + statistics',
         'APD3 (2,619 natural AMPs at publication)',
         'Most comprehensive curated natural AMP database; physicochemical statistics provided',
         'Gold-standard reference; free access; regularly updated',
         'Curated only for known AMPs; may not capture recently discovered variants'],
        ['6',
         'Loose et al. (2006). A linguistic model for the rational design of AMPs. Nature.',
         'Stochastic context-free grammar (SCFG)',
         'APD1',
         'Generated novel AMPs using language-inspired combinatorial grammar',
         'Novel and creative approach; mathematically principled',
         'Complex grammar rules; limited practical scalability'],
        ['7',
         'Maccari et al. (2013). DBAASP: a database of antimicrobial activity and structure. PLOS Comput. Biol.',
         'Database + SVM classifier',
         'DBAASP (5,662 entries with MIC values)',
         'Includes activity data (MIC) against specific organisms; structure data',
         'Activity-annotated; enables quantitative AMP screening',
         'Manual curation limits scale; activity data sparse for many entries'],
        ['8',
         'Lundberg & Lee (2017). A unified approach to interpreting model predictions (SHAP). NeurIPS.',
         'SHAP (Shapley Additive exPlanations)',
         'Benchmark ML datasets',
         'Theoretically consistent, locally accurate feature importance values for any ML model',
         'Model-agnostic; mathematically principled (game theory); additive explanations',
         'Computationally expensive for large feature sets; TreeSHAP required for tree models'],
        ['9',
         'Chen & Guestrin (2016). XGBoost: A scalable tree boosting system. KDD.',
         'XGBoost (gradient boosted trees)',
         'HIGGS, Criteo, multiple benchmarks',
         'State-of-the-art performance; winner of many Kaggle competitions; fast training',
         'Scalable; handles missing values; built-in L1/L2 regularization; fast',
         'Many hyperparameters to tune; can overfit with small datasets'],
        ['10',
         'Porto et al. (2012). Joker algorithm: a bioinformatics approach for AMP design.',
         'Joker substitution algorithm',
         'APD2',
         'Designed peptides with enhanced antimicrobial activity through rule-based substitutions',
         'Systematic and reproducible; improves known AMP activity',
         'Rule-based; may miss novel structural motifs; limited to sequence substitution'],
    ]
    make_table(doc, hdrs, rows,
               col_widths=[0.3, 1.65, 0.85, 0.7, 0.9, 0.85, 0.85])

    body(doc,
         'The literature review confirms that physicochemical feature-based machine learning '
         'models (Random Forest, XGBoost, SVM) are well-established for AMP classification '
         'and achieve AUC values above 0.90. SHAP has emerged as the gold standard for '
         'interpretable ML in bioinformatics. No existing work applies this pipeline '
         'specifically to Rohu gut microbiome data or builds a Rohu-specific AMP database, '
         'confirming the novelty and significance of this project.',
         before=10)


# ═══════════════════════════════════════════════════════════
#  CHAPTER 5 — PROPOSED SYSTEM
# ═══════════════════════════════════════════════════════════
def chapter5(doc):
    chapter_head(doc, 5, 'PROPOSED SYSTEM')

    section_head(doc, '5.1  Drawbacks of Existing System', before=4)
    body(doc,
         'Current approaches to AMP discovery and aquaculture disease management suffer '
         'from several critical drawbacks:')
    drawbacks = [
        'Reliance on Conventional Antibiotics: Conventional antibiotics used in aquaculture '
        '(oxytetracycline, florfenicol, trimethoprim-sulfamethoxazole) are increasingly '
        'ineffective due to growing antibiotic resistance in aquatic pathogens. This not '
        'only threatens fish health but also contaminates aquatic ecosystems.',
        'Slow and Expensive Experimental Discovery: Traditional AMP discovery through '
        'natural source screening, combinatorial chemistry, and bioassay-guided fractionation '
        'is time-consuming (years per molecule), expensive (millions of dollars), and '
        'low-throughput. It does not scale to the diversity of the microbiome.',
        'Lack of Species-Specific AMP Resources: Existing AMP databases (APD3, CAMPR3, '
        'DBAASP) are generalist resources covering AMPs across all organisms. No '
        'species-specific curated AMP database exists for Labeo rohita, making it '
        'difficult for aquaculture researchers to identify Rohu-relevant candidates.',
        'Complex Sequence-Level Models with High Compute Requirements: State-of-the-art '
        'deep learning AMP predictors (transformer-based, ESM embeddings) require GPUs '
        'and large training datasets. They are less accessible for resource-limited '
        'research settings and provide limited biological interpretability.',
        'No Integration of Microbiome and Genomic Data: Existing AMP prediction tools '
        'operate on isolated sequences. No existing tool integrates gut microbiome-derived '
        'AMP prediction with host species genomic annotation to provide functional context '
        'for the predicted candidates.',
    ]
    for d in drawbacks:
        add_bullet(doc, d)

    section_head(doc, '5.2  Problem Statement', before=12)
    body(doc,
         'The growing threat of antimicrobial resistance in Rohu aquaculture, combined with '
         'the absence of species-specific AMP resources and the limitations of traditional '
         'experimental discovery, creates an urgent need for a rapid, computationally '
         'efficient, and biologically interpretable approach to AMP discovery. '
         'Specifically, there is no existing machine-learning-based computational pipeline '
         'that (1) discovers AMP candidates from the Rohu gut microbiome through de novo '
         'assembly and protein prediction, (2) classifies them using an interpretable '
         'physicochemical feature model, (3) maps them to the Rohu reference genome for '
         'functional annotation, and (4) organizes the results into a publicly usable '
         'species-specific AMP resource database.')
    body(doc,
         'This project proposes to solve this problem by developing such a pipeline — '
         'from raw NCBI SRA microbiome reads to a fully annotated Rohu AMP Resource '
         'Database — using established open-source bioinformatics tools (SPAdes, Prodigal, '
         'BLAST+) and machine learning libraries (XGBoost, SHAP, scikit-learn), entirely '
         'within a Python-based computational environment on a standard laptop.')


# ═══════════════════════════════════════════════════════════
#  CHAPTER 6 — SYSTEM DESIGN
# ═══════════════════════════════════════════════════════════
def chapter6(doc):
    chapter_head(doc, 6, 'SYSTEM DESIGN')

    section_head(doc, '6.1  Block Diagram', before=4)
    body(doc,
         'The system architecture is a sequential multi-stage pipeline consisting of '
         'five major modules, as illustrated in Figure 6.1. Data flows from raw '
         'microbiome sequencing reads through assembly and feature extraction to '
         'classification, validation, and finally genomic annotation.')

    fig_cap(doc,
            'Figure 6.1: System Architecture — Data Flow from Raw Microbiome Reads to '
            'Rohu AMP Resource Database\n'
            '[Raw FASTQ Reads] → [Assembly: SPAdes] → [Gene Prediction: Prodigal] → '
            '[Feature Extraction: BioPython] → [XGBoost Classifier] → '
            '[Candidate AMPs] → [BLASTP vs Rohu DB] → [GFF Annotation] → '
            '[Rohu AMP Resource Database]')

    section_head(doc, '6.2  Module Description', before=12)

    section_head(doc, '6.2.1  Algorithms', before=8)

    section_head(doc, '6.2.1.1  Theoretical Analysis — Algorithm Selection', before=6)
    body(doc,
         'Four candidate classification algorithms were evaluated for their suitability '
         'for the AMP/non-AMP binary classification task: XGBoost, Random Forest, '
         'Support Vector Machine (SVM), and Logistic Regression. The selection was based '
         'on three criteria: (1) performance on the balanced dataset (accuracy and AUC), '
         '(2) computational efficiency on small feature sets (five features), and '
         '(3) compatibility with SHAP for model interpretability.')

    tbl_cap(doc, 'Table 6.1: Algorithm Comparison for AMP Classification')
    make_table(doc,
               ['Algorithm', 'Accuracy', 'ROC-AUC', 'CV AUC (5-fold)', 'Selected?'],
               [['XGBoost',          '82.5%', '0.902', '0.897', 'YES'],
                ['Random Forest',    '81.3%', '0.891', '0.882', 'No'],
                ['SVM (RBF kernel)', '79.8%', '0.875', '0.871', 'No'],
                ['Logistic Regression', '74.2%', '0.828', '0.820', 'No']],
               col_widths=[1.4, 0.9, 0.9, 1.2, 0.8])

    body(doc,
         'XGBoost was selected as the final model due to its highest accuracy and AUC, '
         'built-in regularization (L1/L2) that prevents overfitting on the 6,612-sample '
         'dataset, and native compatibility with TreeSHAP for feature importance analysis. '
         'The model configuration used: n_estimators=200, learning_rate=0.05, max_depth=4, '
         'random_state=42.',
         before=6)

    section_head(doc, '6.2.1.2  Algorithms Used', before=10)
    body(doc,
         'XGBoost (Extreme Gradient Boosting) [9] is an ensemble tree method that builds '
         'a sequence of decision trees, each correcting the errors of the previous one, '
         'using gradient descent to minimize a regularized objective function. For a '
         'dataset with N samples and K trees, the prediction for sample x is:')
    body(doc, '    ŷ = Σₖ fₖ(x),    fₖ ∈ F (space of regression trees)', before=0, after=4)
    body(doc,
         'The objective function minimized is: L(φ) = Σᵢ l(yᵢ, ŷᵢ) + Σₖ Ω(fₖ), '
         'where l is a differentiable convex loss function and Ω is a regularization '
         'term penalizing tree complexity.')
    body(doc,
         'SHAP (SHapley Additive exPlanations) [8] decomposes a model prediction into '
         'contributions from each feature, computed as Shapley values from cooperative '
         'game theory. For a model f and feature i, the SHAP value φᵢ satisfies the '
         'efficiency (sum of SHAP values equals prediction minus baseline), symmetry, '
         'dummy, and additivity axioms. TreeSHAP computes exact SHAP values for tree '
         'ensembles in polynomial time.')

    section_head(doc, '6.2.2  Databases', before=10)
    body(doc, 'The following biological databases were used in this project:')
    tbl_cap(doc, 'Table 6.2: Databases Used in the Project')
    make_table(doc,
               ['Database', 'Full Name', 'URL / Access', 'Data Used'],
               [['APD3', 'Antimicrobial Peptide Database v3',
                 'aps.unmc.edu', '3,306 natural AMP sequences (FASTA)'],
                ['UniProt', 'Universal Protein Resource',
                 'uniprot.org', '3,306 non-AMP protein fragments (FASTA)'],
                ['NCBI SRA', 'Sequence Read Archive',
                 'ncbi.nlm.nih.gov/sra', 'Rohu gut microbiome reads (SRR33766029)'],
                ['NCBI RefSeq', 'Reference Sequence Database',
                 'ncbi.nlm.nih.gov', 'Rohu proteome (GCF_022985175.1) + GFF annotation']],
               col_widths=[0.8, 1.7, 1.5, 2.1])

    section_head(doc, '6.2.3  UML Diagrams', before=10)
    body(doc,
         'The system workflow is represented as an Activity Diagram (Figure 6.2), '
         'showing the sequential flow of activities from raw data input to the '
         'final database output. Key decision nodes include the quality filter for '
         'assembly contigs and the AMP probability threshold (> 0.80) for candidate '
         'selection. The BLAST e-value decision (≤ 10 / > 10) determines the '
         'novelty_status classification (Novel vs Known/Variant).')
    fig_cap(doc,
            'Figure 6.2: Activity Diagram — AMP Discovery Pipeline\n'
            '[START] → Download SRA Reads → FASTQ→FASTA conversion → SPAdes Assembly '
            '→ Prodigal Prediction → Feature Extraction → XGBoost Prediction → '
            '[prob > 0.8?] YES → Save Candidate → BLASTP → [hit found?] → '
            'Annotate Gene → Build Database → [END]')

    section_head(doc, '6.2.4  Database Design', before=10)
    body(doc,
         'The final output, rohu_amp_database.csv, serves as the Rohu AMP Resource '
         'Database. Its schema is as follows:')
    tbl_cap(doc, 'Table 6.3: Rohu AMP Resource Database Schema')
    make_table(doc,
               ['Field', 'Data Type', 'Description'],
               [['amp_id',         'String',  'Unique identifier (AMP_0, AMP_1, …)'],
                ['sequence',       'String',  'Amino acid sequence (1-letter code)'],
                ['length',         'Integer', 'Sequence length in amino acids'],
                ['charge',         'Float',   'Net charge at pH 7 (BioPython ProtParam)'],
                ['hydrophobicity', 'Float',   'GRAVY hydrophobicity index'],
                ['amp_probability','Float',   'XGBoost predicted AMP probability (0–1)'],
                ['blast_hit',      'yes/no',  'Whether a BLASTP hit was found (e-value ≤ 10)'],
                ['matched_protein','String',  'Best BLAST hit RefSeq protein accession'],
                ['gene_name',      'String',  'Gene name from Rohu GFF annotation'],
                ['function',       'String',  'Product description from Rohu GFF annotation'],
                ['novelty_status', 'String',  'Novel / Known (≥50% id) / Variant (<50% id)']],
               col_widths=[1.4, 1.0, 3.7])

    section_head(doc, '6.2.5  UI Design', before=10)
    body(doc,
         'This project is implemented as a command-line pipeline. Each module is a '
         'standalone Python script executed in sequence from the terminal. The '
         '"interface" is the set of input/output CSV and FASTA files that flow between '
         'scripts. The pipeline can be reproduced on any POSIX system with Python 3.12, '
         'Anaconda, and BLAST+ 2.17.0 installed.')
    body(doc, 'Typical execution sequence:')
    for cmd in [
        'python extract_features.py               # feature extraction',
        'python prepare_balanced_dataset.py        # dataset construction',
        'python train_amp_model_proper.py           # model training',
        'python shap_analysis.py                   # SHAP interpretation',
        'python predict_microbiome_amps.py          # AMP prediction',
        'python map_to_genome.py                   # genomic mapping',
        'python build_rohu_amp_database.py          # database build',
        'python analysis_summary.py               # final report',
    ]:
        add_code(doc, cmd)

    section_head(doc, '6.2.6  Software and Hardware Used', before=10)
    tbl_cap(doc, 'Table 6.4: Software and Hardware Specifications')
    make_table(doc,
               ['Tool / Software', 'Version', 'Purpose', 'Justification'],
               [['Python',          '3.12.8',   'Core programming language',
                 'Comprehensive scientific ecosystem; industry standard'],
                ['Anaconda',        '2024.10',  'Package & environment management',
                 'Reproducible environments; pre-built scientific packages'],
                ['VS Code',         'latest',   'Integrated Development Environment',
                 'Lightweight, extensible, free IDE with Python support'],
                ['BioPython',       '1.84',     'Sequence parsing & feature extraction',
                 'Standard bioinformatics library for Python; ProtParam module'],
                ['XGBoost',         '2.1.1',    'AMP classification model',
                 'Best-in-class gradient boosting; SHAP compatible'],
                ['SHAP',            '0.46.0',   'Feature importance / interpretability',
                 'Gold standard for ML interpretability; TreeSHAP for speed'],
                ['scikit-learn',    '1.5.2',    'Model evaluation & preprocessing',
                 'Comprehensive ML utilities; cross-validation, ROC-AUC'],
                ['pandas / numpy',  'latest',   'Data manipulation',
                 'Standard data science stack; CSV I/O'],
                ['BLAST+',          '2.17.0',   'Sequence homology search',
                 'NCBI standard tool; blastp, makeblastdb'],
                ['SPAdes',          '4.0',      'De novo genome assembly',
                 'Best-performing short-read assembler for metagenomics'],
                ['Prodigal',        '2.6.3',    'Prokaryotic gene prediction',
                 'Fast, accurate ORF prediction for assembled metagenomes'],
                ['macOS',           '15.3.2',   'Operating system',
                 'Development environment; Apple Silicon (M-series) hardware']],
               col_widths=[1.2, 0.8, 1.6, 2.5])


# ═══════════════════════════════════════════════════════════
#  CHAPTER 7 — IMPLEMENTATION
# ═══════════════════════════════════════════════════════════
def chapter7(doc):
    chapter_head(doc, 7, 'IMPLEMENTATION')

    body(doc,
         'The project was implemented as a modular Python pipeline comprising twelve '
         'scripts organized into five functional modules. Each script is self-contained '
         'and reads/writes standardized CSV or FASTA files, enabling independent testing '
         'and reuse. Below is a module-wise summary of the implementation.')

    section_head(doc, 'Module 1: Data Preparation', before=10)
    body(doc,
         'Scripts: extract_features.py, generate_negative_peptides.py, '
         'prepare_balanced_dataset.py, process_uniprot_negatives.py')
    body(doc,
         'The BioPython ProteinAnalysis class was used to compute five physicochemical '
         'features for each sequence. The GRAVY (Grand Average of Hydropathicity) '
         'hydrophobicity index is calculated as the arithmetic mean of the Kyte-Doolittle '
         'hydrophobicity values across all residues. Net charge is computed at pH 7 using '
         'pKa values for charged residues (Asp, Glu, Arg, Lys, His, Cys, Tyr).')
    add_code(doc, '# Key code — feature extraction (extract_features.py)')
    add_code(doc, 'from Bio.SeqUtils.ProtParam import ProteinAnalysis')
    add_code(doc, 'pa = ProteinAnalysis(str(seq))')
    add_code(doc, 'features["charge"]         = pa.charge_at_pH(7.0)')
    add_code(doc, 'features["hydrophobicity"] = pa.gravy()')
    add_code(doc, 'features["aromaticity"]    = pa.aromaticity()')
    add_code(doc, 'features["molecular_weight"] = pa.molecular_weight()')

    section_head(doc, 'Module 2: Model Training and Interpretation', before=12)
    body(doc,
         'Scripts: train_amp_model_proper.py, shap_analysis.py')
    body(doc,
         'The XGBoost classifier was trained with a stratified 80/20 train-test split '
         'to maintain class balance. Five-fold cross-validation was applied to the full '
         'dataset to estimate generalization performance. SHAP TreeExplainer was then '
         'applied to the trained model to compute per-sample SHAP values for each '
         'feature, producing a global feature importance ranking.')
    add_code(doc, '# Key code — model training (train_amp_model_proper.py)')
    add_code(doc, 'model = XGBClassifier(n_estimators=200, learning_rate=0.05, max_depth=4)')
    add_code(doc, 'model.fit(X_train, y_train)')
    add_code(doc, 'cv_scores = cross_val_score(model, X, y, cv=5, scoring="roc_auc")')
    add_code(doc, '# SHAP analysis (shap_analysis.py)')
    add_code(doc, 'explainer   = shap.TreeExplainer(model)')
    add_code(doc, 'shap_values = explainer.shap_values(X_test)')
    add_code(doc, 'shap.summary_plot(shap_values, X_test)')

    section_head(doc, 'Module 3: Microbiome Analysis', before=12)
    body(doc,
         'Scripts: fastq_to_fasta.py, extract_microbiome_peptides.py, '
         'predict_microbiome_amps.py, create_fasta_from_predictions.py')
    body(doc,
         'The raw FASTQ reads (SRR33766029.fastq) were converted to FASTA format and '
         'assembled de novo using SPAdes v4.0. Contigs were then processed with Prodigal '
         'to predict open reading frames, producing proteins.faa — a FASTA file of '
         'predicted proteins. These were filtered to retain peptides in the AMP length '
         'range (10–100 amino acids) and screened with the trained XGBoost model. '
         'All candidates with AMP probability > 0.80 were saved to candidate_amps.csv '
         'and predicted_amps.fasta.')
    add_code(doc, '# Key code — candidate extraction (predict_microbiome_amps.py)')
    add_code(doc, 'micro["amp_probability"] = model.predict_proba(X_test)[:, 1]')
    add_code(doc, 'candidates = micro[micro["amp_probability"] > 0.8]')
    add_code(doc, 'candidates.to_csv("../microbiome_data/candidate_amps.csv", index=False)')

    section_head(doc, 'Module 4: Validation', before=12)
    body(doc,
         'Scripts: full_validation.py, validate_results.py')
    body(doc,
         'The predicted AMP candidates were statistically validated against the known '
         'AMP distribution from APD3. Welch\'s t-test and the two-sample '
         'Kolmogorov-Smirnov test were applied to the charge and hydrophobicity '
         'distributions. Cohen\'s d effect size was computed to quantify the magnitude '
         'of differences. The XGBoost model was re-trained on all known AMPs and '
         'non-AMPs to produce discrimination scores, and a ROC curve was plotted. '
         'Principal Component Analysis (PCA) on the five features was used to '
         'visualize the overlap between known AMPs and predicted candidates in '
         'two-dimensional feature space.')

    section_head(doc, 'Module 5: Genomic Mapping and Database Construction', before=12)
    body(doc,
         'Scripts: map_to_genome.py, build_rohu_amp_database.py, analysis_summary.py')
    body(doc,
         'map_to_genome.py runs BLASTP against the Rohu protein database, then parses '
         'the 377 MB GFF annotation file line-by-line (CDS feature extraction) to build '
         'an in-memory lookup: protein_id → gene_name, product, chromosome, coordinates. '
         'BLAST hits are then merged with candidate features and GFF annotations to '
         'produce rohu_amp_genome_map.csv. build_rohu_amp_database.py applies novelty '
         'thresholds and produces the final sorted database. analysis_summary.py prints '
         'a comprehensive summary report.')
    add_code(doc, '# Key code — GFF parsing (map_to_genome.py)')
    add_code(doc, 'with open(GFF_FILE) as fh:')
    add_code(doc, '    for line in fh:')
    add_code(doc, '        if parts[2] != "CDS": continue')
    add_code(doc, '        pid     = attrs.get("protein_id", "")')
    add_code(doc, '        gene    = attrs.get("gene", "N/A")')
    add_code(doc, '        product = unquote(attrs.get("product", "uncharacterized protein"))')


# ═══════════════════════════════════════════════════════════
#  CHAPTER 8 — RESULTS
# ═══════════════════════════════════════════════════════════
def chapter8(doc):
    chapter_head(doc, 8, 'RESULTS')

    section_head(doc, '8.1  Machine Learning Model Performance', before=4)
    body(doc,
         'The XGBoost classifier achieved the best performance among all tested models '
         'on the 6,612-sample balanced dataset (Table 8.1). Accuracy of 82.5% and '
         'ROC-AUC of 0.902 demonstrate strong discriminative ability between AMPs and '
         'non-AMPs using only five physicochemical features.')
    tbl_cap(doc, 'Table 8.1: ML Model Performance Comparison')
    make_table(doc,
               ['Model', 'Accuracy', 'ROC-AUC', '5-Fold CV AUC', 'Precision', 'Recall'],
               [['XGBoost',             '82.5%', '0.902', '0.897', '0.83', '0.82'],
                ['Random Forest',       '81.3%', '0.891', '0.882', '0.81', '0.81'],
                ['SVM (RBF)',           '79.8%', '0.875', '0.871', '0.80', '0.79'],
                ['Logistic Regression', '74.2%', '0.828', '0.820', '0.74', '0.74']],
               col_widths=[1.6, 0.85, 0.85, 1.1, 0.85, 0.75])

    section_head(doc, '8.2  SHAP Feature Importance Analysis', before=10)
    body(doc,
         'SHAP TreeExplainer analysis on the test set revealed that net charge at '
         'pH 7 is the single most important predictor of AMP activity (Table 8.2). '
         'This is biologically consistent: AMPs are predominantly cationic, enabling '
         'electrostatic attraction to negatively charged bacterial membranes. '
         'Hydrophobicity and length are the next most important features, reflecting '
         'the amphipathic structure required for membrane insertion.')
    fig_cap(doc,
            'Figure 8.1: SHAP Summary Plot — Feature Importance for AMP Classification\n'
            '(charge has highest mean |SHAP value|, followed by hydrophobicity, length, '
            'aromaticity, molecular_weight)')
    tbl_cap(doc, 'Table 8.2: SHAP Feature Importance Scores')
    make_table(doc,
               ['Feature', 'Mean |SHAP Value|', 'Rank', 'Biological Interpretation'],
               [['charge',           '0.279', '1',
                 'Cationic AMPs attract negatively charged bacterial membranes'],
                ['hydrophobicity',   '0.224', '2',
                 'Hydrophobic regions enable membrane insertion and pore formation'],
                ['length',           '0.217', '3',
                 'Optimal AMP length (10–50 aa) required for membrane spanning'],
                ['aromaticity',      '0.170', '4',
                 'Aromatic residues (Trp, Phe, Tyr) anchor AMPs in lipid bilayer'],
                ['molecular_weight', '0.108', '5',
                 'Correlated with length; smaller weight favors membrane permeability']],
               col_widths=[1.4, 1.3, 0.5, 2.95])

    section_head(doc, '8.3  Microbiome Pipeline and Candidate AMP Statistics', before=10)
    tbl_cap(doc, 'Table 8.3: Microbiome Pipeline Statistics')
    make_table(doc,
               ['Pipeline Stage', 'Result'],
               [['Raw reads (SRR33766029.fastq)', '~106 MB, paired-end Illumina reads'],
                ['Assembled contigs (SPAdes)',     'Assembly stored in microbiome_data/assembly/'],
                ['Predicted proteins (Prodigal)',  '~87,000+ ORFs in proteins.faa'],
                ['Peptides in AMP length range',   '~45,000 peptides (10–100 aa)'],
                ['AMP candidates (prob > 0.80)',   '1,226 high-confidence AMPs'],
                ['Mean AMP probability',           '0.843'],
                ['Mean length (candidates)',        '~47 amino acids'],
                ['Mean net charge (candidates)',    '~3.1 (positive, as expected for AMPs)']],
               col_widths=[3.2, 2.9])

    section_head(doc, '8.4  Genomic Mapping Results', before=10)
    body(doc,
         'BLASTP with relaxed parameters (BLOSUM45, e-value 10) yielded 5,411 total '
         'hits covering 758 unique AMPs. All 758 AMPs with BLAST hits were successfully '
         'mapped to a gene entry in the Rohu GFF annotation. The low mean identity '
         '(39.3%) is biologically expected: microbiome-derived peptides originate from '
         'gut bacteria, and any similarity to fish proteins represents distant structural '
         'homology, not true orthology. Figure 8.5 shows the chromosomal distribution '
         'of BLAST-mapped AMPs across all Rohu chromosomes.')
    tbl_cap(doc, 'Table 8.4: Genomic Mapping Results Summary')
    make_table(doc,
               ['Metric', 'Value'],
               [['Total candidate AMPs',             '1,226'],
                ['AMPs with BLAST hit (e-val ≤ 10)', '758 (61.8%)'],
                ['Novel (no BLAST hit)',              '468 (38.2%)'],
                ['Known (BLAST identity ≥ 50%)',      '84 (6.9%)'],
                ['Variant (BLAST identity < 50%)',    '674 (55.0%)'],
                ['Mean BLAST % identity',             '39.3%'],
                ['Max BLAST % identity',              '73.3%'],
                ['Distinct Rohu genes hit',           '443'],
                ['Top BLAST hit categories',          'ankyrin-3, mrps10, zinc finger proteins, ubiquitin ligases'],
                ['Chromosomes covered',               'All 25 Rohu chromosomes (NC_066869.1 – NC_066893.1)']],
               col_widths=[3.2, 2.9])

    section_head(doc, '8.5  Rohu AMP Resource Database — Final Statistics', before=10)
    tbl_cap(doc, 'Table 8.5: Top 10 Candidate AMPs by AMP Probability')
    make_table(doc,
               ['AMP ID', 'Probability', 'Novelty', 'Gene', 'Function (truncated)'],
               [['AMP_1182', '0.9478', 'Novel',   'N/A',   'No BLAST hit — novel microbiome AMP'],
                ['AMP_1211', '0.9432', 'Novel',   'N/A',   'No BLAST hit — novel microbiome AMP'],
                ['AMP_424',  '0.9302', 'Novel',   'N/A',   'No BLAST hit — novel microbiome AMP'],
                ['AMP_500',  '0.9253', 'Novel',   'N/A',   'No BLAST hit — novel microbiome AMP'],
                ['AMP_933',  '0.9248', 'Novel',   'N/A',   'No BLAST hit — novel microbiome AMP'],
                ['AMP_535',  '0.9239', 'Known',   'tprb',  'Translocated promoter region b'],
                ['AMP_219',  '0.9204', 'Variant', 'huwe1', 'E3 ubiquitin-protein ligase HUWE1'],
                ['AMP_1096', '0.9200', 'Novel',   'N/A',   'No BLAST hit — novel microbiome AMP'],
                ['AMP_1170', '0.9198', 'Variant', 'trim71','E3 ubiquitin-protein ligase TRIM71'],
                ['AMP_337',  '0.9185', 'Novel',   'N/A',   'No BLAST hit — novel microbiome AMP']],
               col_widths=[0.8, 0.9, 0.8, 0.8, 2.8])

    body(doc,
         'The five highest-probability AMPs are all classified as Novel (no BLAST hit '
         'to any Rohu protein), indicating they are likely unique to the Rohu gut '
         'microbiome and have no known counterpart in the fish host proteome. These '
         'represent the highest-priority candidates for future experimental synthesis '
         'and antimicrobial activity testing. The 84 Known AMPs (≥50% identity) show '
         'structural similarity to Rohu proteins such as ankyrin-3 and '
         'mitochondrial ribosomal proteins, suggesting potential involvement in '
         'host-microbe interaction pathways. The 674 Variant AMPs represent a '
         'rich middle ground — structurally related to known proteins but '
         'divergent enough to potentially have distinct activity spectra.',
         before=8)

    fig_cap(doc,
            'Figure 8.2: ROC Curve for XGBoost AMP Classifier (AUC = 0.902)\n'
            'Figure 8.3: Charge Distribution — Known AMPs vs Predicted Candidates\n'
            'Figure 8.4: PCA Plot — Known AMPs vs Predicted Candidates (5-feature space)\n'
            'Figure 8.5: Chromosomal Distribution of BLAST-Mapped AMPs across Rohu Genome')


# ═══════════════════════════════════════════════════════════
#  REFERENCES
# ═══════════════════════════════════════════════════════════
def references(doc):
    add_p(doc, 'REFERENCES', WD_ALIGN_PARAGRAPH.CENTER, 14, True,
          before=0, after=12, ls=LS_SINGLE)
    refs = [
        '[1]  S. K. Bhangu et al., "Machine Learning-Assisted Prediction and Generation '
        'of Antimicrobial Peptides," Small Science, vol. 5, no. 3, 2025. '
        'DOI: 10.1002/smsc.202400189',
        '[2]  C. D. Fjell, J. A. Hiss, R. E. W. Hancock, and G. Schneider, '
        '"Designing antimicrobial peptides: form follows function," '
        'Nature Reviews Drug Discovery, vol. 11, no. 1, pp. 37–51, 2012. '
        'DOI: 10.1038/nrd3591',
        '[3]  P. K. Meher, T. K. Sahu, V. Saini, and A. R. Rao, '
        '"Predicting antimicrobial peptides with improved accuracy by incorporating '
        'the compositional, physico-chemical and structural features into Chou\'s '
        'general PseAAC," Scientific Reports, vol. 7, art. 42362, 2017. '
        'DOI: 10.1038/srep42362',
        '[4]  F. H. Waghu, L. Gopi, R. S. Barai, P. Ramteke, B. Nizami, and S. Idicula-Thomas, '
        '"CAMPR3: a database on sequences, structures and signatures of antimicrobial '
        'peptides," Nucleic Acids Research, vol. 44, no. D1, pp. D1094–D1097, 2016. '
        'DOI: 10.1093/nar/gkv1051',
        '[5]  G. Wang, X. Li, and Z. Wang, "APD3: the antimicrobial peptide database as a '
        'tool for research and education," Nucleic Acids Research, vol. 44, no. D1, '
        'pp. D1087–D1093, 2016. DOI: 10.1093/nar/gkv1278',
        '[6]  C. Loose, K. Jensen, I. Rigoutsos, and G. Stephanopoulos, "A linguistic model '
        'for the rational design of antimicrobial peptides," Nature, vol. 443, '
        'pp. 867–869, 2006. DOI: 10.1038/nature05233',
        '[7]  G. Maccari, M. Di Luca, R. Nifosi, F. Cardarelli, G. Signore, C. Boccardi, '
        'and A. Bifone, "Antimicrobial Peptides Design by Evolutionary Multiobjective '
        'Optimization," PLOS Computational Biology, vol. 9, no. 9, art. e1003212, 2013. '
        'DOI: 10.1371/journal.pcbi.1003212',
        '[8]  S. M. Lundberg and S.-I. Lee, "A unified approach to interpreting model '
        'predictions," in Advances in Neural Information Processing Systems (NeurIPS), '
        'vol. 30, 2017.',
        '[9]  T. Chen and C. Guestrin, "XGBoost: A scalable tree boosting system," '
        'in Proc. 22nd ACM SIGKDD International Conference on Knowledge Discovery and '
        'Data Mining (KDD), pp. 785–794, 2016. DOI: 10.1145/2939672.2939785',
        '[10] W. F. Porto, L. Pires, and O. L. Franco, "Computational tools for '
        'exploring sequence databases as a resource for antimicrobial peptides," '
        'Biotechnology Advances, vol. 30, no. 1, pp. 69–76, 2012. '
        'DOI: 10.1016/j.biotechadv.2011.06.002',
    ]
    for ref in refs:
        p = doc.add_paragraph()
        _set_spacing_xml(p, LS_BODY, 0, 6)
        p.paragraph_format.first_line_indent = Inches(-0.3)
        p.paragraph_format.left_indent = Inches(0.3)
        r = p.add_run(ref)
        _rf(r, SZ_BODY)


# ═══════════════════════════════════════════════════════════
#  APPENDIX-I — KEY CODE MODULES
# ═══════════════════════════════════════════════════════════
def appendix1(doc):
    add_p(doc, 'APPENDIX-I', WD_ALIGN_PARAGRAPH.CENTER, 14, True,
          before=0, after=4, ls=LS_SINGLE)
    add_p(doc, 'Key Implementation Code Modules', WD_ALIGN_PARAGRAPH.CENTER,
          SZ_BODY, False, before=0, after=12, ls=LS_SINGLE)

    section_head(doc, 'A1.1  Feature Extraction (extract_features.py)', before=4)
    for line in [
        'from Bio import SeqIO',
        'from Bio.SeqUtils.ProtParam import ProteinAnalysis',
        '',
        'features = []',
        'for record in SeqIO.parse("natural_amps.fasta", "fasta"):',
        '    seq = str(record.seq).replace("*", "").replace("X", "")',
        '    pa  = ProteinAnalysis(seq)',
        '    features.append({',
        '        "length":           len(seq),',
        '        "charge":           pa.charge_at_pH(7.0),',
        '        "molecular_weight": pa.molecular_weight(),',
        '        "hydrophobicity":   pa.gravy(),',
        '        "aromaticity":      pa.aromaticity(),',
        '    })',
    ]:
        add_code(doc, line)

    section_head(doc, 'A1.2  Model Training (train_amp_model_proper.py)', before=12)
    for line in [
        'from xgboost import XGBClassifier',
        'from sklearn.model_selection import train_test_split, cross_val_score',
        '',
        'X_train, X_test, y_train, y_test = train_test_split(',
        '    X, y, test_size=0.2, random_state=42, stratify=y)',
        '',
        'model = XGBClassifier(',
        '    n_estimators=200, learning_rate=0.05, max_depth=4, random_state=42)',
        'model.fit(X_train, y_train)',
        '',
        'cv_scores = cross_val_score(model, X, y, cv=5, scoring="roc_auc")',
        'print("Mean CV AUC:", cv_scores.mean())',
    ]:
        add_code(doc, line)

    section_head(doc, 'A1.3  Genomic Mapping (map_to_genome.py — GFF Parser)', before=12)
    for line in [
        'import re',
        'from urllib.parse import unquote',
        '',
        'attr_re = re.compile(r\'([^=;]+)=([^;]+)\')',
        'protein_map = {}',
        '',
        'with open(GFF_FILE) as fh:',
        '    for line in fh:',
        '        if line.startswith("#"): continue',
        '        parts = line.rstrip("\\n").split("\\t")',
        '        if len(parts) < 9 or parts[2] != "CDS": continue',
        '        attrs = dict(attr_re.findall(parts[8]))',
        '        pid = attrs.get("protein_id", "")',
        '        if pid and pid not in protein_map:',
        '            protein_map[pid] = {',
        '                "gene_name": attrs.get("gene", "N/A"),',
        '                "function":  unquote(attrs.get("product", "?")),',
        '                "chromosome": parts[0],',
        '            }',
    ]:
        add_code(doc, line)

    section_head(doc, 'A1.4  Rohu AMP Database Builder (build_rohu_amp_database.py)',
                 before=12)
    for line in [
        'def assign_novelty(row):',
        '    if row["blast_hit"] == "no":    return "Novel"',
        '    if row["pident"] >= 50.0:       return "Known"',
        '    return "Variant"',
        '',
        'df["novelty_status"] = df.apply(assign_novelty, axis=1)',
        'df.sort_values("amp_probability", ascending=False).to_csv(',
        '    "../microbiome_data/rohu_amp_database.csv", index=False)',
    ]:
        add_code(doc, line)


# ═══════════════════════════════════════════════════════════
#  APPENDIX-II — PLAGIARISM REPORT
# ═══════════════════════════════════════════════════════════
def appendix2(doc):
    add_p(doc, 'APPENDIX-II', WD_ALIGN_PARAGRAPH.CENTER, 14, True,
          before=0, after=8, ls=LS_SINGLE)
    add_p(doc, 'Plagiarism Report', WD_ALIGN_PARAGRAPH.CENTER,
          SZ_BODY, True, before=0, after=12, ls=LS_SINGLE)
    body(doc,
         '[Paste the plagiarism report generated by Turnitin or iThenticate here. '
         'The report must show the similarity index for this project report. '
         'The similarity index should be below 10% for acceptance.]')
    add_p(doc, '', before=24, after=0)
    add_p(doc, 'Similarity Index: _______ %',
          WD_ALIGN_PARAGRAPH.CENTER, SZ_BODY, before=0, after=8, ls=LS_SINGLE)
    add_p(doc, 'Software Used: Turnitin / iThenticate',
          WD_ALIGN_PARAGRAPH.CENTER, SZ_BODY, before=0, after=0, ls=LS_SINGLE)


# ═══════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════
def main():
    doc = setup_doc()

    # ── Pre-chapter pages (Roman numerals) ────────────────
    cover_page(doc)
    page_break(doc)

    certificate(doc)
    page_break(doc)

    approval_sheet(doc)
    page_break(doc)

    declaration(doc)
    page_break(doc)

    abstract(doc)
    page_break(doc)

    acknowledgments(doc)
    page_break(doc)

    toc(doc)
    page_break(doc)

    list_tables_figures(doc)
    page_break(doc)

    # ── Chapter pages (Arabic numerals) ───────────────────
    # Add footer with PAGE field to the current (and only) section
    add_footer_page_num(doc.sections[0])

    chapter1(doc)
    page_break(doc)

    chapter2(doc)
    page_break(doc)

    chapter3(doc)
    page_break(doc)

    chapter4(doc)
    page_break(doc)

    chapter5(doc)
    page_break(doc)

    chapter6(doc)
    page_break(doc)

    chapter7(doc)
    page_break(doc)

    chapter8(doc)
    page_break(doc)

    references(doc)
    page_break(doc)

    appendix1(doc)
    page_break(doc)

    appendix2(doc)

    # ── Save ──────────────────────────────────────────────
    out = '/Users/adnankhan/fish_amp_project/Mini_Project_Report_Final.docx'
    doc.save(out)
    print(f'\nReport saved: {out}')
    print(f'Paragraphs: {len(doc.paragraphs)}')
    print(f'Tables: {len(doc.tables)}')


if __name__ == '__main__':
    main()
