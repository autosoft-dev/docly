from typing import List


def filter_translation_output(translation_output: List[str]):
    output = []
    for i in range(0, len(translation_output)):
        if output:
            if translation_output[i] != output[-1]:
                output.append(translation_output[i])
        else:
            output.append(translation_output[i])
    return output