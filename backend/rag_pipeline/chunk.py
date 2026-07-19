import re
from ..config import MAX_CHUNK_SIZE, OVERLAP_SIZE


# Chunker
# Args - Text
# Return - List of text chunks with sentence-aware overlap

def _backtrack_to_word_boundary(text, start, min_start):
    while start > min_start and start < len(text) and not re.match(r"\s", text[start - 1]):
        start -= 1
    return start


def chunk_doc(text):
    chunks = []
    start = 0

    sentence_pattern = r'[.!?]["\']?(?=\s|$)'

    while start < len(text):
        if len(text) - start <= MAX_CHUNK_SIZE:
            chunks.append(text[start:].strip())
            break

        end = start + MAX_CHUNK_SIZE
        chunk = text[start:end]
        sentence_ends = list(re.finditer(sentence_pattern, chunk))

        if sentence_ends:
            split_index = start + sentence_ends[-1].end()
            overlap_start = start + sentence_ends[-2].end() if len(sentence_ends) >= 2 else split_index
            overlap_length = split_index - overlap_start

            if overlap_length > OVERLAP_SIZE:
                desired_start = split_index - OVERLAP_SIZE
                desired_start = max(desired_start, overlap_start)
                overlap_start = _backtrack_to_word_boundary(text, desired_start, overlap_start)

            chunks.append(text[start:split_index].strip())
            start = overlap_start
        else:
            chunks.append(text[start:end].strip())
            start = end

    return chunks


if __name__ == "__main__":
    sentence = "Artificial intelligence (AI) has transitioned from a futuristic concept into an essential tool in modern medicine. This shift is changing how doctors diagnose diseases, manage patient care, and develop new treatments. As medical data grows exponentially, machine learning algorithms help healthcare professionals make faster, more accurate decisions.Historically, medical data was difficult to organize and analyze quickly. Patient files, lab results, and imaging scans were stored in silos across different systems. The integration of advanced computational power has solved this bottleneck. AI systems can now process terabytes of unstructured medical data in seconds, highlighting critical patterns that might escape the human eye.Diagnostic radiology is one of the clearest examples of this technology in action. Algorithms trained on millions of clinical images can identify anomalies like tumors or fractures with high precision. In many cases, these systems detect early-stage cellular changes before they become visible to human radiologists. This early detection drastically improves patient survival rates for aggressive diseases like cancer.Beyond diagnostics, AI is streamlining hospital workflows and reducing administrative burdens. Electronic health records (EHRs) often require hours of manual data entry from nurses and physicians. Natural language processing (NLP) tools can now listen to doctor-patient consultations and automatically update medical charts. This reduction in paperwork allows clinicians to spend more face-to-face time with patients, restoring a human element to medical care.The pharmaceutical industry is also experiencing an AI-driven revolution. Developing a new drug traditionally takes over a decade and costs billions of dollars. Machine learning models accelerate this timeline by simulating how billions of chemical compounds interact with specific target proteins. This predictive modeling narrows down potential drug candidates in days rather than years, speeding up clinical trials for rare or emerging diseases.However, the rapid adoption of AI in medicine introduces significant ethical and practical challenges. Data privacy is a primary concern, as medical records are highly sensitive and attractive targets for cyberattacks. Furthermore, machine learning models are only as good as the data used to train them. If training sets lack diversity, the AI may produce biased or inaccurate recommendations for underrepresented demographics.Another hurdle is the black box problem of deep learning algorithms. It can be difficult for developers and clinicians to understand exactly how an AI arrived at a specific diagnostic conclusion. In high-stakes medical scenarios, doctors are hesitant to trust a machine's recommendation without a clear, transparent explanation of its underlying logic.To fully realize the benefits of healthcare AI, regulatory bodies must establish strict guidelines for safety, accountability, and fairness. Standardizing data formats across hospitals will ensure that models operate reliably across different populations. Additionally, medical schools are beginning to integrate data science into their curricula, preparing future doctors to work alongside digital assistants.Artificial intelligence will not replace human physicians. Instead, it serves as a powerful collaborator that handles data management, pattern recognition, and routine administrative tasks. By combining the emotional intelligence and ethical judgment of human doctors with the analytical speed of machines, modern medicine can achieve unprecedented levels of efficiency and patient care."
    chunks = chunk_doc(sentence)
    for chunk in chunks:
        print(chunk)
        print("---")
