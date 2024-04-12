# Homomorphic-election
Homomorphic encryption is a form of encryption that allows computations to be performed on encrypted data without decrypting it first. This means that operations can be performed directly on encrypted data, and the results will be the same as if they were performed on the unencrypted data. 

Applications of homomorphic encryption include secure cloud computing, privacy-preserving data analysis, and confidential computation in scenarios where sensitive data needs to be processed while maintaining confidentiality.

In this project, I've built an election system that keeps votes private using homomorphic encryption. Think of it like magic! I've also incorporated blockchains to make sure everyone can see how many votes are in play, ensuring transparency. For encrypting votes, I've chosen Paillier encryption. It's like wrapping each vote in a special, secret cloak. This cloak not only keeps the number of votes for each group hidden until the end of the election but also adds a fun twist – even if two people vote the same way, their encrypted votes look totally different! It's like giving each vote its own unique costume and it's because Paillier has probabilistic encryption. Another cool thing about Paillier is its homomorphic encryption. Instead of decrypting votes to count them, we can perform mathematical operations on the encrypted votes directly(adding up the ecrypted votes easilly), making tallying super easy. When the election is over, we unwrap the votes with our private keys and reveal the final results. You read the section below for more details on how the project works.
## Workflow
There are two type of blockchains:
  1. country blockchain or country chain.
  2. local blockchain or local chain.
Country blockchains can only be manipulated within the private network of that country, and local blockchains can only be manipulated from the private network of that city. This means that you can't participate in the election of a country or a city if you are not physically present there (or not connected to their private networks). Please note that I haven't implemented this part, as it falls under the responsibility of network engineers to take care of.

At the first of the election, authenticated officials put the public key of the goverment in the country chain. City officials then will pick up this key and put it inside the local chains of each city or village(again, officials authentication and their accessibilities is not implemented).
Then, people who reside within each local chain scope will go and register their votes. It is assumed that elections, like presidential elections, are always held between two factions. +1 vote means voting for faction A and negative vote -1 means voting for faction B. so people just need to register 1 or -1.
After that, each vote is encrypted using Pailliar enctyption and public key of the goverment and it is added to the local chain.
After the end of the voting period, the officials of the city or village collect the people's votes homomorphically and place them in the local and country chains.
Then, the goverment will collect the local chain votes homomorphically and decrypts the result using its private key and places it in the country's blockchain.
## Implementation and instructions
As you can see three python scripts are implemented. [BlockChain.py](BlockChain.py), [CountryChain.py](CountryChain.py) and [LocalChain.py](LocalChain.py). [BlockChain.py](BlockChain.py) is the implementation of blockchain. [CountryChain.py](CountryChain.py) is an interactive program for goverment officials to create the country blockchain, add the goverment public key, receive votes of local chains, release the election result etc... . [LocalChain.py](LocalChain.py) is an interactive program for cityt officials to create local chains, receive the public key, register votes and send the aggregated votes to the country chain.

### CountryChain commands
1. First, run the script [CountryChain.py](CountryChain.py).
2. `cb` (create blockchain), this command creates the country blockchain.
3. `gnk` (generate key), use this command for generating the key pair. after generating it, public key will be added to the country chain.
4. `lfp` (listen for public key request), running this command will cause the process to establish a server on ip and port specified in code(you can change it to your desired ip and port). It will create a socket
   and a child process, then, will pass this socket and the country chain to the child process, the child process will then listen for requests and send the public key of goverment after a tcp connection is
   established. Note that the main process and the child process are running concurrently so you can still run your desired commands after running this command.
5. `gvs` (gather votes), use this command whenever the election period is finished. This command will terminate `lfp` child process, establishes new server on the ip and port especified in code, and creates new
   child process to listen for connection requests and receiving aggregated votes of local chains. The main processs and the child process are again running concurrently. AGAIN, authentication is not within the
   scope of this project.
6. `elr` (election result), this command will add up the encrypted local votes and decrypts them using the goverment's private key and will release the election result and adds it to the country chain.
You should run these commands respectively otherwise, the process will not run the command and will show you proper messages and guides you towards the correct command.
### LocalChain commands
1. First, run the script [LocalChain.py](LocalChain.py).
2. `init`, this command will create the local chain.
3. `rcp ip port`, this command will send tcp connection request to the (ip, port) specified in the command. After the connection is established, the server will automatically send the public key. After the public
   key is received, it will be added to local chain.
4. `vote number`, this command will register a vote. It will encrypt it with the public key and adds it to the local chain. Note that the number should be only 1 or -1, otherwise the program will not accept the
   vote and will show a proper message.
5. `env ip port`, this command will add up the encrypted votes and sends the result to the ip and port specifed in the command.
You should run these commands respectively and with a correct format otherwise, the process will not run the command and will show you proper messages and guides you towards the correct command.
## Example
This, demonstrates an example of how to use and run commands. It shows a simple scenario where there are two local chains gathering votes, first one votes adds up to 7 and the second one adds up to -4. the result will be 3. The gif is 3mins long.

![example](images/example.gif)

