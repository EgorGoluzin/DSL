# from dsl_info import *


# def __RemoveNones(attributes):
#     return [attribute for attribute in attributes if attribute]


# def __CreatePairs(attributes):
#     attributes = __RemoveNones(attributes)
#     if len(attributes) % 2 != 0:
#         raise Exception("Failed to make pairs - odd number of attributes")
#     res = []
#     for i in range(0, len(attributes), 2):
#         res.append((attributes[i], attributes[i + 1]))
#     return res


# def __CheckOne(attributes):
#     attributes = __RemoveNones(attributes)
#     if len(attributes) != 1:
#         raise Exception("Expect 1 attribute")
#     return attributes[0]


# attributesMap = {
#     Nonterminal.AXIOM_BLOCK : __CheckOne,
#     Nonterminal.TERMINALS_BLOCK : __CreatePairs,
#     Nonterminal.KEYS_BLOCK : __RemoveNones,
#     Nonterminal.NONTERMINALS_BLOCK : __RemoveNones,
# }


from dsl_info import *


def __RemoveNones(attributes):
    return [attribute for attribute in attributes if attribute]


def __Multiple(attributes):
    attributes = __RemoveNones(attributes)
    res = 1
    for num in attributes:
        res *= num
    return res


def __Add(attributes):
    attributes = __RemoveNones(attributes)
    res = 0
    for num in attributes:
        res += num
    return res


attributesMap = {
    Nonterminal.TERM : __Multiple,
    Nonterminal.EXPRESSION : __Add,
    Nonterminal.EXPRESSIONS : __RemoveNones
}

