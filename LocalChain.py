from phe import paillier
import pickle
from BlockChain import BlockChain
import socket

if __name__ == '__main__':
    local_chain = None
    state = 'init'
    public_key = None
    election_result = 0
    while True:
        command = input('command> ')

        if command == 'init':
            if state != 'init':
                print("you can't create a blockchain again.")
                continue
            local_chain = BlockChain()
            print('the local chain is created.')

            state = 'receive public'

        elif command.startswith('rcp'):  # rcp ip port -> receive public key from ip and port specified
            if state != 'receive public':
                print("""you can't run this command right now, it's either because you haven't created a blockchain
                yet, or you've run this command previously.""")
                continue
            ip = command.split()[1]
            port = int(command.split()[2])
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((ip, port))
            except Exception as e:
                print(f"failed to establish connection with the server: {e}")
                continue
            try:
                public_key_byte = client_socket.recv(4096)
                public_key = pickle.loads(public_key_byte)
                local_chain.add_block(public_key_byte.decode('utf-8'))
                election_result = public_key.encrypt(election_result)
            except Exception as e:
                print(f"failed to receive the public key from server: {e}")
                continue
            finally:
                client_socket.close()

            print('public_key received successfully.')
            state = 'voting'

        elif command.startswith('vote'):
            if state != 'voting':
                print("""you can't run this command right now, it's either because you haven't received the public key
                yet, or you've run this command previously.""")
                continue

            vote = int(command.split()[1])
            if not(vote == 1 or vote == -1):
                print('invalid vote.')
                continue
            cipher_vote = public_key.encrypt(vote)
            local_chain.add_block(pickle.dumps(cipher_vote).decode('utf-8'))
            print('vote added successfully.')

        elif command.startswith('env'):  # env ip port -> end vote
            if state != 'voting':
                print("""you can't run this command right now, you haven't started the voting.
                or it's finished.""")
                continue

            state = 'send-votes'
            #  first block is the genesis block and the second one is the public key.
            current_block = local_chain.head.next_block.next_block
            while current_block is not None:
                cipher_vote = pickle.loads(current_block.data.encode())
                election_result = election_result + cipher_vote
                current_block = current_block.next_block

            ip = command.split()[1]
            port = int(command.split()[2])
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((ip, port))
            except Exception as e:
                print(f"failed to establish connection with the server: {e}")
                continue

            try:
                client_socket.send(pickle.loads(election_result))
            except Exception as e:
                print(f"failed to send data to the server: {e}")
                continue
            finally:
                client_socket.close()

            local_chain.add_block(f'election sum:{pickle.dumps(election_result)}')

            print('election result calculated and added to the local and country chains.')
            break
