#!/usr/bin/env python3

from typing import Any
from enum import Enum, unique, auto
from typing import Tuple

class Obj():
    head: Any


    def __init__(self, init_head: Any = None):
        self.head = init_head


    def __str__(self) -> str:
        return "Object"


    def __repr__(self) -> str:
        return "Object"


    def eval(self):
        return Obj(self.head)


class Nil(Obj):
    head = None


    def __init__(self, init_head = None):
        self.head = init_head


    def is_nil(val: Any):
        return True if type(val) is Nil else False


    def __str__(self) -> str:
        return "()"


    def __repr__(self) -> str:
        return "()"


    def eval(self):
        return Nil()


nil = Nil()


class Num(Obj):
    head: float | int = 0

    def __init__(self, init_head: float | int = 0):
        if type(init_head) is int:
            self.head = init_head
        if type(init_head) is float:
            self.head = int(init_head) if int(init_head) - init_head == 0 else init_head


    def __str__(self) -> str:
        return f"{self.head}"


    def __repr__(self) -> str:
        return f"Number {self.head}"


    def __add__(self, other: Obj):
        if type(other) is Num:
            return Num(self.head + other.head)
        elif type(other) is int or float:
            return Num(self.head + other)
        elif type(other) is None:
            return Num(self.head)
        else:
            print(type(other))
            assert False


    def __sub__(self, other: Obj):
        if type(other) is Num:
            return Num(self.head - other.head)
        elif type(other) is int or float:
            return Num(self.head - other)
        elif type(other) is None:
            return Num(self.head)
        else:
            print(type(other))
            assert False


    def eval(self):
        return Num(self.head)


class Sym(Obj):
    head: str = ""

    def __init__(self, init_head: str = ""):
        self.head = init_head


    def __str__(self) -> str:
        return f"{self.head}"


    def __repr__(self) -> str:
        return f"symbol {self.head}"


    def eval(self):
        return Sym(self.head)


class Fn(Obj):
    head: str = ""
    tail: Obj = nil

    def __init__(self, init_head):
        self.head = init_head

    def __str__(self) -> str:
        return f"{self.head}"


    def __repr__(self) -> str:
        return f"fn {self.head}"


    def buildin_sum(self, obj: Obj) -> Num:
            if type(obj) is Num:
                return obj
            elif type(obj) is Cons:
                return obj.head + self.buildin_sum(obj.tail)
            elif type(obj) is Nil:
                return Num(0)
            else:
                print(f"{type(obj)}: {type(self.head)} -> {type(self.tail)}")
                assert False


    def buildin_sub(self, obj: Obj) -> Num:
            if type(obj) is Num:
                return obj
            elif type(obj) is Cons:
                if type(obj.tail) is Nil: return Num(obj.head.head * -1)
                else: return obj.head - self.buildin_sum(obj.tail)
            elif type(obj) is Nil:
                return Num(0)
            else:
                print(f"{type(obj)}: {type(self.head)} -> {type(self.tail)}")
                assert False


    def buildin_quit(self, obj):
        import os

        if type(obj) is Cons and type(obj.head) is Nil or type(obj) is Nil:
            os._exit(0)
        elif type(obj) is Cons:
            os._exit(obj.head.eval().head)


    def eval(self):
        match self.head:
            case '+':
                return self.buildin_sum(self.tail)
            case '-':
                return self.buildin_sub(self.tail)
            case "quit":
                return self.buildin_quit(self.tail)
            case _:
                assert False
                return nil


class Cons(Obj):
    head: Obj = nil
    tail: Obj = nil


    def __init__(self, init_head: Obj = nil, init_tail: list[Obj] | Obj = nil):
        self.head = init_head

        if type(init_tail) is list:
            match len(init_tail):
                case 0:
                    self.tail = nil
                case 1:
                    self.tail = init_tail[0]
                case _:
                    self.tail = Cons(init_tail[0], init_tail[1:])
        else:
            self.tail = init_tail


    def __str__(self) -> str:
        def str_help(self, acc: bool) -> str:
            result: str = ""
            if type(self.tail) is Cons:
                result = str(self.head) + ' ' + str_help(self.tail, False)
                return '(' + result + ')' if acc else result
            else:
                result = str(self.head) if self.tail == nil else str(self.head) + " . " + str(self.tail)
                return '(' + result + ')' if acc else result

        return str_help(self, True)


    def __repr__(self) -> str:
        return f"{repr(self.head)} -> {repr(self.tail)}"


    def eval(self):
        if type(self.head) is Fn and type(self.tail) is Cons or type(self.tail) is Nil:
            self.head.tail = self.tail
            return self.head.eval()
        else:
            print(f"invalid list `{self}`")
            assert False


class Parser():
    class Tk(Enum):
        l_parenthe  = auto()
        r_parenthe  = auto()
        number      = auto()
        symbol      = auto()
        fn          = auto()
        EOF         = auto()
        err         = auto()


    tk_last: Tk                   = Tk.EOF
    tk_list: list[dict[int, str]] = []
    source: str = ""
    last_word: str = ""


    def __init__(self, init_source):
        self.source = init_source


    def char_next(self) -> str:
        result: str = self.source[0]
        self.source = self.source[1:]

        return result


    def char_peek(self) -> str:
        try: return self.source[1]
        except IndexError: return ''

    def tk_next(self) -> dict[Tk, str]:
        self.last_word = ""

        if len(self.source) == 0: return { self.Tk.EOF: self.last_word }

        while self.source[0].isspace():
            self.char_next()
            if len(self.source) == 0: return { self.Tk.EOF: self.last_word }

        if self.source[0].isdecimal() or self.char_peek() == '.' or self.source[0] == '.':
            while self.source[0].isdecimal() or self.char_peek() == '.' or self.source[0] == '.':
                self.last_word += self.char_next()
                if len(self.source) == 0: return { self.Tk.number: self.last_word }

            return { self.Tk.number: self.last_word }

        elif self.source[0] == '(':
            self.last_word += self.char_next()
            return { self.Tk.l_parenthe: self.last_word }

        elif self.source[0] == ')':
            self.last_word += self.char_next()
            return { self.Tk.r_parenthe: self.last_word }

        elif self.source[0] in "+-":
            while self.source[0] in "+-":
                self.last_word += self.char_next()
                if len(self.source) == 0: return { self.Tk.fn: self.last_word }

            return { self.Tk.fn: self.last_word }

        elif self.source[:len("quit")] == "quit":
            while self.source[:len("quit")] == "quit":
                self.last_word += self.source[:len("quit")]
                self.source = self.source[len("quit"):]
                if len(self.source) == 0: return { self.Tk.fn: self.last_word }

            return { self.Tk.fn: self.last_word }

        elif self.source[0].isalpha():
            while self.source[0].isalpha():
                self.last_word += self.char_next()
                if len(self.source) == 0: return { self.Tk.symbol: self.last_word }

            return { self.Tk.symbol: self.last_word }


        return { self.Tk.err: self.last_word }


    def parse(self) -> list[dict[Tk, str]]:
        (tk, text) = self.tk_next().popitem()
        result: list[dict[Parser.Tk, str]] = [{ tk: text }]

        while tk != self.Tk.EOF and tk != self.Tk.err:
            (tk, text) = self.tk_next().popitem()
            result += [{ tk: text }]

        result.pop()
        return result


class Evaluator():
    #env: dict[Obj, Obj] = { nil: nil }
    reader:  Parser                     = Parser('')
    lexs:    list[dict[Parser.Tk, str]] = []
    program: list[Obj]                  = []


    def __init__(self, source: str):
        self.p = Parser(source)
        self.lexs = self.p.parse()
        self.make_program()


    def lex_next(self) -> Tuple[Parser.Tk, str]:
        result: Tuple[Parser.Tk, str] = self.lexs[0].popitem()
        self.lexs = self.lexs[1:]
        return result


    def obj_next(self) -> Obj:
        if len(self.lexs) == 0:
            self.lexs.append({ Parser.Tk.EOF: '' })

        lex = self.lex_next()

        match lex[0]:
            case Parser.Tk.number:
                return Num(float(lex[1]))

            case Parser.Tk.symbol:
                return Sym(lex[1])

            case Parser.Tk.fn:
                return Fn(lex[1])

            case Parser.Tk.l_parenthe:
                head: Obj = self.obj_next()
                tmp: Obj  = self.obj_next()
                objs: list[Obj] = []

                if self.lexs == []: return Cons(head, tmp)
                while self.lexs[0] != { Parser.Tk.r_parenthe: ')' }:
                    objs.append(tmp)
                    tmp = self.obj_next()

                self.lex_next()
                objs.append(tmp)
                objs.append(nil)
                return Cons(head, objs)

            case _:
                return nil


    def make_program(self):
        while self.lexs != []:
            self.program.append(self.obj_next())


    def eval_next(self) -> Obj | None:
        return self.program.pop(0).eval() if self.program != [] else None


    def eval(self, f = lambda x: None):
        while True:
            if (obj := self.eval_next()) == None: return
            f(obj)


if __name__ == "__main__":
    from sys import argv

    if len(argv) < 2:
        while True:
            e = Evaluator(input("> "))
            e.eval(lambda x: print(f"{type(x)} : {x}"))
    else:
        with open(argv[1], 'r') as f:
            e = Evaluator(f.read())
            e.eval(print)
