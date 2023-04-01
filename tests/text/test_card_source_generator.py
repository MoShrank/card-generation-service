from text.CardSourceGenerator import CardSourceGenerator


def test_find_sentence_indices():
    source_generator = CardSourceGenerator()

    test_cases = [
        {
            "text": "This is a test sentence. It contains a substring that we want to find. The substring is here.",
            "substring_start": 29,
            "substring_end": 38,
            "expected_output": (25, 70),
        },
        {
            "text": "This is a test sentence. We want to find the sentence that starts with the substring",
            "substring_start": 0,
            "substring_end": 4,
            "expected_output": (0, 24),
        },
        {
            "text": "This is a sentence with a question mark? It contains the substring we are looking for.",
            "substring_start": 0,
            "substring_end": 5,
            "expected_output": (0, 40),
        },
    ]
    for i, test_case in enumerate(test_cases):
        text = test_case["text"]
        substring_start = test_case["substring_start"]
        substring_end = test_case["substring_end"]
        expected_output = test_case["expected_output"]
        output = source_generator._find_sentence_indices(
            text, substring_start, substring_end
        )
        assert (
            output == expected_output
        ), f"Failed test case {i}. Expected {expected_output}, but got {output}"
