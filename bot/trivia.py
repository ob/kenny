import csv
import random
from typing import List, Dict


def load_questions(path: str) -> List[Dict[str, str]]:
    """
    Load trivia questions from a CSV file with headers: category, question, answer.
    Returns a list of dicts.
    """
    questions: List[Dict[str, str]] = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Normalize keys and strip whitespace
            questions.append({
                'category': row.get('category', '').strip(),
                'question': row.get('question', '').strip(),
                'answer': row.get('answer', '').strip(),
            })
    return questions


def pick_question(questions: List[Dict[str, str]]) -> Dict[str, str]:
    """
    Randomly select a question dict from the list.
    """
    return random.choice(questions)
