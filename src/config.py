import os

# 1. get the path to the 'src' folder
SRC_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. get the project root
PROJECT_ROOT = os.path.dirname(SRC_DIR)

# 3. define the data directory
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

# THE DATABASE
CLINVAR_FILE = os.path.join(DATA_DIR, "references", "clinvar.vcf.gz")
PATIENT_FILE = os.path.join(DATA_DIR, "patients", "HG002_GRCh38_1_22_v4.2.1_benchmark.vcf.gz")

SIMULATED_PATIENT_DATA = os.path.join(DATA_DIR, "patients", "simulated_patients.json")

KB_PATH = os.path.join(PROJECT_ROOT, "data", "knowledge_base")
DB_PATH = os.path.join(KB_PATH, "data", "chroma_db")