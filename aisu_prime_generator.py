from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Iterable, Iterator, List, Optional, Tuple


# ---- primality (64-bit deterministic Miller–Rabin) ----

def is_prime_64(n: int) -> bool:
    if n < 2:
        return False

    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for p in small:
        if n == p:
            return True
        if n % p == 0:
            return False

    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    bases = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)
    for a in bases:
        a %= n
        if a == 0:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True


# ---- congruence constraints ----

ForbiddenCongruence = Tuple[int, int]  # (modulus, forbidden_residue)

def passes_forbidden(n: int, forbidden: Iterable[ForbiddenCongruence]) -> bool:
    for m, r in forbidden:
        if n % m == r:
            return False
    return True


# ---- wheel construction from constraints ----

@dataclass(frozen=True)
class Wheel:
    M: int
    residues: Tuple[int, ...]
    forbidden: Tuple[ForbiddenCongruence, ...]


def build_wheel(forbidden: List[ForbiddenCongruence]) -> Wheel:
    mods: List[int] = []
    M = 1
    for m, _ in forbidden:
        if m not in mods:
            mods.append(m)
            M *= m

    residues = [r for r in range(M) if passes_forbidden(r, forbidden)]
    return Wheel(M=M, residues=tuple(residues), forbidden=tuple(forbidden))


# ---- streams ----

def candidate_stream(wheel: Wheel, start: int = 2) -> Iterator[int]:
    M, residues = wheel.M, wheel.residues
    q = start // M
    while True:
        base = q * M
        for r in residues:
            n = base + r
            if n >= start:
                yield n
        q += 1


def primes(
    forbidden: Optional[List[ForbiddenCongruence]] = None,
    start: int = 2,
) -> Iterator[int]:
    if forbidden is None:
        forbidden = [(2, 0), (3, 0), (5, 0), (7, 0), (11, 0), (13, 0)]
    wheel = build_wheel(forbidden)
    for n in candidate_stream(wheel, start=start):
        if not passes_forbidden(n, wheel.forbidden):
            continue
        if is_prime_64(n):
            yield n


# ---- printing ----

def print_primes(
    count: int = 10000,
    per_line: int = 12,
    forbidden: Optional[List[ForbiddenCongruence]] = None,
    start: int = 2,
    out_path: Optional[str] = None,
) -> None:
    out = sys.stdout if out_path is None else open(out_path, "w", encoding="utf-8")
    try:
        gen = primes(forbidden=forbidden, start=start)
        line: List[int] = []
        printed = 0
        while printed < count:
            p = next(gen)
            line.append(p)
            printed += 1
            if len(line) >= per_line:
                out.write(" ".join(str(x) for x in line) + "\n")
                line.clear()
        if line:
            out.write(" ".join(str(x) for x in line) + "\n")
    finally:
        if out_path is not None:
            out.close()


if __name__ == "__main__":
    # 小さい素数から自然に列記
    print_primes(count=50000, per_line=12)

    # さらに大量に出したい場合はファイルへ（例）
    # print_primes(count=300000, per_line=12, out_path="primes_300k.txt")

    # 禁則を厚くしたい場合（例）
    # forbidden = [(2,0),(3,0),(5,0),(7,0),(11,0),(13,0),(17,0),(19,0),(23,0),(29,0),(31,0)]
    # print_primes(count=200000, per_line=12, forbidden=forbidden)
