import socket
from phe import paillier
from BlockChain import BlockChain
import multiprocessing
import pickle


def send_the_last_block(blockchain):
    host = '127.0.0.1'
    port = 12000
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen()
    except Exception as e:
        print("couldn't establish a server, reset the lfp state using 'lfpr' command and try again: ", e)
        return
    while True:
        try:
            client_socket, client_address = server_socket.accept()
        except Exception as e:
            print(f"failed to establish connection with a client: {e}")
            continue
        try:
            client_socket.send(blockchain.tail.data.encode())
        except Exception as e:
            print(f'failed to send data to client {client_address}: {e}')
        finally:
            client_socket.close()


def listen_for_votes(blockchain: BlockChain):
    host = '127.0.0.1'
    port = 12001
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen()
    except Exception as e:
        print("couldn't establish a server, reset the gvs state using 'gvsr' command and try again: ", e)
        return

    while True:
        try:
            client_socket, client_address = server_socket.accept()
        except Exception as e:
            print(f'failed to establish connection with a client: {e}')
            continue
        try:
            received_vote = client_socket.recv(4096)
            blockchain.add_block(received_vote.decode('utf-8'))
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
    country_chain = None
    child_process = None
    election_result = 0
    while True:
        command = input('command> ')

        if command == 'cb':  # create the blockchain
            if state[0] == 1:
                print('you have already created a blockchain !')
                continue
            country_chain = BlockChain()
            print('country blockchain created')
            state[0] = 1

        elif command == 'gnk':  # generate public and private keys
            if state[0] == 0:
                print('first create a blockchain using "cb" command.')
            if state[1] == 1:
                print('you have already created the key pairs.')
            public_key, private_key = paillier.generate_paillier_keypair()
            print('public and private keys generated')
            country_chain.add_block(pickle.dumps(public_key).decode('utf-8'))
            print('public key added to the blockchain')
            state[1] = 1

        elif command == 'lfp':  # listen for public key requests
            if state[2] == 1:
                print('you are already in this phase.')
                continue
            if not (state[0] == 1 and state[1] == 1):
                print('you should create a blockchain and a key pair first. use "bc" and "gnk" commands')
                continue
            child_process = multiprocessing.Process(target=send_the_last_block, args=(country_chain,))
            child_process.start()
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

            child_process.terminate()
            child_process = multiprocessing.Process(target=listen_for_votes, args=(country_chain,))
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
            child_process.terminate()
            #  first block is the genesis block and the second one is the public key
            current_block = country_chain.head.next_block.next_block
            while current_block is not None:
                cipher_vote = pickle.loads(current_block.data.encode())
                election_result = election_result + cipher_vote
                current_block = current_block.next_block

            plain_vote = private_key.decrypt(election_result)
            result = f'the election ends with result: {plain_vote}'
            country_chain.add_block(result)
            print(result)
            state[4] = 1
            break
