from app.ai.schemas import Quiz


def format_quiz_for_telegram(quiz: Quiz) -> str:
    lines = []

    lines.append("🧠 DAILY APTITUDE CHALLENGE")
    lines.append("")
    lines.append("🎯 5 Questions • 1 Easy • 2 Moderate • 2 Hard")
    lines.append("")

    for q in quiz.questions:
        lines.append(
            f"Q{q.question_number}. [{q.difficulty}]"
        )
        lines.append(f"📚 {q.topic}")
        lines.append("")
        lines.append(q.question)
        lines.append("")

        for option in q.options:
            lines.append(option)

        lines.append("")

    lines.append("💡 Reply with your answers like:")
    lines.append("Q1-A, Q2-C, Q3-B, Q4-D, Q5-A")

    return "\n".join(lines)