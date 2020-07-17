import random


def decompose(n):
    exponentOfTwo = 0

    while n % 2 == 0:
        n = n // 2  # using / turns large numbers into floats
        exponentOfTwo += 1

    return exponentOfTwo, n


def isWitness(possibleWitness, p, exponent, remainder):
    if pow(possibleWitness, remainder, p) == 1:
        return False

    if any(pow(possibleWitness, 2**i * remainder, p) == p - 1 for i in range(exponent)):
        return False

    return True


def probablyPrime(p, accuracy=100):
    if p in (2,3):
        return True
    if p < 2 or p % 2 == 0:
        return False

    exponent, remainder = decompose(p - 1)

    for _ in range(accuracy):
        possibleWitness = random.randint(2, p - 2)
        if isWitness(possibleWitness, p, exponent, remainder):
            return False

    return True


###############################################################################

def goodPrime(p):
    return p % 4 == 3 and probablyPrime(p, accuracy=100)


def findGoodPrime(numBits=512):
    candidate = 1

    while not goodPrime(candidate):
        candidate = random.getrandbits(numBits)

    return candidate


def makeModulus():
    return findGoodPrime() * findGoodPrime()


def parity(n):
    return sum(int(x) for x in bin(n)[2:]) % 2


class BlumBlumShub(object):
    def __init__(self, seed=None):
        self.modulus = makeModulus()
        self.state = seed if seed is not None else random.randint(2, self.modulus - 1)
        self.state = self.state % self.modulus

    def seed(self, seed):
        self.state = seed

    def bitstream(self):
        while True:
            yield parity(self.state)
            self.state = pow(self.state, 2, self.modulus)

    def bits(self, n=20):
        outputBits = ''

        for bit in self.bitstream():
            outputBits += str(bit)
            if len(outputBits) == n:
                break

        return outputBits


if __name__ == "__main__":
    generator = BlumBlumShub()

    hist = [0] * 2**6
    #for i in range(10000):
    for i in range(1000):
        value = int(generator.bits(6), 2)
        hist[value] += 1

print(hist)

