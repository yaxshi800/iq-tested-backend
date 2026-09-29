def detect_card_type(card_number: str) -> str:
    num = "".join(c for c in card_number if c.isdigit())
    if not num:
        return "unknown"

    if num.startswith("8600") or num.startswith("5614"):
        return "uzcard"
    if num.startswith("9860"):
        return "humo"
    if num.startswith("4"):
        return "visa"
    if num[:2] in ["51", "52", "53", "54", "55"]:
        return "mastercard"
    if len(num) >= 4 and 2221 <= int(num[:4]) <= 2720:
        return "mastercard"
    if num.startswith("34") or num.startswith("37"):
        return "amex"
    return "unknown"


def luhn_check(card_number: str) -> bool:
    num = "".join(c for c in card_number if c.isdigit())
    if not num.isdigit() or len(num) < 13 or len(num) > 19:
        return False

    total = 0
    reverse = num[::-1]
    for i, digit in enumerate(reverse):
        n = int(digit)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n

    return total % 10 == 0