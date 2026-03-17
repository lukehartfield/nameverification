import pytest

from backend.verifier import verify


EXPECTED_MATCHES = [
    ("Tyler Bliha", "Tlyer Bilha"),
    ("Al-Hilal", "alhilal"),
    ("Dargulov", "Darguloff"),
    ("Bob Ellensworth", "Robert Ellensworth"),
    ("Mohammed Al Fayed", "Muhammad Alfayed"),
    ("Sarah O'Connor", "Sara Oconnor"),
    ("Jonathon Smith", "Jonathan Smith"),
    ("Abdul Rahman ibn Saleh", "Abdulrahman ibn Saleh"),
    ("Al Hassan Al Saud", "Al-Hasan Al Saud"),
    ("Katherine McDonald", "Catherine Macdonald"),
    ("Yusuf Al Qasim", "Youssef Alkasim"),
    ("Steven Johnson", "Stephen Jonson"),
    ("Alexander Petrov", "Aleksandr Petrof"),
    ("Jean-Luc Picard", "Jean Luc Picard"),
    ("Mikhail Gorbachov", "Mikhail Gorbachev"),
    ("Elizabeth Turner", "Liz Turner"),
    ("Omar ibn Al Khattab", "Omar Ibn Alkhattab"),
    ("Sean O'Brien", "Shawn Obrien"),
]


EXPECTED_NON_MATCHES = [
    ("Emanuel Oscar", "Belinda Oscar"),
    ("Michael Thompson", "Michelle Thompson"),
    ("Ali Hassan", "Hassan Ali"),
    ("John Smith", "James Smith"),
    ("Abdullah ibn Omar", "Omar ibn Abdullah"),
    ("Maria Gonzalez", "Mario Gonzalez"),
    ("Christopher Nolan", "Christian Nolan"),
    ("Ahmed Al Rashid", "Ahmed Al Rashidi"),
    ("Samantha Lee", "Samuel Lee"),
    ("Ivan Petrov", "Ilya Petrov"),
    ("Fatima Zahra", "Zahra Fatima"),
    ("William Carter", "Liam Carter"),
]


@pytest.mark.parametrize(("target", "candidate"), EXPECTED_MATCHES)
def test_expected_matches(target: str, candidate: str) -> None:
    result = verify(target, candidate)

    assert result["match"] is True, result
    assert 0.8 <= result["confidence"] <= 1.0
    assert result["reason"]


@pytest.mark.parametrize(("target", "candidate"), EXPECTED_NON_MATCHES)
def test_expected_non_matches(target: str, candidate: str) -> None:
    result = verify(target, candidate)

    assert result["match"] is False, result
    assert 0.0 <= result["confidence"] < 0.8
    assert result["reason"]
