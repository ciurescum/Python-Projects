# Python_TicTacToe_Game

This is a TicTacToe Game developed in Python where many clients can connect to a server and play the game. 

**1.Instructions**

The server can be opened by running server.py, using the following command: ./server.py
The server will listen on port 1400 and will wait for clients to connect.

The client can be opened by running client.py, using the following command in another terminal: ./client.py 127.0.0.1
Every client will set a name and the server will provide a **unique id**.

**2. Functionality**

The game table will be a matrix with 4 columns and 4 lines (different for the usual 3x3 game table):

The client has to make a move and choose a number between 1 and 16. At every move, the server will send to every client the updated game table.
To win the game, the player has to create a row, column or diagonal full of "X" or "0".

Initially, there will be a list with all the server connected clients and once 2 players are connected, the game will start.
The server will choose who will make the first move using a random function.

The communication between the server and the client is a two-way communication. The server, as well as the client, can send packets to each other.
If the communication presents issues, there will be an error message printed on the client's console. 

The players' moves will be transfered between the two opponents by the server machine because the 2 clients are not connected to each other. Moreover, 
the server will send messages with the client id, the updated game table, the game state and if neccessary, some error messages.

After the server receives the player's move, it analyses the win conditions and will send to the clients some winning/ losing messages.
If a client wants to disconnect during the game, he/she can invoke the close function.

**3. Specifications**

The port I used for this game is 1400, but it can be **configurable**.
Moreover, the communication is set via **TCP Protocol**.

