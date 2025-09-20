"""
assignment_quiz_generator.py

A small Streamlit app that generates 2 assignment prompts and 3 multiple-choice
questions (with options and answers) from a provided document or topic.

Usage:
    streamlit run assignment_quiz_generator.py

Author: [Isam Balghari]
"""

from __future__ import annotations

import re
import random
from collections import Counter
from typing import List, Tuple

import streamlit as st


def split_sentences(text: str) -> List[str]:
    """Split text into sentences using simple punctuation rules.

    Args:
        text: The input text to split.

    Returns:
        A list of non-empty sentences.
    """
    # Normalize whitespace and split on sentence-ending punctuation
    text = re.sub(r"\s+", " ", text.strip())
    parts = re.split(r"(?<=[.!?])\s+", text)
    sentences = [p.strip() for p in parts if p.strip()]
    return sentences


def extract_keywords(text: str, top_n: int = 8) -> List[str]:
    """Return a list of simple keywords (most frequent non-stop words).

    This function uses a tiny built-in stopword list so you don't need
    any external NLP libraries.

    Args:
        text: Input text to analyze.
        top_n: Number of top keywords to return.

    Returns:
        A list of keywords sorted by frequency.
    """
    stopwords = {
        "the",
        "and",
        "is",
        "in",
        "to",
        "of",
        "a",
        "an",
        "for",
        "on",
        "with",
        "that",
        "this",
        "are",
        "as",
        "by",
        "from",
        "be",
        "or",
        "it",
        "we",
        "you",
        "they",
        "which",
    }
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    candidates = [w for w in words if w not in stopwords]
    counts = Counter(candidates)
    keywords = [w for w, _ in counts.most_common(top_n)]
    return keywords


def make_assignment_prompts(sentences: List[str], keywords: List[str]) -> List[str]:
    """Generate two assignment-style essay prompts.

    Strategy:
    - Use long sentences (if available) to surface ideas.
    - Use top keywords to build a comparative or exploratory prompt.

    Args:
        sentences: List of sentences from the text.
        keywords: List of extracted keywords.

    Returns:
        Exactly two assignment prompt strings.
    """
    prompts: List[str] = []
    long_sents = sorted(sentences, key=len, reverse=True)

    if long_sents:
        example = long_sents[0][:240].rstrip()
        prompts.append(
            f"Read the following excerpt and write a 800-1200 word essay: \"{example}\". "
            "Discuss its main claims and implications, and relate them to broader "
            "concepts from the document."
        )
    else:
        prompts.append(
            "Write an 800-1200 word essay summarising the main ideas of the "
            "provided text, identifying two areas for further investigation."
        )

    # second prompt uses keywords to form a comparative / evaluative question
    if len(keywords) >= 2:
        k1, k2 = keywords[0], keywords[1]
        prompts.append(
            f"Compare and contrast the roles of '{k1}' and '{k2}' as presented in "
            "the text. In your answer, evaluate strengths and weaknesses of the "
            "arguments and suggest practical applications or experiments to test them."
        )
    else:
        prompts.append(
            "Identify two central themes from the document and critically evaluate "
            "their significance. Provide examples and suggest follow-up questions."
        )

    return prompts


def generate_mcqs(keywords: List[str]) -> List[Tuple[str, List[str], int]]:
    """Create 3 multiple-choice questions from keywords.

    Each question is a tuple: (question_text, options, index_of_correct).

    Args:
        keywords: List of keywords to use as correct answers.

    Returns:
        A list of three MCQs.
    """
    mcqs: List[Tuple[str, List[str], int]] = []
    pool = keywords[:] or ["concept", "method", "result", "theory", "model"]

    # Ensure we have enough distractors by using variations of keywords
    all_terms = list(dict.fromkeys(pool + [k + "s" for k in pool]))
    random.shuffle(all_terms)

    for i in range(3):
        correct = pool[i % len(pool)]
        # build distractors
        distractors = []
        tries = 0
        while len(distractors) < 3 and tries < 30:
            candidate = random.choice(all_terms)
            if candidate != correct and candidate not in distractors:
                distractors.append(candidate)
            tries += 1

        options = distractors[:3] + [correct]
        random.shuffle(options)
        correct_index = options.index(correct)
        question = (
            f"Which of the following best describes the term '{correct}' as used "
            "in the document?"
        )
        mcqs.append((question, options, correct_index))

    return mcqs


def format_mcq_display(mcqs: List[Tuple[str, List[str], int]]) -> str:
    """Return a formatted string suitable for display with Streamlit.

    Args:
        mcqs: List of MCQ tuples.

    Returns:
        A multi-line string with questions, options and answers.
    """
    lines: List[str] = []
    for i, (q, opts, ans_idx) in enumerate(mcqs, start=1):
        lines.append(f"Q{i}. {q}")
        for j, opt in enumerate(opts, start=1):
            lines.append(f"   {chr(64+j)}. {opt}")
        lines.append(f"   Answer: {chr(65+ans_idx)}")
        lines.append("")
    return "\n".join(lines)


def generate_from_text(text: str) -> Tuple[List[str], List[Tuple[str, List[str], int]]]:
    """Run the full lightweight pipeline: parse, extract, and generate.

    Args:
        text: Input document or topic string.

    Returns:
        A tuple (assignments, mcqs).
    """
    sentences = split_sentences(text)
    keywords = extract_keywords(text, top_n=8)
    assignments = make_assignment_prompts(sentences, keywords)
    mcqs = generate_mcqs(keywords)
    return assignments, mcqs


def main() -> None:
    """Streamlit front-end: accept input and show generated questions.

    Run with: `streamlit run assignment_quiz_generator.py`.
    """
    st.set_page_config(page_title="Assignment & Quiz Generator")
    st.title("Assignment & Quiz Generator")

    st.write(
        "Paste a document or a short topic description below. The app will "
        "produce 2 assignment prompts and 3 multiple-choice questions."
    )

    text = st.text_area("Input document or topic", height=280)

    if st.button("Generate"):
        if not text.strip():
            st.warning("Please provide some input text or a topic to continue.")
            return

        assignments, mcqs = generate_from_text(text)

        st.header("Assignment Prompts (2)")
        for idx, p in enumerate(assignments, start=1):
            st.markdown(f"**Assignment {idx}:** {p}")

        st.header("Multiple Choice Quiz (3)")
        for idx, (q, opts, ans_idx) in enumerate(mcqs, start=1):
            st.markdown(f"**Q{idx}.** {q}")
            for j, opt in enumerate(opts, start=1):
                st.write(f"- {chr(64+j)}. {opt}")
            st.info(f"Correct answer: {chr(65+ans_idx)}")

        st.success("Generation complete. Edit the input and re-click Generate to try again.")


if __name__ == "__main__":
    main()
