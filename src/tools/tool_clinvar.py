# build the Engine (the tool)
# .tbi (tabix index) => indexing is done

import pysam
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))      # .../src/agents
project_root = os.path.dirname(os.path.dirname(current_dir))  # .../disease_detection

# add project root to system path so we can see 'src'
if project_root not in sys.path:
    sys.path.append(project_root)
    
from src.config import CLINVAR_FILE

"""v03 - OPTIMIZED"""
class ClinVarTool:
    def __init__(self):
        # open the file ONCE when the tool is started
        if os.path.exists(CLINVAR_FILE):
            self.vcf = pysam.VariantFile(CLINVAR_FILE)
            self.available = True
        else:
            self.vcf = None
            self.available = False
            print(f"Warning >>> ClinVar file not found at {CLINVAR_FILE}")
    
    def get_variant_significance(self, chrom, pos, ref, alt):
        # fast lookup using the already-open file
        if not self.available:
            return "ERROR >>> DB Missing ⧱"
        
        try:
            # handle 'chr' prefix mismatch
            # check only once per call instead of try/catch block if possible
            target_chrom = chrom if chrom in self.vcf.header.contigs else f"chr{chrom}"
            
            # fetch specific region (fast random access)
            # pysam uses 0-based indexing for start, 1-based for end
            records = self.vcf.fetch(target_chrom, pos - 1, pos)
            
            for record in records:
                # exact match check
                if record.ref != ref:
                    continue
                if alt in record.alts:
                    if "CLNSIG" in record.info:
                        return record.info['CLNSIG'][0]
                    return "Uncertain (No CLNSIG)"
            
            return "<<< Not Found >>>"
        except ValueError:
            # usually happens if chromosome is not in header
            return "ERROR >>> Region Error ⧱"
        except Exception as e:
            return f"ERROR >>> {e}"
    
    def close(self):
        if self.vcf:
            self.vcf.close()
        

"""v02"""
# def get_variant_significance(chrom, pos, ref, alt):
#     """
#     queries the local clinvar VCF to see if a specific variant is pathogenic
#         chrom (_type_): Chromosome (e.g., "1", "X")
#         pos (_type_): Position (1-based, as in VCF)
#         ref (_type_): Reference allele (e.g., "A")
#         alt (_type_): Alternate allele (e.g., "G")
#     returns:
#         str: Clinical Significance (...)
#     """
#     if not os.path.exists(CLINVAR_FILE):
#         return "ERROR >>> ClinVar file NOT FOUND ⚠️"
    
#     try:
#         # open ClinVar
#         vcf = pysam.VariantFile(CLINVAR_FILE)

#         # fetch records at this specific coordinate
#         # pysam.fetch uses 0-based indexing => pos-1
#         try:
#             records = vcf.fetch(chrom, pos - 1, pos)
#         except ValueError:
#             # if the chromosome format doesnt match
#             # try adding or removing 'chr' prefix
#             if chrom.startswith("chr"):
#                 chrom = chrom.replace("chr", "")
#             else:
#                 chrom = "chr" + chrom
#             try: 
#                 records = vcf.fetch(chrom, pos - 1, pos)
#             except ValueError:
#                 return "ERROR >>> Region Error ⧱"
        
#         # check if any record matches our specific REF and ALT
#         for record in records:
#             # check if this record matches the input REF
#             if record.ref != ref:
#                 continue
#             # check if our ALT is in this record's list of alts
#             # record.alts is a tuple
#             if alt in record.alts:
#                 # MATCH FOUND => extract info
#                 if "CLNSIG" in record.info:
#                     # return the first significance listed
#                     sig = record.info['CLNSIG'][0]
#                     return sig
#                 else:
#                     return "Uncertain (No CLNSIG)"
#         return "<<< Not Found >>>"
#     except Exception as e:
#         return f"ERROR >>> {e}"
    
# if __name__ == "__main__":
#     print("🧪 Testing ClinVar Lookup Tool...")
    
#     # case 1: a dummy variant that probably does not exist
#     result = get_variant_significance("1", 12345, "A", "G")
#     print(f"Test 1 (Random) >>> {result}")
    
#     # case 2: test a real pathogenic variant 
#     # peak into the file to find 1 valid coordinate
#     vcf = pysam.VariantFile(CLINVAR_FILE)
#     print("\n🔎 Searching for a real Pathogenic variant to verify...")
    
#     found = False
#     for record in vcf:
#         if "CLNSIG" in record.info and "Pathogenic" in record.info['CLNSIG'][0]:
#             # found a pathogenic variant
#             test_chrom = record.chrom
#             test_pos = record.pos
#             test_ref = record.ref
#             test_alt = record.alts[0]  # take the first ALT
            
#             print(f"FOUND >>> Known Pathogen at {test_chrom} >>> {test_pos} | {test_ref}-->{test_alt}")
#             print("Running tool against it...")
#             # run the tool
#             sig = get_variant_significance(test_chrom, test_pos, test_ref, test_alt)
#             print(f"✅ Result >>> {sig}")
#             found = True
#             break
        
#     if not found:
#         print(">>> ⚠️ Could not find a pathogenic variant in the first few lines!")