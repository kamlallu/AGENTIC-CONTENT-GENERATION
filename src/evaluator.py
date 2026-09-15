import os
from typing import cast

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import BaseModel


load_dotenv()


model_name = os.getenv("GROQ_MODEL")

if not model_name:
    raise ValueError("GROQ_MODEL is missing from .env")


model = ChatGroq(
    model=model_name,
    temperature=0
)


class CheckResult(BaseModel):
    name: str
    passed: bool
    reason: str
    fix: str


class EvaluationResult(BaseModel):
    passed: bool
    checks: list[CheckResult]


def evaluate_lesson(topic, lesson) -> EvaluationResult:

    prompt = f"""
Check this lesson for a beginner.

Topic:
{topic}

Lesson:
{lesson}

Available supporting context:
Only the information explicitly provided in the topic and lesson.
No external research papers, documents, or sources have been provided
to the evaluator.

Check these points:

1. Is the information correct?

2. Is it easy for a beginner with limited English to understand?

3. Does it use a useful example?

4. Are important technical words explained?

5. Does it explain what it is, why it matters, and how it works?

6. Does the lesson have a clear flow?

7. Grounding and unsupported claims:
   - General factual explanations that are appropriate for teaching the
     topic are allowed.
   - Clearly labelled hypothetical examples are allowed.
   - Do not require citations for normal, well-established explanations.
   - Be strict with specific claims such as exact statistics, percentages,
     research findings, named studies, authors, dates, or numerical
     comparisons.
   - If the lesson makes a specific research or numerical claim and the
     supporting source or information was not provided in the available
     context, mark this check as FAIL.
   - Do not assume a claim is supported just because it sounds plausible
     or because you may know it from your own knowledge.
   - If the lesson invents information or presents a clearly false claim
     as factual, mark this check as FAIL.
   - Explain exactly what is unsupported or incorrect and give a simple fix.

For each point, give PASS or FAIL.

Do not give partial scores.

If something fails, explain the problem and give a simple fix.

Return all 7 checks.

The final result is PASS only if all applicable checks pass.
"""

    evaluator = model.with_structured_output(
        EvaluationResult,
        method="json_schema"
    )

    result = evaluator.invoke(prompt)

    return cast(EvaluationResult, result)