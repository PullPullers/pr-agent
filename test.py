print("Hello from PR-Agent Test!")


def divide(a, b):
    if b == 0:
        return 0
    return a / b


def check_even(num):
    if num % 2 == 0:
        return True
    else:
        return False


def unused_function():
    temp = 42
    # TODO
    pass


def duplicate_logic(x):
    if x > 10:
        return "large"
    if x > 10:
        return "big"
    return "small"
