#  Agentic Content Generation

This is my take-home assignment for the GenAI Engineer role at NxtWave.

The task was to build a system which can generate a beginner lesson for a topic, check the lesson, and improve it if there is any problem.

For this assignment I used the topic **Introduction to RAG**.

## What I built

The workflow is:

Topic
↓
Generate lesson
↓
Check lesson
↓
If PASS → Save
If FAIL → Take feedback → Generate again

I used LangGraph for this flow.

The generator creates the lesson and the evaluator checks the lesson.

The evaluator checks 7 things:

1. Is the information correct?
2. Is it properly grounded?
3. Is it easy for a beginner to understand?
4. Does it have a simple example?
5. Are technical words explained?
6. Does it cover what RAG is, why it is useful and how it works?
7. Is the lesson easy to follow?

Every check is either PASS or FAIL.

If a check fails, the evaluator gives the reason and a possible fix. This feedback is passed to the generator for the next attempt.

I have kept a limit of 2 retries so that the workflow does not keep running.

## Files

`main.py`  
Starts the workflow and gives the topic.

`src/generator.py`  
Creates the lesson.

`src/evaluator.py`  
Checks the lesson using the 7 checks.

`src/workflow.py`  
Connects the generator and evaluator and handles the retry.

`rejection_log.json`  
Stores the failed attempts and the reasons.

`memory.json`  
Stores previous problems so they can be used in future runs.

`output/final_lesson.md`  
Stores the final accepted lesson.

## How I tested it

I tested the system in two ways.

### Test 1

Input:

`Explain RAG.`

The lesson passed on the first attempt.

Result:

`PASS`

Retries:

`0`

### Test 2

I used a request which asks for specific research information so that I could test the evaluator and retry flow.

The flow was:

Generate
↓
Fail
↓
Save the failure
↓
Send the feedback to generator
↓
Generate again
↓
Pass

Retries:

`1`

This helped me check that the system is actually using the evaluator feedback instead of only generating the lesson once.

## Tech used

- Python
- LangGraph
- LangChain
- Groq
- Pydantic
- JSON

## How to run

Create the virtual environment:

```bash
python -m venv venv
