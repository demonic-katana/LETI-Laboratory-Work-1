import math


def tokenize(arith_expr):
    tokens = []
    pos = 0

    while pos < len(arith_expr):
        symbol = arith_expr[pos]
        if symbol.isspace():
            pos += 1
            continue
        if arith_expr.startswith("log10", pos):
            tokens.append("log10")
            pos += 5
            continue
        if arith_expr.startswith(">=", pos):
            tokens.append(">=")
            pos += 2
            continue
        if symbol in "0123456789.":
            number = ""
            while pos < len(arith_expr) and arith_expr[pos] in "0123456789.":
                number += arith_expr[pos]
                pos += 1
            if number.count(".") > 1 or number == ".":
                raise ValueError(f"Некорректное число: {number}")
            if "." in number:
                tokens.append(float(number))
            else:
                tokens.append(int(number))
            continue
        if symbol in "()+-*/":
            tokens.append(symbol)
            pos += 1
            continue

        raise ValueError(f"Недопустимый символ '{symbol}' в позиции {pos + 1}")

    if not tokens:
        raise ValueError("Выражение не должно быть пустым")

    return tokens


def parse_primary(tokens, pos):
    if pos >= len(tokens):
        raise ValueError("Ожидалось число или открывающая скобка")

    token = tokens[pos]

    if isinstance(token, (int, float)):
        return token, pos + 1

    if token == "(":
        value, pos = parse_comparison(tokens, pos + 1)
        if pos >= len(tokens) or tokens[pos] != ")":
            raise ValueError("Не хватает закрывающей скобки ')'")
        return value, pos + 1

    if token == "log10":
        if pos + 1 >= len(tokens) or tokens[pos + 1] != "(":
            raise ValueError("После log10 должна идти открывающая скобка '('")

        value, pos = parse_comparison(tokens, pos + 2)
        if pos >= len(tokens) or tokens[pos] != ")":
            raise ValueError("Не хватает закрывающей скобки в log10(...)")
        if value <= 0:
            raise ValueError("Логарифм определён только для положительных чисел")

        return math.log10(value), pos + 1

    raise ValueError(f"Неожиданный токен: {token}")


def parse_unary(tokens, pos):
    if pos < len(tokens) and tokens[pos] in ("+", "-"):
        operator = tokens[pos]
        value, pos = parse_unary(tokens, pos + 1)
        if operator == "-":
            value = -value
        return value, pos

    return parse_primary(tokens, pos)


def parse_term(tokens, pos):
    value, pos = parse_unary(tokens, pos)

    while pos < len(tokens) and tokens[pos] in ("*", "/"):
        operator = tokens[pos]
        right, pos = parse_unary(tokens, pos + 1)

        if operator == "*":
            value *= right
        else:
            if right == 0:
                raise ZeroDivisionError("Деление на ноль")
            value /= right

    return value, pos


def parse_expression(tokens, pos):
    value, pos = parse_term(tokens, pos)

    while pos < len(tokens) and tokens[pos] in ("+", "-"):
        operator = tokens[pos]
        right, pos = parse_term(tokens, pos + 1)

        if operator == "+":
            value += right
        else:
            value -= right

    return value, pos


def parse_comparison(tokens, pos):
    value, pos = parse_expression(tokens, pos)

    if pos < len(tokens) and tokens[pos] == ">=":
        right, pos = parse_expression(tokens, pos + 1)
        value = "Неравенство " + ("истинно" if value >= right else "ложно")

    return value, pos


def calc(tokens):
    result, pos = parse_comparison(tokens, 0)

    if pos != len(tokens):
        raise ValueError(f"Лишний или неверно расположенный токен: {tokens[pos]}")

    return result


if __name__ == "__main__":
    print("Арифметический интерпретатор (вариант 29)")
    print("Операции: +, -, *, /, >=; скобки и функция log10(x)")
    print("Для завершения введите 'выход'.")

    while True:
        try:
            arith_expr = input("\nВведите арифметическое выражение: ")
        except (EOFError, KeyboardInterrupt):
            print("\nРабота завершена.")
            break

        if arith_expr.strip().lower() in ("выход", "exit"):
            break

        try:
            result = calc(tokenize(arith_expr))
        except (ValueError, ZeroDivisionError) as error:
            print(f"Ошибка: {error}")
        else:
            print(f"{arith_expr} = {result}")
