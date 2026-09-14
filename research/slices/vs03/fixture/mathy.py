"""Disposable math fixture. add() is defective; mul() must stay correct."""


def add(a, b):
    return a - b


def mul(a, b):
    return a * b
