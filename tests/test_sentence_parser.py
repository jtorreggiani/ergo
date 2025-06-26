from src.sentence_parser import split_sentences

def test_sentence_parser():
    text = """
    Functional requirements describe expected behaviors (i.e. outputs). Non-functional requirements specify issues like portability, security, maintainability, reliability, scalability, performance, reusability, and flexibility. They are classified into the following types: interface constraints, performance constraints (such as response time, security, storage space, etc.), operating constraints, life cycle constraints (maintainability, portability, etc.), and economic constraints. Knowledge of how the system or software works is needed when it comes to specifying non-functional requirements. Domain requirements have to do with the characteristic of a certain category or domain of projects. [ 35 ]"
    """

    sentences = split_sentences(text)
    expected_sentence = "Functional requirements describe expected behaviors (i.e. outputs)."
    assert sentences[0].strip() == expected_sentence

def test_aka_sentence_parser():
    text = "Software construction typically involves programming (a.k.a. coding), unit testing , integration testing , and debugging so as to implement the design. [ 1 ] [ 6 ] \"Software testing is related to, but different from, ... debugging\". [ 6 ] Testing during this phase is generally performed by the programmer and with the purpose to verify that the code behaves as designed and to know when the code is ready for the next level of testing. [ citation needed ]"

    sentences = split_sentences(text)
    expected_sentence = "Software construction typically involves programming (a.k.a. coding), unit testing, integration testing, and debugging so as to implement the design."
    assert sentences[0] == expected_sentence
