import re, math
from typing import Dict
# Implementacja funkcji is_palindrome


def is_palindrome(text: str) -> bool:
    """
    Sprawdza, czy `text` jest palindromem, ignorując wielkość liter i znaki białe.
    Przykłady:
      is_palindrome("kajak") -> True
      is_palindrome("Kobyła ma mały bok") -> True
    """
    if text is None:
        # Optionalnie: None nie powinno występować według specyfikacji; traktujemy jako False
        return False
    # Usuń wszystkie znaki białe (spacje, tabulatory, nowe linie) i sprowadź do małych liter
    normalized = "".join(ch.lower() for ch in text if not ch.isspace())
    return normalized == normalized[::-1]


def fibonacci(n: int) -> int:
    """
    Zwraca n-ty element ciągu Fibonacciego:
      fibonacci(0) == 0
      fibonacci(1) == 1

    Dla n < 0 rzuca ValueError.
    """
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
    """
    Zlicza liczbę samogłosek w `text`.
    Samogłoski: a, e, i, o, u, y oraz polskie warianty: ą, ę, ó.
    Wielkość liter nie ma znaczenia.

    Zwraca liczbę samogłosek (int). Dla pustego ciągu -> 0.
    Rzuca TypeError jeśli przekazany typ nie jest str.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a str")
    vowels = set("aeiouyąęó")  # wszystkie w lowercase
    count = 0
    for ch in text.lower():
        if ch in vowels:
            count += 1
    return count


def calculate_discount(price: float, discount: float) -> float:
    """
    Zwraca cenę po uwzględnieniu zniżki.
    Przykład: calculate_discount(100, 0.2) -> 80.0

    Wymagania:
    - discount musi być w przedziale [0, 1]. W przeciwnym razie ValueError.
    - price i discount muszą być liczbami (int/float) — w przeciwnym razie TypeError.
    """
    if not isinstance(price, (int, float)):
        raise TypeError("price must be a number")
    if not isinstance(discount, (int, float)):
        raise TypeError("discount must be a number")
    if discount < 0 or discount > 1:
        raise ValueError("discount must be between 0 and 1 inclusive")
    return float(price * (1 - discount))


def flatten_list(nested_list: list) -> list:
    """
    Spłaszcza zagnieżdżoną listę elementów (tylko listy są traktowane jako zagnieżdżenia).
    Przykład:
      flatten_list([1, [2, 3], [4, [5]]]) -> [1, 2, 3, 4, 5]

    Dla pustej listy zwraca [].
    Jeśli argument nie jest listą, rzuca TypeError.
    """
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
    """
    Zwraca słownik z częstością występowania słów w tekście.
    Ignoruje wielkość liter i interpunkcję.

    Przykłady:
      word_frequencies("To be or not to be") -> {"to": 2, "be": 2, "or": 1, "not": 1}
      word_frequencies("Hello, hello!") -> {"hello": 2}
    """
    if not isinstance(text, str):
        raise TypeError("text must be a str")
    # Znajdź sekwencje liter (w tym litery Unicode, np. polskie znaki)
    words = re.findall(r"[^\W\d_]+", text.lower(), flags=re.UNICODE)
    freqs: Dict[str, int] = {}
    for w in words:
        freqs[w] = freqs.get(w, 0) + 1
    return freqs


def is_prime(n: int) -> bool:
    """
    Sprawdza, czy n jest liczbą pierwszą.
    Zwraca False dla n < 2.
    Rzuca TypeError jeśli n nie jest int.
    """
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