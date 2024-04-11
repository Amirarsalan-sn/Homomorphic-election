import multiprocessing
import time
from phe import paillier
import pickle

def modify_variable(shared_variable):
    input('how are you')
    while True:
        shared_variable.value -= 2
        print(f'script 2 changed the shared value for {shared_variable.value}')
        if (input('continue?')) == '0':
            break


if __name__ == '__main__':
    one = 1
    public, private = paillier.generate_paillier_keypair()
    one = public.encrypt(one)
    one_serl = pickle.dumps(one)
    new_one = pickle.loads(one_serl)
    print(type(one), one)