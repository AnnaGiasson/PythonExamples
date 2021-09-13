from collections import deque
import re
from collections import namedtuple


Operator = namedtuple('Operator',
                      ('presidence', 'associativity', 'leading_value'))

Command = namedtuple('Command',
                     ('message', 'func'))


class Calculator():

    """
    This program functions as a calculator. It is capabile of the following
    operatations:
        +, -, *, /, ^
    Additionally, it can handle for nested parenthesis and non-unitary +, -
    operators. Using the = operator expressions can be stored into an
    alphabetic variable name to be used for future calculations. Upon
    evaluation of a non-assignment operation the result is automatically stored
    in the variable 'ans'.
    """

    def __init__(self) -> None:
        self.commands = {'/exit': Command('Bye!', lambda: exit()),
                         '/help': Command(self.__doc__, lambda: None),
                         '/clear': Command('Variables Erased',
                                           lambda: self.variables.clear()),
                         }

        # op: ("presidence in RPN", "associativity (Left/Right)")
        # presidence and associativity used to convert to RPN
        self.operators = {'+': Operator(2, 'L', 0),
                          '-': Operator(2, 'L', 0),
                          '*': Operator(3, 'L', None),
                          '/': Operator(3, 'L', None),
                          '^': Operator(4, 'R', None),
                          }

        # name: (regex pattern, processing func)
        self.element_patterns = {
                                 'arg': (re.compile(r'\d+|\d+\.\d*|\.\d*'),
                                         float),
                                 'var': (re.compile(r'[a-zA-Z]+'),
                                         lambda s: self.variables.get(s, s)),
                                 'op': (re.compile(r'[+\-*\/^=]+'),
                                        self.resolve_op),
                                 'sep': (re.compile(r'[()]'),
                                         lambda s: s),
                                 }

        self.variables = {}
        self.expression = deque()

    def _continue_operator_stack_pop(self, operator_stack: deque, tok: str) -> bool:
        """
        only used in 'convert_to_rpn' when determining when to stop removing
        elements from the op stack. Logic was too complex to stick in the 'if'
        statement and have it stay readable
        """
        # top is operator_stack the right

        if not operator_stack:  # stack is empty
            return False

        top_op = operator_stack[-1]

        condition1 = (top_op in self.operators)
        if condition1:  # if statement because ( and ) arent in self.operators
            condition1 &= (self.operators[top_op].presidence > self.operators[tok].presidence)

        condition2 = (top_op != '(')
        if condition2:  # if statement because ( and ) arent in self.operators
            condition2 &= (self.operators[top_op].presidence == self.operators[tok].presidence)
            condition2 &= (self.operators[tok].associativity == 'L')

        return condition1 or condition2

    def convert_expression_to_rpn(self) -> None:
        """
        Implements Dijkstra's Shunting-yard algorithm to convert between infix
        and reverse-polish notations using a stack

        en.wikipedia.org/wiki/Shunting-yard_algorithm#The_algorithm_in_detail
        """

        output_queue = deque()
        op_stack = deque()  # top is the right side

        while self.expression:
            element = self.expression.popleft()

            if isinstance(element, str):
                raise UnknownVariableError(f'Undeclared variable "{element}"')

            if isinstance(element, float):
                output_queue.append(element)  # numbers pass right to output

            elif element in self.operators:
                # pop higher presidence operators / () before pushing to stack
                while self._continue_operator_stack_pop(op_stack, element):
                    output_queue.append(op_stack.pop())
                op_stack.append(element)

            elif element == '(':
                op_stack.append(element)  # automatically ( get pushed to stack

            elif element == ')':
                # when closing ) found push all operators to the output
                # and discard (
                try:
                    while (op_stack[-1] != '('):
                        output_queue.append(op_stack.pop())
                    op_stack.pop()
                except IndexError:
                    raise InvalidExpressionError("Unbalanced parenthesis")

        while op_stack:
            output_queue.append(op_stack.pop())

        while output_queue:
            self.expression.append(output_queue.popleft())

    def calculate_expression(self) -> float:
        """
        Converts valid infix expressions to reverse polish notation then
        calculates and returns the resulting value
        """

        # top of input and comp stack is the left
        self.convert_expression_to_rpn()
        comp_stack = deque()

        while self.expression:
            element = self.expression.popleft()

            if isinstance(element, float):
                comp_stack.appendleft(element)
            else:
                b = comp_stack.popleft()
                a = comp_stack.popleft()

                if element == '+':
                    comp_stack.appendleft(a + b)
                elif element == '-':
                    comp_stack.appendleft(a - b)
                elif element == '/':
                    comp_stack.appendleft(a/b)
                elif element == '*':
                    comp_stack.appendleft(a*b)
                elif element == '^':
                    comp_stack.appendleft(a**b)

        return comp_stack.pop()

    def resolve_op(self, op_str: str) -> str:
        """resolves non-unitary + and - operators to unitary operators"""
        if len(op_str) == 1:
            return op_str

        if any(op in op_str for op in '*/^'):
            raise InvalidExpressionError(f'Invalid operator {op_str}')

        return '-' if (op_str.count('-') % 2 == 1) else '+'

    def parse_input(self, user_input: str) -> deque:
        """
        Parses an input expression string splitting it into arguements,
        variables, operators, and parenthesis. Outputs a queue of operators and
        arguements in infix notation. Non unitary + or - operators are
        interpreted.
        """

        out_queue = deque()
        i = 0
        while user_input[i:]:
            for patt, func in self.element_patterns.values():
                match = re.match(patt, user_input[i:])
                if not match:  # no match found
                    continue

                out_queue.append(func(match[0]))
                i += match.end()
                break
            else:
                raise InvalidExpressionError(f'Input error at position {i}')

        return out_queue

    # needs to be rewritten to use RPN
    def is_valid_expression(self) -> bool:
        """parses through user inputs and validates syntax, returning a bool.
        If an uninitialized variable is present it also sets the instance var
        unknown_var to True"""

        input_queue = self.expression.copy()
        output_stack = deque()  # top is left

        while input_queue:
            token = input_queue.popleft()

            if token.isnumeric():
                if output_stack and (output_stack[0].isnumeric()):
                    return False  # two adjanct numbers with no operator
                output_stack.appendleft(token)

            elif set(token).intersection(set(self.operators)):  # contains ops
                if output_stack and (output_stack[0] in self.operators):
                    return False  # two adjanct operators with no number
                if len(token) > 1:
                    return False  # non unitary + or - handled by parse_input
                output_stack.appendleft(token)

            else:  # unknown token
                return False

        if token in self.operators:
            return False  # last character is an operator

        return True

    def is_valid_var_name(self, var_name: str) -> bool:
        if not var_name.isalpha():
            return False
        return True

    def pop_var_name(self) -> str:
        """
        checks that only a single equals is present (boolean comparison not
        supported), that the expression has a varable name/"="/then an
        expression, and that the variable name is a valid name. Then removes
        the variable name from the queue, leaving the expression in the queue
        and returns the variable name.
        """

        if self.expression.count('=') != 1:
            raise InvalidExpressionError('Only 1 "=" in assignment expression')

        if (len(self.expression) < 3) or (self.expression[1] != '='):
            # "var" "=" "expression"
            raise InvalidExpressionError('missing variable or expression')

        var_name = self.expression.popleft()
        self.expression.popleft()  # remove "="

        if self.is_valid_var_name(var_name):
            return var_name
        raise InvalidVariableError('variable names have only letters '
                                   f'(error: {var_name})')

    def run_command(self, cmd_str) -> None:
        try:
            print(self.commands[cmd_str].message)
            self.commands[cmd_str].func()
        except KeyError:
            raise UnknownCommandError(f'Unsupported command: {cmd_str}')

    def process_input(self, user_input: str) -> None:

        if user_input == "":
            return None

        if user_input.startswith('\\'):  # check if command
            self.run_command(user_input)
            return None

        self.expression = self.parse_input(user_input)

        if '=' in self.expression:  # check assignment
            var_name = self.pop_var_name()
        else:
            var_name = None
        self.convert_expression_to_rpn()

        if self.is_valid_expression():

            # save last answer
            self.variables['ans'] = self.calculate_expression()
            print(self.variables['ans'])
        else:
            raise InvalidExpressionError('Invalid expression')

        if var_name:
            self.variables[var_name] = self.variables['ans']

    @ staticmethod
    def santitize_input(user_input: str) -> str:
        processed_input = user_input.strip()
        return processed_input.replace(' ', '')

    def start_session(self) -> None:

        while True:
            try:
                user_input = self.santitize_input(input())
                self.process_input(user_input)

            except CalculatorBaseError as err:
                print(err)


class CalculatorBaseError(Exception):
    def __init__(self, message="Unknown variable", *args: object) -> None:
        super().__init__(message, *args)


class UnknownVariableError(CalculatorBaseError):
    def __init__(self, message="Unknown variable", *args: object) -> None:
        super().__init__(message, *args)


class InvalidVariableError(CalculatorBaseError):
    def __init__(self, message="Invalid variable", *args: object) -> None:
        super().__init__(message, *args)


class InvalidExpressionError(CalculatorBaseError):
    def __init__(self, message="Invalid expression", *args: object) -> None:
        super().__init__(message, *args)


class UnknownCommandError(CalculatorBaseError):
    def __init__(self, message="Unknown command", *args: object) -> None:
        super().__init__(message, *args)


if __name__ == '__main__':

    calc = Calculator()
    calc.start_session()
