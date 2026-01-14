# ᨖ GenomAI: Rare Disease Detection Assistant
**GAAI Capstone Project W25 | HAW Hamburg**

**GenomAI** is an Agentic AI system designed to assist in the analysis of Next-Generation Sequencing (NGS) data. It combines a bioinformatics pipeline for variant calling with a **Retrieval-Augmented Generation (RAG)** agent to explain complex genetic findings to both patients and clinicians.

![Project Status](https://img.shields.io/badge/Status-Completed-success)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Stack](https://img.shields.io/badge/Tech-Streamlit%20|%20LangChain%20|%20Ollama-orange)

---

### 📁 Project Structure
The repository is organized to separate source code from data assets.

```text
disease_detection/
├── data/                    # Data storage (large files excluded from git)
│   ├── knowledge_base/      # PDF Literature for the RAG Agent
│   ├── patients/            # Simulated & Real VCF Data (JSON/VCF)
│   └── references/          # ClinVar Database 
├── src/                     # Source Code
│   ├── agents/              # Logic for variant filtering & prioritization
│   ├── tools/               # RAG and ClinVar lookup tools
│   ├── utils/               # VCF parsers and helpers
│   ├── app.py               # Main Streamlit Application
│   └── config.py            # Path configurations
├── requirements.txt         # Python dependencies
└── README.md                # Documentation

### 🛡️ License & Disclaimer
This project is for educational and research purposes only. It is not a certified medical device and should not be used for clinical diagnosis.