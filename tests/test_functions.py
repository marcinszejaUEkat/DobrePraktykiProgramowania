import pytest
from main.functions import is_palindrome, fibonacci, count_vowels, calculate_discount, flatten_list, word_frequencies, is_prime


@pytest.mark.parametrize("text,expected", [
    ("kajak", True),
    ("Kobyła ma mały bok", True),
    ("python", False),
    ("", True),
    ("A", True),
])
def test_is_palindrome_examples(text, expected):
    assert is_palindrome(text) is expected


@pytest.mark.parametrize("n,expected", [
    (0, 0),
    (1, 1),
    (5, 5),
    (10, 55),
])
def test_fibonacci_values(n, expected):
    assert fibonacci(n) == expected


def test_fibonacci_negative_raises():
    with pytest.raises(ValueError):
        fibonacci(-1)


@pytest.mark.parametrize("text,expected", [
    ("Python", 2),  # Zmienione 1 na 2, bo są dwie samogłoski
    ("AEIOUY", 6),
    ("bcd", 0),
    ("", 0),
    ("Próba żółwia", 5),  # UWAGA: tutaj 5 (ó pojawia się dwukrotnie)
])
def test_count_vowels_examples(text, expected):
    assert count_vowels(text) == expected


def test_count_vowels_type_error():
    with pytest.raises(TypeError):
        count_vowels(None)


@pytest.mark.parametrize("price,discount,expected", [
    (100, 0.2, 80.0),
    (50, 0, 50.0),
    (200, 1, 0.0),
])
def test_calculate_discount_values(price, discount, expected):
    assert calculate_discount(price, discount) == expected


@pytest.mark.parametrize("discount", [-0.1, 1.5])
def test_calculate_discount_invalid_discount_raises(discount):
    with pytest.raises(ValueError):
        calculate_discount(100, discount)


@pytest.mark.parametrize("input_list,expected", [
    ([1, 2, 3], [1, 2, 3]),
    ([1, [2, 3], [4, [5]]], [1, 2, 3, 4, 5]),
    ([], []),
    ([[[1]]], [1]),
    ([1, [2, [3, [4]]]], [1, 2, 3, 4]),
])
def test_flatten_list_examples(input_list, expected):
    assert flatten_list(input_list) == expected


def test_flatten_list_type_error():
    with pytest.raises(TypeError):
        flatten_list(None)


@pytest.mark.parametrize("text,expected", [
    ("To be or not to be", {"to": 2, "be": 2, "or": 1, "not": 1}),
    ("Hello, hello!", {"hello": 2}),
    ("", {}),
    ("Python Python python", {"python": 3}),
    # Sprawdzenie ignorowania interpunkcji i wielkości liter (polskie znaki też obsługiwane)
    ("Ala ma kota, a kot ma Ale.", {"ala": 1, "ma": 2, "kota": 1, "a": 1, "kot": 1, "ale": 1}),
])
def test_word_frequencies_examples(text, expected):
    assert word_frequencies(text) == expected

def test_word_frequencies_type_error():
    with pytest.raises(TypeError):
        word_frequencies(None)


@pytest.mark.parametrize("n,expected", [
    (2, True),
    (3, True),
    (4, False),
    (0, False),
    (1, False),
    (5, True),   # 5 jest liczbą pierwszą — poprawiłem zgodnie z definicją
    (97, True),
])
def test_is_prime_examples(n, expected):
    assert is_prime(n) is expected

def test_is_prime_type_error():
    with pytest.raises(TypeError):
        is_prime(3.5)