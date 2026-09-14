import re


def parse_answers(text: str) -> dict[int, str]:
    """
    Parse answers from messages such as:

    Q1-A, Q2-C, Q3-B, Q4-D, Q5-A

    Also accepts:

    Q1 A Q2 C Q3 B Q4 D Q5 A
    """

    pattern = r"Q\s*(\d+)\s*[-:.\s]\s*([ABCD])"

    matches = re.findall(pattern, text.upper())

    answers = {}

    for question_number, answer in matches:
        answers[int(question_number)] = answer

    return answers


def is_valid_answer_submission(answers: dict[int, str]) -> bool:
    """
    Check whether the submission contains exactly
    questions 1 through 5.
    """

    return set(answers.keys()) == {1, 2, 3, 4, 5}


if __name__ == "__main__":
    test_message = "Q1-A, Q2-C, Q3-B, Q4-D, Q5-A"

    parsed = parse_answers(test_message)

    print("Parsed answers:")
    print(parsed)

    print("\nValid submission:")
    print(is_valid_answer_submission(parsed))