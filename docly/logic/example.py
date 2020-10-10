import random


class Example(object):
    """A single training/test example."""
    def __init__(self,
                 idx,
                 source,
                 target,
                 ):
        self.idx = idx
        self.source = source
        self.target = target


def make_example(code_tokens):
    idx = random.randint(1, 100000)
    examples = []
    for ct in code_tokens:
        ex = Example(idx=idx,
                    source=" ".join(ct),
                    target="")
        examples.append(ex)
    return examples