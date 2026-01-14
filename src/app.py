import streamlit as st
import pandas as pd
import time
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)
    

from src.agents.variant_filter import analyze_patient_genome
from src.tools.tool_rag import query_literature

# CACHING -> prevent Streamlit from reloading the model
@st.cache_resource
def load_rag_resource():
    # trigger the embedding loading here
    # refactor tool_rag.py slightly to expose the model
    # call a warmup func 
    print("⚡ Caching AI Resouces...")
    return True

# HEADER
st.title("ᨖ GenomAI Rare Disease Assistant")
st.markdown("""
**Model:** Local RAG (MacOS)\n
This system detects potential disease markers in NGS data and uses Agentic AI to explain findings.
            """)

# call it once at start
load_rag_resource()

# UI CONFIG
st.set_page_config(
    page_title="Genomic AI Assistant",
    page_icon="🧬",
    layout="wide"
)

# SIDEBAR
with st.sidebar:
    st.write("**System Status:** ᯤ Online ")
    st.header("⛯ Configuration")
    # 1. patient mode selection 
    patient_mode = st.selectbox(
        "Select Patient Case",
        [
            ("real", "HG002 (Real Data - Healthy)"),
            ("patient_long_qt", "Simulated: Long QT Syndrome"),
            ("patient_cf", "Simulated: Cystic Fibrosis"),
            ("patient_gaucher", "Simulated: Gaucher Disease"),
            ("patient_complex", "Simulated: Patient D (Complex Case)")
        ],
        format_func=lambda x: x[1]
    )
    
    # 2. persona selection 
    st.divider()
    st.header("☰ **User Type**")
    audience = st.radio("You are:", ["Patient", "Doctor"], index=0)
    
    if st.button("▷ Run Analysis ⚡︎˖ ࣪ "):
        with st.spinner("Analyzing Agentic Workflow..."):
            # simulate processing time for realism
            time.sleep(1)
            # call the backend
            st.session_state['results'] = analyze_patient_genome(patient_mode=patient_mode[0])
            st.success("Analysis Complete ████████")
            
# MAIN DISPLAY
# check if we have results in the "Session State" (memory)
if 'results' in st.session_state:
    hits = st.session_state['results']
    
    if len(hits) == 0:
        st.info("↪ No Pathogenic variants found in the patient genome 🍀")
    else:
        st.subheader(f"🚩 Detected Variants ({len(hits)})")
        
        # convert list of dicts to a nice DataFrame
        df = pd.DataFrame(hits)
        
        # display as a clean interactive table
        st.dataframe(
            df[['chrom', 'pos', 'ref', 'alt', 'significance']],
            hide_index=True,
            width="stretch"
            # use_container_width=True # <-- being retired
        )
        
        # INTERACTIVE EXPLANATION ('Generative')
        st.subheader("⚛ AI Interpretation")
        
        # create tabs for each variant found
        tabs = st.tabs([f"Variant {i+1} (Chr{h['chrom']})" for i, h in enumerate(hits)])
        
        for i, tab in enumerate(tabs):
            with tab:
                variant = hits[i]
                st.markdown(f"**Variant** ➜] Chr{variant['chrom']} ▶ {variant['pos']} {variant['ref']} ➝ {variant['alt']}")
                st.markdown(f"**ClinVar Classification** ➜] `{variant['significance']}`")
                
                
                # INTERACTIVE SECTION
                st.markdown("##### 💬 Ask the AI Agent")
                
                # 1. generate questions based on the specific variants
                default_questions = [
                    f"What is the clinical significance of {variant.get('gene', 'this')} variants?",
                    f"What are the common symptoms of {variant.get('condition', 'this disease')}?",
                    f"How is {variant.get('condition', 'this disease')} typically treated?",
                    "Summarize the mechanism of inheritance"
                ]
                
                # 2. let the user choose or type their own
                selected_question = st.selectbox(
                    "▼ Select A Question:",
                    default_questions,
                    key=f"q_select_{i}"
                )
                
                # 3. custom typing
                custom_question = st.text_input("💭 Ask GenomAI", key=f"q_custom_{i}")
                
                # use custom question if provided, otherwise use selected
                final_query = custom_question if custom_question else selected_question
                
                # 4. the "run" button
                if st.button(f"➤", key=f"btn_{i}"):
                    st.info(f"**Agent Query:** '{final_query}'")
                    
                    # call the RAG tool
                    with st.spinner(f"⚯ ͛ Reading literature for {audience}..."):
                        # pass the 'audience' from the sidebar
                        context = query_literature(final_query, audience=audience)
                        
                    # DISPLAY RESULT
                    st.markdown("### 🤖 AI Response")
                    st.success(context)
                
                # # the "Explain" button
                # if st.button(f"⌕ Research This Variant", key=f"btn_{i}"):
                    
                #     # construct a search query
                #     # if we have a 'gene' name (from simulated data), use it
                #     query = ""
                #     if 'gene' in variant:
                #         query = f"» What is the clinical significance of {variant['gene']} gene variants and {variant['condition']}?"
                #     else:
                #         # fallback query
                #         query = f"» Pathogenic variants in chromosome {variant['chrom']} position {variant['pos']}"
                    
                #     st.info(f"**Agent Query** >>> '{query}'")
                    
                #     # CALL THE RAG TOOL
                #     with st.spinner("⚯ ͛ Reading medical literature..."):
                #         context = query_literature(query, audience=audience)
                        
                #     # display results
                #     st.markdown("###🤖 AI Interpretation")
                #     st.write(context)
                #     st.success("📌 Evidence Retrieved from Local Knowledge Base.")