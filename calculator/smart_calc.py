from collections import deque


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

    def __init__(self):
        self.variables = {}
        self.valid_commands = {'/exit': 'Bye!',
                               '/help': self.__doc__}

        # op: ("presidence in RPN", "associativity (Left/Right)")
        # presidence and associativity used to convert to RPN
        self.operators = {'+': (2, 'L'),
                          '-': (2, 'L'),
                          '*': (3, 'L'),
                          '/': (3, 'L'),
                          '^': (4, 'R')}

        self.status = False
        self.unknown_var = False
        return None

    def _continue_operator_stack_pop(self, operator_stack, tok):
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
            condition1 &= (self.operators[top_op][0] > self.operators[tok][0])

        condition2 = (top_op != '(')
        if condition2:  # if statement because ( and ) arent in self.operators
            condition2 &= (self.operators[top_op][0] == self.operators[tok][0])
            condition2 &= (self.operators[tok][1] == 'L')

        return condition1 or condition2

    def convert_to_rpn(self, infix_expression):
        """
        Implements Dijkstra's Shunting-yard algorithm to convert between infix
        and reverse-polish notations using a stack

        en.wikipedia.org/wiki/Shunting-yard_algorithm#The_algorithm_in_detail
        """

        input_queue = self.parse_input(infix_expression)
        output_queue = deque()
        op_stack = deque()  # top is right

        while input_queue:
            token = input_queue.popleft()

            if token.isnumeric():
                output_queue.append(token)  # numbers pass right to output

            elif token in self.operators:
                # pop higher presidence operators / () before pushing to stack
                while self._continue_operator_stack_pop(op_stack, token):
                    output_queue.append(op_stack.pop())
                op_stack.append(token)

            elif token == '(':
                op_stack.append(token)  # automatically ( get pushed to stack

            elif token == ')':
                # when closing ) found push all operators to the output
                # and discard (
                while (op_stack[-1] != '('):
                    output_queue.append(op_stack.pop())
                if op_stack[-1] == '(':
                    op_stack.pop()

        while op_stack:
            output_queue.append(op_stack.pop())

        return output_queue

    def calculate(self, expression):
        """
        Converts valid infix expressions to reverse polish notation then
        calculates and returns the resulting value
        """

        # top of input and comp stack is the left
        input_stack = self.convert_to_rpn(self.replace_variables(expression))
        comp_stack = deque()

        while input_stack:
            token = input_stack.popleft()

            if token.isnumeric():
                comp_stack.appendleft(int(token))
            else:
                b = comp_stack.popleft()
                a = comp_stack.popleft()

                if token == '+':
                    comp_stack.appendleft(a + b)
                elif token == '-':
                    comp_stack.appendleft(a - b)
                elif token == '/':
                    comp_stack.appendleft(a//b)
                elif token == '*':
                    comp_stack.appendleft(a*b)
                elif token == '^':
                    comp_stack.appendleft(a**b)

        return comp_stack.pop()

    def replace_variables(self, expression):
        """Replaces known variables in an expression with their values"""

        for var in self.variables:
            if var in expression:
                expression = expression.replace(var, str(self.variables[var]))
        return expression

    def resolve_op(self, op_str):
        """resolves non-unitary + and - operators to unitary operators"""
        if op_str.count('-') % 2 == 1:
            return '-'
        return '+'

    def is_resolvable(self, op_queue):
        """checks a string of operators to see if it is a non-unitary + or -
        and therefore that it can be resolved"""
        return not bool(set(op_queue).difference({'+', '-'}))

    def parse_input(self, user_input):
        """
        Parses an input expression splitting it into arguements, variables,
        operators, and parenthesis. Output is a queue ordered from left to
        right. Non unitary + or - operators are interpreted; all spaces are
        removed.
        """

        # handle for leading + or -
        if user_input.startswith('+') or user_input.startswith('-'):
            user_input = '0' + user_input

        # created needed datastructures
        input_queue = deque(user_input)
        out_queue = deque()  # parsed output
        arg_queue = deque()  # for multi-character numerals / variables
        op_q = deque()  # for nonunitary + or -, or invalid ops like "*+/"

        while input_queue:

            elem = input_queue.popleft()

            if elem.isalnum():
                if op_q:
                    # first flush op queue to output
                    if self.is_resolvable(op_q):
                        out_queue.append(self.resolve_op(''.join(op_q)))
                    else:
                        out_queue.append(''.join(op_q))
                    op_q.clear()

                arg_queue.append(elem)
            else:
                if arg_queue:
                    # first flush arguement queue to output
                    out_queue.append(''.join(arg_queue))
                    arg_queue.clear()

                if elem == ' ':
                    if op_q:
                        # flush op queue to output
                        if self.is_resolvable(op_q):
                            out_queue.append(self.resolve_op(''.join(op_q)))
                        else:
                            out_queue.append(''.join(op_q))
                        op_q.clear()

                elif elem in '()=':
                    if op_q:
                        # flush op queue to output
                        if self.is_resolvable(op_q):
                            out_queue.append(self.resolve_op(''.join(op_q)))
                        else:
                            out_queue.append(''.join(op_q))
                        op_q.clear()

                    out_queue.append(elem)

                elif elem in self.operators:
                    op_q.append(elem)

                else:
                    # pass through unknown character. i.e. ! # $
                    out_queue.append(elem)

        else:
            if arg_queue:
                out_queue.append(''.join(arg_queue))
                arg_queue.clear()
            if op_q:
                out_queue.append(''.join(op_q))
                op_q.clear()

        return out_queue

    def is_valid_expression(self, expression):
        """parses through user inputs and validates syntax, returning a bool.
        If an uninitialized variable is present it also sets the instance var
        unknown_var to True"""

        input_queue = self.parse_input(self.replace_variables(expression))
        output_stack = deque()  # top is left

        parenthesis_count = 0
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

            elif token in '()':  # keep track of the number of parenthesis

                if (token == ')') and (parenthesis_count == 0):
                    return False  # ) before an opening (

                parenthesis_count += 1 if token == '(' else -1
                if parenthesis_count < 0:  # too many )
                    return False

            elif token == '=':
                # only valid for assignment, gets stripped out before
                # is_valid_expression is called
                return False

            elif token.isalpha():
                # all existing vars are filtered out by replace_variables
                self.unknown_var = True
                return False

            elif token.isalnum():  # invalid variable name
                return False

            else:  # unknown token
                return False

        if token in self.operators:
            return False  # last character is an operator

        if parenthesis_count != 0:   # unbalanced ()
            return False

        return True

    def is_valid_var_name(self, var_name):
        if not var_name.isalpha():
            return False
        return True

    def check_assignment(self, string):
        """
        checks if an assignment is valid and has proper syntax. if so it adds
        the name and value of the assignment to the instance namespace.
        If an uninitialized variable is present it also sets the instance var
        unknown_var to True.
        """

        assignment_idx = string.index('=')
        var_name = string[:assignment_idx].strip()
        var_expression = string[(assignment_idx+1):]

        if self.is_valid_var_name(var_name):
            if self.is_valid_expression(var_expression):
                self.variables[var_name] = self.calculate(var_expression)
                return None

            # is_valid_expression returned False because of a unknown var
            if self.unknown_var:
                print('Unknown variable')
                self.unknown_var = False
                return None

            print('Invalid assignment')
            return None

        print('Invalid identifier')
        return None

    def check_command(self, string):
        if string not in self.valid_commands:
            print('Unknown command')
            return False

        print(self.valid_commands[string])

        if string == '/exit':
            self.status = False

        return True

    def handle_input(self, user_input):

        if not user_input:  # check if blank
            return None

        if user_input.startswith('/'):  # check if command
            self.check_command(user_input)
            return None

        if '=' in user_input:  # check assignment
            self.check_assignment(user_input)
            return None

        if self.is_valid_expression(user_input):  # check valid input
            ans = self.calculate(user_input)  # if so calculate
            print(ans)
            self.variables['ans'] = ans  # save last answer
            return None

        # is_valid_expression returned False because of a unknown var
        if self.unknown_var:
            print('Unknown variable')
            self.unknown_var = False
            return None

        print('Invalid expression')
        return None

    def start_session(self):
        self.status = True
        while self.status:
            self.handle_input(input())
        return None


if __name__ == '__main__':

    calc = Calculator()
    calc.start_session()
