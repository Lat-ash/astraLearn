from groq import Groq
import re


class TestGeneratorAgent:
    def __init__(self, api_key, model_name="llama-3.1-8b-instant"):
        self.client = Groq(api_key=api_key)
        self.model = model_name

    def generate_single_mcq(self, text):
        # Use a reasonable chunk if text is too long, but don't truncate important content
        if len(text) > 6000:
            # Take beginning and end to capture content from all files
            text = text[:3000] + "\n...[content continues]...\n" + text[-3000:]

        prompt = f"""
Create ONE multiple-choice question based on the provided material from ALL files/chapters.

IMPORTANT RULES:
- Generate exactly 1 question with 4 choices (A, B, C, D)
- Make sure all choices are plausible but only one is correct
- Base everything strictly on the provided material from ALL files
- Draw questions from content across ALL chapters/files
- Keep explanation concise (2-3 lines)
- Ensure the question tests understanding of key concepts from the entire material

MATERIAL:
{text}

FORMAT EXACTLY LIKE THIS - NO DEVIATIONS:
QUESTION: [Your question here?]
A) [Choice A]
B) [Choice B]
C) [Choice C]
D) [Choice D]
CORRECT: [A/B/C/D]
EXPLANATION: [Brief explanation here in 2-3 lines]
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500,
            )

            res = response.choices[0].message.content

            # Debug: Print raw response
            print("RAW MCQ RESPONSE:", res)

            # Parse with more robust regex
            question_match = re.search(
                r"QUESTION:\s*(.+?)(?=\n[A-D]\)|\nCORRECT:|\nEXPLANATION:|\Z)",
                res,
                re.DOTALL,
            )
            choices = re.findall(r"^[A-D]\)\s*(.+)$", res, re.MULTILINE)
            correct_match = re.search(r"CORRECT:\s*([A-D])", res)
            explanation_match = re.search(
                r"EXPLANATION:\s*(.+?)(?=\n[A-D]\)|\nQUESTION:|\Z)", res, re.DOTALL
            )

            question = (
                question_match.group(1).strip()
                if question_match
                else "What is a key concept discussed across the material?"
            )
            choices = (
                choices
                if choices
                else ["Concept A", "Concept B", "Concept C", "Concept D"]
            )
            correct = correct_match.group(1) if correct_match else "A"
            explanation = (
                explanation_match.group(1).strip()
                if explanation_match
                else "This tests your understanding of key concepts from the provided material."
            )

            # Ensure we have exactly 4 choices
            while len(choices) < 4:
                choices.append(f"Option {chr(68 - len(choices))}")

            return question, choices[:4], correct, explanation

        except Exception as e:
            print(f"Error generating MCQ: {e}")
            return (
                "What is a key concept discussed across all the provided material?",
                ["Concept A", "Concept B", "Concept C", "Concept D"],
                "A",
                "Review the material to understand the key concepts discussed across all files.",
            )
