from transformers import pipeline

class DecisionEngine:
    def __init__(self):
        self.qa = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
    
    def generate_answer(self, question, relevant_chunks):
        context = " ".join(relevant_chunks)
        result = self.qa(question=question, context=context)
        return result['answer']