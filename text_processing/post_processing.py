from typing import Dict, List


def parse_completion(completion: str) -> List[Dict[str, str]]:
    completion = "Q: " + completion
    qas = completion.split("\n\n")

    parsed_qas = []
    for qa in qas:
        split_qa = qa.split("\n")
        if len(split_qa) == 2:
            parsed_qas.append(
                {
                    "question": split_qa[0].strip().replace("Q: ", ""),
                    "answer": split_qa[1].strip().replace("A: ", ""),
                }
            )

    return parsed_qas
