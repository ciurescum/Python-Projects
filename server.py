#!/usr/bin/python

from socket import *
import threading
from random import randint


#In partea de server am creat 3 clase: Server, Jucator si Joc

# clasa care se ocupa cu gestionarea conexiunilor de la si catre clienti

class Server:
    def __init__(self):
        port = 1400
        #setam protocolul TCP si comunicatia implicita prin internet
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        #asociem socket-ul cu adresa (localhost) si portul (port) dorite
        self.server_socket.bind( ("localhost", port) )
        #deschidem socket-ul in modul server, 
        #la care se vor putea conecta cei 2 clienti
        self.server_socket.listen(2)
        
        print "Server initializat"
        print "Serverul asculta pe portul " + str(port) + ".."
        
        # vom crea o lista cu jucatorii care stabilesc conexiuni la server
        self.jucatori = []
        # pentru a crea echipele de jucatori se foloseste un lock
        self.matching_lock = threading.Lock()
        
 

    def start(self):
        # se asteapta stabilirea conexiunilor
        while True:
            data, client_addr = self.server_socket.accept()
            print "Conexiune stabilita cu adresa " + str(client_addr) + ".."

            # pentru fiecare conexiune noua la server se va crea o instanta de Jucator
            # si un thread corespunzator acesteia care va gestiona fiecare conexiune individual
            # in timp ce serverul continua sa primeasca conexiuni
            
            jucator_nou = Jucator(data)

            threading.Thread( target=self.client_thread, args=(jucator_nou,) ).start()
           
            

    def close(self):
        print "Serverul se inchide"
        self.server_socket.close()
       

    def client_thread(self, jucator):
        
        # fiecarui client i se va da un id unic
        jucator.send("A", str(jucator.id))
        # daca s-a primit id-ul
        if jucator.recv(2, "C") == "1":
            print "Jucatorul " + str(jucator.id) + " s-a conectat la server"
            # se adauga jucatorul la lista de jucatori
            self.jucatori.append(jucator)

        # If Player is in asteapta state try to match with another asteapta Player 
        if jucator.asteapta:
            print "Se gaseste oponent pentru jucatorul " + str(jucator.id) + ".."
        while jucator.asteapta:
            oponent = self.creaza_joc(jucator)
             
            if oponent is None:
                continue
            else:
                new_game = Joc(jucator, oponent)
                
                print "Incepe jocul intre jucatorul " + str(jucator.id) + " si jucatorul " + str(oponent.id) 

                new_game.start()
                
        self.jucatori.remove(jucator)

    def creaza_joc(self, jucator):
        # se aleg jucatorii
        self.matching_lock.acquire()
        try:
            # se parcurge lista de jucatori si se creeaza echipele
            for jucator_in_asteptare in self.jucatori:
                if jucator_in_asteptare.asteapta and jucator_in_asteptare is not jucator:
                    jucator.match = jucator_in_asteptare
                    jucator_in_asteptare.match = jucator
                    jucator.sign = "X"
                    jucator_in_asteptare.sign = "O"
                    jucator.asteapta = False
                    jucator_in_asteptare.asteapta = False
                    return jucator_in_asteptare
        finally:
            self.matching_lock.release()
        # Nu mai exista niciun jucator in lista
        return None
    
class Jucator:
    
    nr_jucatori = 0

    # se initializeaza obiectul jucator 
    def __init__(self, connection):
        Jucator.nr_jucatori += 1
        if Jucator.nr_jucatori >2:
            Jucator.nr_jucatori=1
            self.id = Jucator.nr_jucatori
        else:
            self.id = Jucator.nr_jucatori
        self.connection = connection
        # atunci cand se creaza o noua conexiune cu un jucator, 
        # acesta va fi in asteptare pana se va gasi un oponent
        self.asteapta = True

    # se trimit pachete de la server la client
    def send(self, cmd_type, msg):
        try:
            self.connection.send( (cmd_type+msg).encode() )
        except:
            print "Eroare la trimiterea pachetului catre clientul " + str(self.id) 
            self.pierdere_conexiune()

    
    #se primesc pachete de la client
    def recv(self, size, msg_type):
        try:
            msg = self.connection.recv(size).decode()

            # mesaj de inchidere  joc
            if msg[0] == "Q":
                print msg[1:]
                self.pierdere_conexiune(self)
            # mesaj de confirmare
            elif msg[0] == "C":
                return msg[1:]  
            # stare joc
            elif msg[0] == "G":
                return msg[1:]
            # mesaj necunoscut
            elif msg[0] != msg_type:
               
                print "Eroare:"
                print "mesaj necunoscut:  " + msg[0]
                print "alege dintre:                  " + msg_type
                print "Clientul se va deconecta de la server"
                
                self.pierdere_conexiune()
            return msg
        except:
    
            print "A aparut o eroare la trimiterea unui pachet de la jucatorul " + str(self.id) + "."
           
            self.pierdere_conexiune()

    # Serverul trimite infrmatii despre jucatori
    def trimite_info_jucatori(self):
        # trimite simbolul X sau 0 clientului
        self.send("R", self.sign)
        # primeste confirmare
        if self.recv(2, "C") != "2":
            print "nu s-a putut trimite X sau 0 clientului"
            self.pierdere_conexiune()
        # se trimite id-ul coechipierului
        self.send("M", str(self.match.id))
        # primeste confirmarea
        if self.recv(2, "C") != "3":
            print "nu s-a putut trimite id-ul coechipierului"
            self.pierdere_conexiune()

    # Functie folosita pentru a deconecta un jucator
    def pierdere_conexiune(self):
        print "Jucatorul " + str(self.id) + " s-a deconectat"

        try:
            self.match.send("C", "Acest joc s-a terminat.Oponentul a pierdut conexiunea.")
        except:
            pass
        self.connection.close()
        raise Exception

# clasa Joc gestioneaza starea jocului la nivel de server
class Joc:
    # Porneste un joc intre 2 jucatori
    def __init__(self, jucator1, jucator2):
        # initial tabela are numai spatii goale
        self.board = "EEEEEEEEEEEEEEEE"
        jucator1.trimite_info_jucatori()
        jucator2.trimite_info_jucatori()
        print "Jucatorul " + str(jucator1.id) + " va juca cu Jucatorul " + str(jucator2.id) + "."
      
        

        # se alege random cine incepe 
        rand_int = randint(0,1)
        if rand_int == 0:
            self.jucator1 = jucator1
            self.jucator2 = jucator2
        else:
            self.jucator1 = jucator2
            self.jucator2 = jucator1

       
    def start(self):
        while True:
            
        
            if self.move(self.jucator1, self.jucator2):
                return
            if self.move(self.jucator2, self.jucator1):
                return
         
   
    # se fac mutari pt fiecare jucator
    def move(self, jucator_activ, jucator_in_asteptare):
        #se trimite fiecarui jucator starea tablei de joc
        print "Tabela de joc updatata este:"
        print self.format_board()
        jucator_activ.send("G", self.board)
        if jucator_activ.recv(3, "C") != "1":
            print "A aparut o eroare la trimiterea tablei de joc"
        jucator_in_asteptare.send("G", self.board)
        if jucator_in_asteptare.recv(3, "C") != "1":
            print "A aparut o eroare la trimiterea tablei de joc"
            

        jucator_activ.send("G", "Go")
        if jucator_activ.recv(3, "C") != "2":
            print "A aparut o eroare la trimiterea tablei de joc"
        jucator_in_asteptare.send("G", "Wait")
        if jucator_in_asteptare.recv(3, "C") != "2":
            print "A aparut o eroare la trimiterea tablei de joc"

        # receptioneaza miscarea fiecarui jucator
        move =  jucator_activ.recv(3, "G")

        jucator_in_asteptare.send("G", str(move))
        self.update_board(int(move), jucator_activ.sign)

        # verifica daca jocul s-a terminat
        if self.verifica_conditie_castig():
            # Trimite-le jucatorilor configuratia tablei de joc
            jucator_activ.send("G", self.board)
            jucator_in_asteptare.send("G", self.board)
            # Afiseaza rezultatul
            jucator_activ.send("G", "Win")
            jucator_in_asteptare.send("G", "Lose")
            print "Jocul dintre jucatorul " + str(jucator_activ.id) + " si jucatorul " + str(jucator_in_asteptare.id) + " s-a incheiat"
            return True
        elif self.check_game_over():
            
            jucator_activ.send("G", self.board)
            jucator_in_asteptare.send("G", self.board)
            # Afiseaza rezultatul
            jucator_activ.send("G", "Draw")
            jucator_in_asteptare.send("G", "Draw")
            print "Jocul dintre jucatorul " + str(jucator_activ.id) + " si jucatorul " + str(jucator_in_asteptare.id) + " s-a incheiat"
            return True
        return False
    
    def format_board(self):
        board_arr = [str(i) for i in range(1,17)]
        
        try:
            for i in range(len(self.board)):
                if self.board[i] != "E":
                    board_arr[i] = self.board[i]
    
            return "| " + board_arr[0] + "| " + board_arr[1] + "| " + board_arr[2]  + "| " + board_arr[3] + "|\n"+"| " + board_arr[4] + "| " + board_arr[5]  + "| " + board_arr[6] + "| " + board_arr[7] + "|\n" + "| " + board_arr[8] + "|" + board_arr[9] + "|" + board_arr[10]+ "|" + board_arr[11] + "|\n" + "|" + board_arr[12]+ "|"+ board_arr[13] + "|" + board_arr[14]+ "|" + board_arr[15]+"|\n"
        except:
            print "S-a produs o eroare la tabela de joc"
            
    def update_board(self, move, sign):
        board_arr = list(self.board)
        board_arr[move-1] = sign
        self.board = "".join(board_arr)

    def check_game_over(self):
        for pos in self.board:
            if pos == "E":
                return False
        return True

    # gaseste castigatorul
    def verifica_conditie_castig(self):
        # verifica fiecare conditie de castig
        # prima linie
        if self.board[0] != "E" and self.board[0] == self.board[1] and self.board[0] == self.board[2] and self.board[0] == self.board[3]:
            return True
        # a doua linie
        elif self.board[4] != "E" and self.board[4] == self.board[5] and self.board[4] == self.board[6] and self.board[4] == self.board[7]:
            return True
        # a treia linie
        elif self.board[8] != "E" and self.board[8] == self.board[9] and self.board[8] == self.board[10] and self.board[8] == self.board[11]:
            return True
        # a patra linie
        elif self.board[12] != "E" and self.board[12] == self.board[13] and self.board[12] == self.board[14] and self.board[12] == self.board[15]:
            return True
        # prima coloana
        elif self.board[0] != "E" and self.board[0] == self.board[4] and self.board[0] == self.board[8] and self.board[0] == self.board[12]:
            return True
        # a doua col
        elif self.board[1] != "E" and self.board[1] == self.board[5] and self.board[1] == self.board[9] and self.board[1] == self.board[13]:
            return True
        # a treia col
        elif self.board[2] != "E" and self.board[2] == self.board[6] and self.board[2] == self.board[10] and self.board[2] == self.board[14]:
            return True
        # a patra col
        elif self.board[3] != "E" and self.board[3] == self.board[7] and self.board[3] == self.board[11] and self.board[3] == self.board[15]:
            return True
        # prima diagonala
        elif self.board[0] != "E" and self.board[0] == self.board[5] and self.board[0] == self.board[10] and self.board[0] == self.board[15]:
            return True
        # a doua diagonala
        elif self.board[3] != "E" and self.board[3] == self.board[6] and self.board[3] == self.board[9] and self.board[3] == self.board[12]:
            return True
        return False
    
if __name__ == "__main__":
    server = Server()
    #server.bind(1400)
    server.start()
