from src.workflow import app, LessonState


topic = "Explain RAG using finding from specific reaserch study , including the study 's author, publication year and exact percentage improvement "


state: LessonState = {
    "topic": topic,
    "lesson": "",
    "feedback": "",
    "retry_count": 0,
    "evaluation": None
}


result = app.invoke(state)


print("=" * 60)
print("FINAL LESSON")
print("=" * 60)

print(result["lesson"])


print()
print("=" * 60)
print("EVALUATION")
print("=" * 60)


evaluation = result["evaluation"]

if evaluation is None:
    raise ValueError("Evaluation was not completed")


for check in evaluation.checks:

    if check.passed:
        status = "PASS"
    else:
        status = "FAIL"

    print(f"{check.name}: {status}")
    print(f"Reason: {check.reason}")

    if not check.passed:
        print(f"Fix: {check.fix}")

    print()


print("=" * 60)


if evaluation.passed:
    print("Overall: PASS")
else:
    print("Overall: FAIL")


print()
print("Retries used:", result["retry_count"])