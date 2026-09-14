import random

from app.database.database import (
    get_recent_topics,
)


TOPICS = {
    "Aptitude": [
        "Percentages",
        "Profit and Loss",
        "Simple Interest",
        "Compound Interest",
        "Ratio and Proportion",
        "Averages",
        "Time and Work",
        "Pipes and Cisterns",
        "Time Speed and Distance",
        "Problems on Trains",
        "Boats and Streams",
        "Mixtures and Allegations",
        "Partnership",
        "Age Problems",
        "Number System",
        "LCM and HCF",
        "Simplification",
        "Permutation and Combination",
        "Probability",
        "Data Interpretation",
    ],

    "Logical Reasoning": [
        "Number Series",
        "Alphabet Series",
        "Coding and Decoding",
        "Blood Relations",
        "Direction Sense",
        "Syllogisms",
        "Logical Venn Diagrams",
        "Seating Arrangement",
        "Puzzles",
        "Statement and Conclusion",
        "Statement and Assumption",
        "Analogy",
        "Classification",
        "Odd One Out",
        "Ranking and Ordering",
        "Calendar",
        "Clock",
        "Data Sufficiency",
    ],

    "DSA": [
        "Arrays",
        "Strings",
        "Linked Lists",
        "Stacks",
        "Queues",
        "Hashing",
        "Recursion",
        "Searching",
        "Sorting",
        "Binary Search",
        "Trees",
        "Binary Search Trees",
        "Heaps",
        "Graphs",
        "Graph Traversal",
        "Dynamic Programming",
        "Greedy Algorithms",
        "Time Complexity",
        "Space Complexity",
        "Two Pointers",
        "Sliding Window",
    ],
}


def get_all_topics():
    """
    Return all available (category, topic) pairs.
    """

    topics = []

    for category, category_topics in TOPICS.items():
        for topic in category_topics:
            topics.append((category, topic))

    return topics


def get_random_topic():
    """
    Select a topic that has not appeared recently.

    IMPORTANT:
    This function only SELECTS a topic.
    It does not record the topic as used.

    The topic should be recorded only after the quiz
    has been successfully generated and saved.
    """

    recent_topics = get_recent_topics(limit=10)

    recent_set = set(recent_topics)

    all_topics = get_all_topics()

    available_topics = [
        topic
        for topic in all_topics
        if topic not in recent_set
    ]

    # If every topic has been used recently, reset the
    # selection pool rather than failing.
    if not available_topics:
        available_topics = all_topics

    return random.choice(available_topics)


def get_daily_topic():
    """
    Return today's selected category and topic.
    """

    return get_random_topic()