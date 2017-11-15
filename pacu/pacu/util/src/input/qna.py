from ..compat.input import ask
from ..inspect.get import clsname
from ..str.poly import polymorphicStr

class QnA(object):
    def __init__(self, question, answer=NotImplemented):
        self.question = question
        self.answer = answer
    def __repr__(self):
        return '{}({!r}, answer={!r})'.format(
            clsname(self), str(self.question), self.answer)
    def ask(self, question=None):
        self.answer = ask(question or self.question)
        return self
    def persist(self, question=None):
        answer = None
        while not answer:
            answer = ask(question or self.question)
        self.answer = answer
        return self
    def __str__(self):
        return polymorphicStr(self.answer)

def test():
    qna = QnA('Name it: ').persist()
    print "You've named:", qna
