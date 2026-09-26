"""Perform four arithmetic operations for two integers."""


def main() -> None:
    n = int(input("Enter integer n: "))
    m = int(input("Enter integer m: "))

    print(f"n + m = {n + m}")
    print(f"n - m = {n - m}")
    print(f"n * m = {n * m}")

    if m == 0:
        print("n / m: division by zero is not possible")
    else:
        print(f"n / m = {n / m}")


if __name__ == "__main__":
    main()
