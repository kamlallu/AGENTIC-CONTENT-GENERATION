import json
import os
from typing import TypedDict

from langgraph.graph import StateGraph, END

from src.generator import generate_lesson
from src.evaluator import evaluate_lesson, EvaluationResult


class LessonState(TypedDict):
    topic: str
    lesson: str
    feedback: str
    retry_count: int
    evaluation: EvaluationResult | None


def load_memory():

    try:
        with open("memory.json", "r") as file:
            return json.load(file)

    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_rejection_log(state: LessonState):

    evaluation = state["evaluation"]

    if evaluation is None:
        return

    failed_checks = []

    for check in evaluation.checks:

        if not check.passed:
            failed_checks.append({
                "check": check.name,
                "reason": check.reason,
                "fix": check.fix
            })

    if not failed_checks:
        return

    try:
        with open("rejection_log.json", "r") as file:
            logs = json.load(file)

    except (FileNotFoundError, json.JSONDecodeError):
        logs = []

    logs.append({
        "topic": state["topic"],
        "attempt": state["retry_count"] + 1,
        "status": "FAIL",
        "failures": failed_checks
    })

    with open("rejection_log.json", "w") as file:
        json.dump(logs, file, indent=4)


def update_memory(state: LessonState):

    evaluation = state["evaluation"]

    if evaluation is None:
        return

    memory = load_memory()

    for check in evaluation.checks:

        if not check.passed:

            memory.append({
                "topic": state["topic"],
                "problem": check.name,
                "reason": check.reason,
                "fix": check.fix
            })

    with open("memory.json", "w") as file:
        json.dump(memory, file, indent=4)


def build_memory_feedback():

    memory = load_memory()

    if not memory:
        return ""

    problem_counts = {}

    for item in memory:

        problem = item["problem"]

        if problem not in problem_counts:
            problem_counts[problem] = 0

        problem_counts[problem] += 1

    feedback = "\nPrevious problems found in lessons:\n"

    for problem, count in problem_counts.items():

        feedback += (
            f"- {problem} failed {count} time(s). "
            "Pay extra attention to this.\n"
        )

    return feedback


def generate(state: LessonState):

    memory_feedback = build_memory_feedback()

    feedback = state["feedback"]

    if memory_feedback:
        feedback = feedback + memory_feedback

    lesson = generate_lesson(
        state["topic"],
        feedback
    )

    return {
        "lesson": lesson
    }


def evaluate(state: LessonState):

    result = evaluate_lesson(
        state["topic"],
        state["lesson"]
    )

    return {
        "evaluation": result
    }


def prepare_retry(state: LessonState):

    evaluation = state["evaluation"]

    if evaluation is None:
        raise ValueError("Evaluation was not completed")

    failed_checks = []

    for check in evaluation.checks:

        if not check.passed:
            failed_checks.append(
                f"{check.name}: {check.reason}. Fix: {check.fix}"
            )

    feedback = "\n".join(failed_checks)

    return {
        "feedback": feedback,
        "retry_count": state["retry_count"] + 1
    }


def save_final_lesson(state: LessonState):

    os.makedirs("output", exist_ok=True)

    with open(
        "output/final_lesson.md",
        "w",
        encoding="utf-8"
    ) as file:
        file.write(state["lesson"])


def decide_next(state: LessonState):

    evaluation = state["evaluation"]

    if evaluation is None:
        raise ValueError("Evaluation was not completed")

    if evaluation.passed:
        return "save"

    if state["retry_count"] >= 2:
        return "save"

    return "retry"


workflow = StateGraph(LessonState)


workflow.add_node("generate", generate)
workflow.add_node("evaluate", evaluate)
workflow.add_node("save_log", save_rejection_log)
workflow.add_node("update_memory", update_memory)
workflow.add_node("prepare_retry", prepare_retry)
workflow.add_node("save_final", save_final_lesson)


workflow.set_entry_point("generate")


workflow.add_edge(
    "generate",
    "evaluate"
)


workflow.add_conditional_edges(
    "evaluate",
    decide_next,
    {
        "save": "save_final",
        "retry": "save_log"
    }
)


workflow.add_edge(
    "save_log",
    "update_memory"
)


workflow.add_edge(
    "update_memory",
    "prepare_retry"
)


workflow.add_edge(
    "prepare_retry",
    "generate"
)


workflow.add_edge(
    "save_final",
    END
)


app = workflow.compile()