import socket
import time

from phe import paillier
from BlockChain import BlockChain
import multiprocessing
import pickle


def send_the_last_block(blockchain, ss):
    print('hello world')
    while True:
        try:
            client_socket, client_address = ss.accept()
        except Exception as e:
            print(f"failed to establish connection with a client: {e}")
            continue
        try:
            client_socket.send(blockchain['data'].tail.data)
        except Exception as e:
            print(f'failed to send data to client {client_address}: {e}')
        finally:
            client_socket.close()


def listen_for_votes(blockchain, ss):
    pool = []
    while True:
        try:
            print('listening started')
            client_socket, client_address = ss.accept()
            if client_address in pool:
                client_socket.close()
                continue
            else:
                pool.append(client_address)
                print(f'client {client_address}, added')

        except Exception as e:
            print(f'failed to establish connection with a client: {e}')
            continue
        try:
            print(f'connection established with {client_address}')
            received_vote = client_socket.recv(4096)
            shared_chain = blockchain['data']
            shared_chain.add_block(received_vote)
            blockchain['data'] = shared_chain
            print(f"block added, size {blockchain['data'].size}")
        except Exception as e:
            print(f'failed to receive votes of client {client_address}: {e}')
        finally:
            client_socket.close()


if __name__ == '__main__':
    """process = multiprocessing.Process(target=modify, args=(shared_var,))
    process.start()
    process.join()

    print(f'final value of shared value: {shared_var.value}')"""
    # initial state -> [blockchain created, key pairs created, public key request, gather votes, election result]
    state = [0, 0, 0, 0, 0]
    child_process = None
    server_socket = None
    country_chain = None
    election_result = 0
    while True:
        command = input('command> ')

        if command == 'cb':  # create the blockchain
            if state[0] == 1:
                print('you have already created a blockchain !')
                continue
            manager = multiprocessing.Manager()
            country_chain = manager.dict({'data': BlockChain()})
            print('country blockchain created')
            state[0] = 1

        elif command == 'gnk':  # generate public and private keys
            if state[0] == 0:
                print('first create a blockchain using "cb" command.')
                continue
            if state[1] == 1:
                print('you have already created the key pairs.')
                continue
            public_key, private_key = paillier.generate_paillier_keypair()
            election_result = public_key.encrypt(election_result)
            print('public and private keys generated')
            chain = country_chain['data']
            chain.add_block(pickle.dumps(public_key))
            country_chain['data'] = chain
            print('public key added to the blockchain')
            state[1] = 1

        elif command == 'lfp':  # listen for public key requests
            if state[2] == 1:
                print('you are already in this phase.')
                continue
            if not (state[0] == 1 and state[1] == 1):
                print('you should create a blockchain and a key pair first. use "cb" and "gnk" commands')
                continue

            host = '127.0.0.1'
            port = 12000
            try:
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.bind((host, port))
                server_socket.listen()
            except Exception as e:
                print("couldn't establish a server, reset the lfp state using 'lfpr' command and try again: ", e)
                continue
            child_process = multiprocessing.Process(target=send_the_last_block, args=(country_chain, server_socket,))
            child_process.start()
            time.sleep(0.5)  # sleep so the child process starts its process.
            print('server is listening for requests.')
            # child_process.join()
            state[2] = 1

        # reset the lfp state in case of which an error occurred during the last phase and the child process terminated.
        elif command == 'lfpr':
            if state[2] == 0:
                print("you are not in the lfp state.")
                continue
            if state[2] == 1 and state[3] == 1:
                print("you have passed the lfp state.")
                continue
            if child_process is not None and child_process.is_alive():
                child_process.terminate()

            if server_socket is not None:
                server_socket.close()

            state[2] = 0
            print('lfp state reset.')

        elif command == 'gvs':  # gather the votes of election
            if state[3] == 1:
                print('you have already done this phase.')
                continue
            if not (state[0] == 1 and state[1] == 1 and state[2] == 1):
                print("""you can't gather the votes of election until you have completed all the previous phases:
                1. create the blockchain: "cb".
                2. create the key pair: "gnk".
                3. listen for public key request: "lfp".
                """)
                continue
            if not child_process.is_alive():
                print('lfp phase is not completed correctly, you can not run this phase.')
                state[2] = 0
                continue

            if server_socket is not None:
                server_socket.close()

            host = '127.0.0.1'
            port = 12001
            try:
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.bind((host, port))
                server_socket.listen()
            except Exception as e:
                print("couldn't establish a server, reset the lfp state using 'lfpr' command and try again: ", e)
                continue
            child_process.terminate()
            child_process = multiprocessing.Process(target=listen_for_votes, args=(country_chain, server_socket,))
            child_process.start()
            time.sleep(0.5)  # sleep so the child process starts its process.
            print('server is listening for requests.')
            # child_process.join()
            state[3] = 1

        # reset the gvs state in case of which an error occurred during the last phase and the child process terminated.
        elif command == 'gvsr':
            if state[3] == 0:
                print("you are not in the gvs state.")
                continue

            if state[3] == 1 and state[4] == 1:
                print("you have already done this phase.")
                continue

            if child_process is not None and child_process.is_alive():
                child_process.terminate()

            if server_socket is not None:
                server_socket.close()

            state[3] = 0
            print('gvs state reset.')

        elif command == 'elr':  # election result
            if state[4] == 1:
                print('you have already done this phase.')
                continue
            if not (state[0] == 1 and state[1] == 1 and state[2] == 1 and state[3] == 1):
                print("""you can't calculate the result of election until you have completed all the previous phases:
                1. create the blockchain: "cb".
                2. create the key pair: "gnk".
                3. listen for public key request: "lfp".
                4. gather the votes from local chains: "gvs".
                """)
                continue
            if not child_process.is_alive():
                print('gvs phase is not completed correctly, you can not run this command.')
                state[3] = 0
                continue

            if server_socket is not None:
                server_socket.close()

            child_process.terminate()
            #  first block is the genesis block and the second one is the public key
            current_block = country_chain['data'].head.next_block.next_block
            while current_block is not None:
                cipher_vote = pickle.loads(current_block.data)
                election_result = election_result + cipher_vote
                current_block = current_block.next_block

            plain_vote = private_key.decrypt(election_result)
            result = f'the election ends with result: {plain_vote}'
            chain = country_chain['data']
            chain.add_block(result.encode())
            country_chain = chain
            print(result)
            state[4] = 1
            break
