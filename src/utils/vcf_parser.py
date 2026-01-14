# inspect data

import pysam
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))      # .../src/agents
project_root = os.path.dirname(os.path.dirname(current_dir))  # .../disease_detection

# add project root to system path so we can see 'src'
if project_root not in sys.path:
    sys.path.append(project_root)
    
from src.config import CLINVAR_FILE, PATIENT_FILE

def inspect_vcf(file_path, label):
    # open a VCF file & print the first 5 variants w key details
    print(f"\n{'='*70}")
    print(f"🧬 INSPECTING >>> {label}")
    print(f"📂 File >>> {file_path}")
    print(f"{'='*70}")
    
    # check if file exists
    if not os.path.exists(file_path):
        print(f"⧱ Error >>> FILE NOT FOUND at {file_path}")
        return
    
    try:
        # open the VCF file
        vcf = pysam.VariantFile(file_path)
        
        # iterate through the first 5 records
        for i, record in enumerate(vcf):
            if i >= 5:
                break
            
            # extract basic info
            chrom = record.chrom
            pos = record.pos
            ref = record.ref
            # alts is a tuple - join it for display
            alts = ",".join(record.alts) if record.alts else "."
            
            # extract specific info based on file type
            extract_info = ""
            
            # for ClinVar: look for Clinical Significance (CLNSIG)
            if "CLNSIG" in record.info:
                # CLNSIG is usually a list, e.g., ['Pathogenic']
                clnsig = record.info['CLNSIG'][0]
                extra_info = f"| Significance: {clnsig}"
            
            # for patient data: look for GENOTYPE (GT)
            # GT is stored in samples & the sample name is usally the first one.
            elif len(record.samples) > 0:
                sample_name = list(record.samples)[0]
                gt = record.samples[sample_name]['GT']
                extra_info = f"| Genotype: {gt}"
            
            print(f"[{i+1}] Chr{chrom}:{pos} | {ref} -> {alts} {extra_info}")
        
        vcf.close()
        print(f"\n↳ Successfully read {label} file!")
    
    except Exception as e:
        print(f"\n⧱ Error reading file: {e}")
        
# run the inspection
if __name__ == "__main__":
    inspect_vcf(CLINVAR_FILE, "ClinVar Database (Known Disease Markers)")
    inspect_vcf(PATIENT_FILE, "Patient Data (HG002)")