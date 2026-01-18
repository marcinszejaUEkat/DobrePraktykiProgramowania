import re, math
from typing import Dict


def is_palindrome(text: str) -> bool:
    if text is None:
        return False
    normalized = "".join(ch.lower() for ch in text if not ch.isspace())
    return normalized == normalized[::-1]


def fibonacci(n: int) -> int:
    if not isinstance(n, int):
        raise TypeError("n must be an int")
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0:
        return 0
    a, b = 0, 1
    for _ in range(1, n):
        a, b = b, a + b
    return b


def count_vowels(text: str) -> int:
    if not isinstance(text, str):
        raise TypeError("text must be a str")
    vowels = set("aeiouyąęó")
    count = 0
    for ch in text.lower():
        if ch in vowels:
            count += 1
    return count


def calculate_discount(price: float, discount: float) -> float:
    if not isinstance(price, (int, float)):
        raise TypeError("price must be a number")
    if not isinstance(discount, (int, float)):
        raise TypeError("discount must be a number")
    if discount < 0 or discount > 1:
        raise ValueError("discount must be between 0 and 1 inclusive")
    return float(price * (1 - discount))


def flatten_list(nested_list: list) -> list:
    if not isinstance(nested_list, list):
        raise TypeError("nested_list must be a list")
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result


def word_frequencies(text: str) -> Dict[str, int]:
    if not isinstance(text, str):
        raise TypeError("text must be a str")
    words = re.findall(r"[^\W\d_]+", text.lower(), flags=re.UNICODE)
    freqs: Dict[str, int] = {}
    for w in words:
        freqs[w] = freqs.get(w, 0) + 1
    return freqs


def is_prime(n: int) -> bool:
    if not isinstance(n, int):
        raise TypeError("n must be an int")
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    limit = int(math.isqrt(n))
    for i in range(3, limit + 1, 2):
        if n % i == 0:
            return False
    return True