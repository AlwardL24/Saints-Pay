def parse_money(from_str: str) -> int:
    """Parse a string representing an amount of money into an integer.

    Throws a ValueError if the string is not a valid amount of money.

    Args:
        from_str (str): The string to parse.

    Returns:
        int: The amount of money in cents.
    """

    components = from_str.split(".")
    if len(components) == 1:
        components.append("00")

    if len(components) != 2:
        raise ValueError("Invalid amount of money")

    if len(components[1]) == 1:
        components[1] += "0"

    # split into dollars and cents

    dollars, cents = components

    # check that dollars and cents are valid

    if not dollars.isdigit() or not cents.isdigit():
        raise ValueError("Invalid amount of money")

    dollars = int(dollars)
    cents = int(cents)

    if cents >= 100:
        raise ValueError("Invalid amount of money")

    # convert to cents

    return dollars * 100 + cents
