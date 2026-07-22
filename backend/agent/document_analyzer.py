import time

from retrieval.vector_store import vector_store
from llm.ollama_client import ollama_client


class DocumentAnalyzer:

    async def analyze_documents(self):
        print("========== USING DOCUMENT ANALYZER ==========")

        chunks = vector_store.get_all_chunks()

        # Check if any documents are indexed
        if not chunks:
            return {
                "analysis": "No indexed documents found."
            }

        print("\n========== FIRST CHUNK ==========\n")
        print(chunks[0]["text"][:1000])  # First 1000 characters
        print("\n========== END FIRST CHUNK ==========\n")

        # Select the first 20 chunks for analysis
        selected_chunks = chunks[:20]

        # Combine selected document chunks
        document_text = "\n\n".join(chunk["text"] for chunk in selected_chunks)

        print(f"Analyzing {len(selected_chunks)} of {len(chunks)} chunks")

        # Debug information
        print(f"Total Chunks Indexed: {len(chunks)}")
        print(f"Chunks Used: {len(selected_chunks)}")
        print(f"Total Characters: {len(document_text)}")
        print(f"Total Words: {len(document_text.split())}")

        analysis_prompt = f"""
        
IMPORTANT FORMAT RULES:
- Return plain Markdown only.
- Do NOT generate JSON.
- Do NOT generate XML.
- Do NOT generate YAML.
- Do NOT generate code blocks.
- Do NOT generate tables.
- Do NOT output structured data.
- Never invent numbers.
- Never modify percentages, dates, measurements, or statistics.
- Copy numerical values exactly as they appear in the document.
- If contradictory values exist, quote them exactly.

You are an expert defence intelligence analyst.

Analyze the provided document thoroughly and generate ONE structured report.

STRICT RULES:
- Generate exactly ONE report.
- Never repeat any section.
- Base every statement ONLY on the provided document.
- Never invent information.
- If information is unavailable, write exactly:
  Not mentioned in the document.
- Stop after the General Observations section.

DOCUMENT:
{document_text}

Return the report using EXACTLY the following format.

# Summary

Write a concise summary (60-100 words) describing:
- Purpose
- Problem addressed
- Main topics
- Overall conclusion

# Key Findings

Provide upto 5 bullet points.

Rules:
- Only important factual findings.
- Include technical observations, statistics and results.
- DO NOT include contradictions or ambiguities in this section.

# Inconsistencies

Identify EVERY contradiction, conflicting statement, conflicting numerical value, unsupported conclusion, or logical inconsistency.

Examples:
- Conflicting accuracy values
- Different experiment counts
- Conflicting dates
- Contradictory statements
- Conclusions that do not match the presented evidence

For each inconsistency:
- Mention both conflicting statements.
- Explain briefly why they conflict.

If none exist, write:

None found.

# Sentence Ambiguities

Identify vague, subjective, unsupported, or absolute statements.

Look specifically for statements containing words or phrases such as:
- always
- never
- every
- all
- highly secure
- extremely reliable
- performs well
- efficient
- robust
- suitable for all conditions
- significant improvement
- better performance

Also identify statements that:
- lack evidence
- are too broad
- are subjective
- cannot be verified
- make absolute claims

For each ambiguity:
- Quote the sentence or phrase.
- Explain why it is ambiguous.
- Suggest how it could be made clearer.

If none exist, write:

None found.

# General Observations

Provide 3–4 concise observations:
- Document organization
- Technical clarity
- Missing evidence
- Overall document quality

IMPORTANT:
1. Always produce ALL five sections.
2. Never leave any section blank.
3. Do NOT place inconsistencies inside Key Findings.
4. Every contradiction MUST appear under Inconsistencies.
5. Every vague or unsupported statement MUST appear under Sentence Ambiguities.
6. Use bullet points where appropriate.
7. End the response after General Observations.
"""

        start_time = time.time()

        print("\n========== PROMPT PREVIEW ==========\n")
        print(analysis_prompt[:2500])  # First 2500 characters
        print("\n========== END PREVIEW ==========\n")

        print(f"Prompt Length: {len(analysis_prompt)}")
        print(f"Document Length: {len(document_text)}")

        analysis = await ollama_client.generate_analysis(analysis_prompt)

        end_time = time.time()

        print(f"Document analysis completed in {end_time - start_time:.2f} seconds")

        print("\n========== DOCUMENT ANALYZER RESPONSE ==========\n")
        print(analysis)

        return {
            "analysis": analysis
        }


document_analyzer = DocumentAnalyzer()