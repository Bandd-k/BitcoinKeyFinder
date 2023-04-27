from hdwallet import HDWallet
import binascii
import multiprocessing as mp
import time
import uuid
import os
from random import randrange
import sys
import json

class Counter(object):
    def __init__(self, initval=0):
        self.val = mp.Value('i', initval)
        self.lock = mp.Lock()

    def increment(self, n):
        with self.lock:
            self.val.value += n
            if self.val.value % 10 == 0:
                print(f"Attempts made: {self.val.value} * 10000")

    def value(self):
        with self.lock:
            return self.val.value

class Solver:

    def __init__(self, process, computer, wallets, counter, verbose=False):
        self.targets = wallets
        self.verbose = verbose
        self.run = True
        self.process = process
        self.random_value = f"{computer}{process}"
        self.counter = counter
        self.current = 0

    def start(self):
        self.run = True
        while self.run:
            self.generate()
    
    def stop(self):
        self.run = False

    def random(self):
        # from bitcoin project
        return str(self.random_value) \
            + str(os.urandom(32).hex()) \
            + str(randrange(2 ** 256)) \
            + str(int(time.time() * 1000000)) \

    def generate(self):
        hdwallet = HDWallet()
        hexSeed = binascii.hexlify(self.random().encode())
        hdwallet.from_seed(hexSeed)
        pubAdr = hdwallet.p2pkh_address()
        wif = hdwallet.wif()
        if self.verbose:
            print(f"Proccess: {self.process}")
            print(f"Key WIF: {wif}")
            print(f"Key address: {pubAdr}")
        if pubAdr in self.targets:
            print("KEY FOUND!!!")
            dump_str = json.dumps(hdwallet.dumps(), indent=4, ensure_ascii=False)
            print(dump_str)
            self.write(dump_str)
            # nice found!!!
            # do something
        self.current += 1
        if self.current == 10000:
            self.counter.increment(1)
            self.current = 0
    
    def write(self, wallet):
        fhand = open("keys.txt", 'a+')
        fhand.write(str(wallet))
        fhand.write("\n###########################################\n")
        fhand.close()

def generate(index, verbose, computer, wallets, counter):
    print(f"Process Started {index}")
    solver = Solver(index, computer, wallets, counter, verbose) 
    solver.start()


if __name__ == "__main__":
    print("START")
    counter = Counter()
    verbose = False
    if len(sys.argv) == 2 and sys.argv[1] == "--verbose":
        verbose = True
    fhand = open("wallets.txt")
    wallets = set(fhand.readlines())
    fhand.close()
    computer = uuid.UUID(int=uuid.getnode())
    # generate(1, verbose, computer, wallets, counter)
    print("Cores on machine to be used:", mp.cpu_count())
    print("Addresses to be used:", len(wallets))
    procs = [mp.Process(target=generate, args=(index, verbose, computer, wallets, counter,)) for index in range(mp.cpu_count())]

    for p in procs: p.start()
    for p in procs: p.join()

#12ib7dApVFvg82TXKycWBNpN8kFyiAN1dr


# compile to executable
# change address of wallets