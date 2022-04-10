from typing import Dict, List


def parse_completion(completion: str) -> List[Dict[str, str]]:
    completion = "Q: " + completion
    qas = completion.split("Q:")

    parsed_qas = []
    for qa in qas:
        qa = qa.split("A:")
        if len(qa) == 2:
            parsed_qas.append({"question": qa[0].strip(), "answer": qa[1].strip()})

    return parsed_qas
