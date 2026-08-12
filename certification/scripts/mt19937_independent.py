#!/usr/bin/env python3
"""Independent MT19937 implementation (written from the published algorithm
spec, init_genrand seeding) used to certify the original CFR_plus rng.c
oracle bit-for-bit. This is certification reference code, NOT production
solver code (no production HUHL solver exists in this repository)."""
import sys

N, M = 624, 397
MATRIX_A = 0x9908B0DF
UPPER_MASK = 0x80000000
LOWER_MASK = 0x7FFFFFFF


class MT19937:
    def __init__(self, seed: int):
        self.mt = [0] * N
        self.mt[0] = seed & 0xFFFFFFFF
        for i in range(1, N):
            self.mt[i] = (1812433253 * (self.mt[i - 1] ^ (self.mt[i - 1] >> 30)) + i) & 0xFFFFFFFF
        self.mti = N

    def _generate(self):
        for i in range(N):
            y = (self.mt[i] & UPPER_MASK) | (self.mt[(i + 1) % N] & LOWER_MASK)
            self.mt[i] = self.mt[(i + M) % N] ^ (y >> 1)
            if y & 1:
                self.mt[i] ^= MATRIX_A
        self.mti = 0

    def next_u32(self) -> int:
        if self.mti >= N:
            self._generate()
        y = self.mt[self.mti]
        self.mti += 1
        y ^= y >> 11
        y ^= (y << 7) & 0x9D2C5680
        y ^= (y << 15) & 0xEFC60000
        y ^= y >> 18
        return y & 0xFFFFFFFF


def main():
    seed, count, oracle_bin = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    rng = MT19937(seed)
    ours = b"".join(rng.next_u32().to_bytes(4, "little") for _ in range(count))
    theirs = open(oracle_bin, "rb").read()
    assert len(theirs) == 4 * count, f"oracle length {len(theirs)} != {4*count}"
    if ours == theirs:
        print(f"seed={seed} count={count}: BIT_EXACT (byte_equal=True)")
        return 0
    # find first divergence
    for i in range(count):
        a = int.from_bytes(ours[4*i:4*i+4], "little")
        b = int.from_bytes(theirs[4*i:4*i+4], "little")
        if a != b:
            print(f"seed={seed} count={count}: FAIL first divergence at index {i}: ours={a} oracle={b}")
            return 1
    return 1


if __name__ == "__main__":
    sys.exit(main())
