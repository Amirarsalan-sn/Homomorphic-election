import hashlib


class Block:
    def __init__(self, data: bytes, prev_hash: bytes, prev_block):
        self.data = data
        self.previous_hash = prev_hash
        self.previous_block = prev_block
        self.next_block = None
        self.hash = self.calc_hash()

    def calc_hash(self):
        to_hash = self.data + self.previous_hash
        return hashlib.sha256(to_hash).digest()


class BlockChain:
    def __init__(self):
        self.head = Block(b'Genesis Block', b'0', None)
        self.tail = self.head
        self.size = 0

    def add_block(self, data: bytes):
        new_block = Block(data, self.tail.hash, self.tail)
        self.tail.next_block = new_block
        self.tail = new_block
        self.size += 1

    def get_size(self):
        return self.size

    def assert_correctness(self):
        current_block = self.head
        while current_block.next_block is not None:
            if current_block.calc_hash() != current_block.next_block.pervious_hash:
                return False
            current_block = current_block.next_block
        return True
