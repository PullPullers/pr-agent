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


def print_score(score):
    if score > 90:
        print("Excellent")


def print_size(x):
    if x > 10:
        print("Big")
    elif x > 5:
        print("Medium")
