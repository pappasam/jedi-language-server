"""Test file for test_refactoring."""


def myfunc1():
    print("myfunc1")


def my_function_2():
    myfunc1()
    print("my_function_2")


myfunc1()
my_function_2()
