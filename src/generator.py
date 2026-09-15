import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq


load_dotenv()


model_name = os.getenv("GROQ_MODEL")

if not model_name:
    raise ValueError("GROQ_MODEL is missing from .env")


model = ChatGroq(
    model=model_name,
    temperature=0.3
)


def generate_lesson(topic, feedback=""):

    prompt = f"""
Create a beginner lesson about this topic:

{topic}

The learner is a 12th-grade graduate from India with limited English
and no previous AI knowledge.

The lesson should explain:

1. What it is
2. Why it matters
3. How it works
4. A simple real-world example
5. Important terms in simple language
6. One limitation
  

Use simple English and short sentences.

Explain technical words before using them.

Teach the topic step by step.

Previous feedback:
{feedback}

If there is previous feedback, improve the lesson based on it.

Write only the lesson.
"""

    response = model.invoke(prompt)

    return response.content