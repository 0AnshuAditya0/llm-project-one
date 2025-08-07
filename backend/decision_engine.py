from transformers import pipeline
from typing import List, Dict, Optional
import re

class AdvancedDecisionEngine:
    def __init__(self):
        self.qa_pipeline = pipeline(
            "question-answering",
            model="deepset/roberta-base-squad2",
            tokenizer="deepset/roberta-base-squad2"
        )
    
    def answer_questions(self, questions: List[str], context_chunks: List[Dict]) -> List[str]:
        """Answer questions using retrieved context"""
        answers = []
        for question in questions:
            # Find best context for this question
            best_context = self._select_best_context(question, context_chunks)
            # Generate answer
            answer = self._answer_with_transformer(question, best_context)
            answers.append(answer)
        return answers
    
    def _select_best_context(self, question: str, chunks: List[Dict]) -> str:
        """Select most relevant context chunks for the question"""
        # Sort chunks by relevance score
        sorted_chunks = sorted(chunks, key=lambda x: x['score'], reverse=True)
        # Combine top chunks (max 2000 tokens)
        context = ""
        token_count = 0
        for chunk in sorted_chunks[:5]:  # Top 5 chunks
            chunk_tokens = len(chunk['text'].split())
            if token_count + chunk_tokens < 2000:
                context += chunk['text'] + "\n\n"
                token_count += chunk_tokens
            else:
                break
        return context.strip()
    
    def _answer_with_transformer(self, question: str, context: str) -> str:
        """Answer using transformer model"""
        if not context:
            return "No relevant information found in the document."
        try:
            result = self.qa_pipeline(question=question, context=context)
            # Check confidence threshold
            if result['score'] < 0.1:
                return "The information is not clearly available in the document."
            return result['answer']
        except Exception as e:
            return f"Error processing question: {str(e)}"
    
    def extract_decision_rationale(self, question: str, answer: str, context: str) -> Dict:
        """Extract rationale for the decision"""
        return {
            'question': question,
            'answer': answer,
            'confidence': self._calculate_confidence(answer, context),
            'supporting_evidence': self._extract_evidence(answer, context),
            'clause_references': self._find_clause_references(context)
        }
    
    def _calculate_confidence(self, answer: str, context: str) -> float:
        """Calculate confidence score"""
        # Simple confidence based on answer length and context overlap
        if "not available" in answer.lower() or "not found" in answer.lower():
            return 0.2
        # Check for specific numbers, dates, or concrete facts
        if re.search(r'\d+', answer):
            return 0.8
        return 0.6
    
    def _extract_evidence(self, answer: str, context: str) -> List[str]:
        """Extract supporting evidence from context"""
        # Find sentences in context that contain key terms from answer
        answer_words = set(answer.lower().split())
        context_sentences = context.split('.')
        evidence = []
        for sentence in context_sentences:
            sentence_words = set(sentence.lower().split())
            overlap = len(answer_words.intersection(sentence_words))
            if overlap >= 2:  # At least 2 words overlap
                evidence.append(sentence.strip())
        return evidence[:3]  # Top 3 pieces of evidence
    
    def _find_clause_references(self, context: str) -> List[str]:
        """Find clause or section references"""
        patterns = [
            r'section\s+\d+',
            r'clause\s+\d+',
            r'article\s+\d+',
            r'paragraph\s+\d+',
            r'\d+\.\d+'
        ]
        references = []
        for pattern in patterns:
            matches = re.findall(pattern, context.lower())
            references.extend(matches)
        return list(set(references))