import agreement_comparision
import data_extraction
import json

# if __name__ == "__main__":

#     #  CHANGE THIS to your new agreement PDF
#     unseen_file = "Standard Contractual Clauses template.pdf"

#     # Step 1: Identify the type of agreement
#     agreement_type = agreement_comparision.document_type(unseen_file)
#     print("Document Type:", agreement_type)

#     # Step 2: Branch based on agreement type
#     if agreement_type == "Data Processing Agreement":
#         # Extract & summarise clauses
#         unseen_data = data_extraction.Clause_extraction_with_summarization(unseen_file)



#         # Load trusted GDPR DPA template
#         with open("dpa_sum.json", "r", encoding="utf-8") as f:
#             template_data = json.load(f)

#         # Compare agreements
#         result = agreement_comparision.compare_agreements(unseen_data, template_data)

#         # Save comparison result as JSON
#         # with open("comparison_result.json", "w", encoding="utf-8") as f:
#         #     f.write(result)
#         # print("\n✅ Comparison saved to comparison_result.json")
#         print(result)

#     elif agreement_type == "Standard Contractual Clauses":
#         # Extract SCC clauses
#         unseen_data = data_extraction.Clause_extraction_with_summarization(unseen_file)
#         # print("\nExtracted SCC clauses:\n", unseen_data)
        
#           # Load trusted GDPR DPA template
#         with open("dpa_sum.json", "r", encoding="utf-8") as f:
#             template_data = json.load(f)

#         # Compare agreements
#         result = agreement_comparision.compare_agreements(unseen_data, template_data)

#         # # Save comparison result as JSON
#         # with open("comparison_result.json", "w", encoding="utf-8") as f:
#         #     f.write(result)
#         # print("\n✅ Comparison saved to comparison_result.json")

#         print(result)

   
#     elif agreement_type == "Controller-to-Controller Agreement":
#         # Extract SCC clauses
#         unseen_data = data_extraction.Clause_extraction_with_summarization(unseen_file)
#         # print("\nExtracted SCC clauses:\n", unseen_data)
        
#           # Load trusted GDPR DPA template
#         with open("dpa_sum.json", "r", encoding="utf-8") as f:
#             template_data = json.load(f)

#         # Compare agreements
#         result = agreement_comparision.compare_agreements(unseen_data, template_data)

#         # # Save comparison result as JSON
#         # with open("comparison_result.json", "w", encoding="utf-8") as f:
#         #     f.write(result)
#         # print("\n✅ Comparison saved to comparison_result.json")

#         print(result)

        
#     elif agreement_type == "Joint Controller Agreement":
#         # Extract SCC clauses
#         unseen_data = data_extraction.Clause_extraction_with_summarization(unseen_file)
#         # print("\nExtracted SCC clauses:\n", unseen_data)
        
#           # Load trusted GDPR DPA template
#         with open("dpa_sum.json", "r", encoding="utf-8") as f:
#             template_data = json.load(f)

#         # Compare agreements
#         result = agreement_comparision.compare_agreements(unseen_data, template_data)

#         # # Save comparison result as JSON
#         # with open("comparison_result.json", "w", encoding="utf-8") as f:
#         #     f.write(result)
#         # print("\n✅ Comparison saved to comparison_result.json")

#         print(result)

#     if agreement_type == "Processor-to-Subprocessor Agreement":
#         # Extract & summarise clauses
#         unseen_data = data_extraction.Clause_extraction_with_summarization(unseen_file)



#         # Load trusted GDPR DPA template
#         with open("dpa_sum.json", "r", encoding="utf-8") as f:
#             template_data = json.load(f)

#         # Compare agreements
#         result = agreement_comparision.compare_agreements(unseen_data, template_data)

#         # Save comparison result as JSON
#         # with open("comparison_result.json", "w", encoding="utf-8") as f:
#         #     f.write(result)
#         # print("\n✅ Comparison saved to comparison_result.json")
#         print(result)


import streamlit as st
import schedule
import time
import threading
import scraping
import notification

def run_scheduler():

    # call call_scrape_funtion function every night at 12 am
    # schedule.every().day.at("00:00").do(scraping.call_scrape_funtion)

    # these are for testing purpose
    # for testing part we will call scheduler in every 10 seconds # schedule.every(10).seconds.do(scraping.call_scrape_funtion)
    schedule.every(1).minutes.do(scraping.call_scrape_funtion)

    while True:
        schedule.run_pending()
        time.sleep(60) #check every 5 seconds

# start scheduler in background thread so streamlit does not block
threading.Thread(target=run_scheduler, daemon=True).start()
if __name__ == "__main__":

    try:
        # Mapping of agreement type to respective JSON file
        AGREEMENT_JSON_MAP = {
            "Data Processing Agreement": "json_files/dpa.json",
            "Joint Controller Agreement": "json_files/jca.json",
            "Controller-to-Controller Agreement": "json_files/c2c.json",
            "Processor-to-Subprocessor Agreement": "json_files/subprocessor.json",
            "Standard Contractual Clauses": "json_files/scc.json"
        }

        st.title("📄 Contract Compliance Checker")

        # File upload
        uploaded_file = st.file_uploader("📤 Upload an agreement (PDF only)", type=["pdf"])

        if uploaded_file is not None:
            with open("temp_uploaded.pdf", "wb") as f:
                f.write(uploaded_file.read())

            st.info("🔍 Analyzing your document...")

            # Step 1: Identify the type of agreement
            agreement_type = agreement_comparision.document_type("temp_uploaded.pdf")
            st.write("**✅ Detected Document Type:**", agreement_type)

            if agreement_type in AGREEMENT_JSON_MAP:
                # Step 2: Extract clauses
                unseen_data = data_extraction.Clause_extraction_with_summarization("temp_uploaded.pdf")

                st.success("**📑 Clause Extraction Completed!**")
                # Step 3: Load the respective template JSON
                template_file = AGREEMENT_JSON_MAP[agreement_type]
                with open(template_file, "r", encoding="utf-8") as f:
                    template_data = json.load(f)

                # Step 4: Compare agreements
                result = agreement_comparision.compare_agreements(unseen_data, template_data)

                # Show results
                st.subheader("📊 Comparison Result")
                st.write(result)

            else:
                st.error(f"❌ No template found for detected type: {agreement_type}")

        else:
            st.warning("📂 Please upload a PDF file to start compliance checking.")

    except  Exception as e:
        print("Error Occured in document comparision", e)
        st.write("Hello, Error here!!")
        error_type = type(e).__name__ 
        notification.send_notification("Error Occured in document comparision", f"Error is {e}")
        # notification.send_notification(f"⚠️ Compliance Checker Error: {error_type}", f"Error is {e}")
