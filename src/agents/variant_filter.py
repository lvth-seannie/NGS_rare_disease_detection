"""
1. open the Patient File
2. loop through the variants
3. call the ClinVarTool
4. print out only the interesting ones (Pathogenic / Likely Pathogenic)
"""
import json
import pysam
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))      # .../src/agents
project_root = os.path.dirname(os.path.dirname(current_dir))  # .../disease_detection

# add project root to system path so we can see 'src'
if project_root not in sys.path:
    sys.path.append(project_root)

from src.config import SIMULATED_PATIENT_DATA, PATIENT_FILE
from src.tools.tool_clinvar import ClinVarTool

def analyze_patient_genome(patient_mode="real", limit=1000):
    # scan the patient VCF and filter for pathogenic variants
    print(f"🏥 Starting Analysis on Patient File...")
    print(f"📂 Reading >>> {PATIENT_FILE}")
    
    if not os.path.exists(PATIENT_FILE):
        print(f"⧱ ERROR >>> Patient file NOT FOUND at {PATIENT_FILE}")
        return
    
    try:
        vcf = pysam.VariantFile(PATIENT_FILE)
    except Exception as e:
        print(f"⧱ ERROR >>> Could not open Patient VCF: {e}")
        return
    
    hits = []
    
    # initialize the tool ONCE before the loop
    clinvar_tool = ClinVarTool()
    
    print(f"🔎 Scanning first {limit} variants...")
    print("-" * 80)
    print(f"{'{COORD':<20} | {'CHANGE':<10} | {'SIGNIFICANCE'}")
    print("-" * 80)
    
    # 1. REAL DATA
    if patient_mode == "real":
        count = 0
        # REAL ANALYSIS
        for record in vcf:
            count += 1
            if count > limit:
                break
            # skip if no alternate allele 
            if not record.alts:
                continue
            alt = record.alts[0]
        
            # 1. EXTRACT DATA
            chrom = record.chrom
            pos = record.pos
            ref = record.ref

            # 2. ASK THE TOOL (already-open)
            significance = clinvar_tool.get_variant_significance(record.chrom, 
                                                                 record.pos, 
                                                                 record.ref, 
                                                                 record.alts[0])
            
            # 3. FILTER
            # print purely Pathogenic / Likely Pathogenic results
            if "Pathogenic" in significance or "Likely pathogenic" in significance:
                row = f"Chr{chrom}:{pos:<12} | {ref}->{alt:<5} | 🚨 {significance}"
                print(row) 
                
                hits.append({
                    "chrom": chrom,
                    "pos": pos,
                    "ref": ref,
                    "alt": alt,
                    "significance": significance
                })
            
            # progress indicator
            if count % 1000 == 0:
                print(f"   ... scanned {count} lines ...")
        pass
    
    # 2. SIMULATED DATA
    else:
        print(f"🔗 Loading Simulation: {patient_mode}")
        if os.path.exists(SIMULATED_PATIENT_DATA):
            with open(SIMULATED_PATIENT_DATA, 'r') as f:
                db = json.load(f)
                
            if patient_mode in db:
                print(f"💉 Loaded Successfully ✔️: {db[patient_mode]['name']}")
                hits = db[patient_mode]['variants']
            else:
                print("🆇 Patient ID NOT FOUND")
        else:
            print("🆇 Simulation file missing ⚠️")
                
    return hits


if __name__ == "__main__":
    analyze_patient_genome()
