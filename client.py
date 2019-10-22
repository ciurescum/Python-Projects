#!/usr/bin/python

import socket
import sys

# In fisierul client am implementat 2 clase: Client si Jucator Client
# clasa Client care va gestiona conexiunile intre client si serve
class Client:
    def __init__(self):
        port = 1400
        address = sys.argv[1]
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print "Clientul se conecteaza la serverul cu adresa: " + address + " pe portul " + str(port)
        self.client_socket.settimeout(10)
        self.client_socket.connect( ("localhost", port) )
        
 
    # trimite pachete client->server.
    def send(self, cmd_type, msg):
        self.client_socket.send( (cmd_type+msg).encode() )
        

    # receptioneaza packete server->client.
    def recv(self, size, msg_type):
        
        self.client_socket.settimeout(60)
        msg = self.client_socket.recv(size).decode()
        
        # serverul a trimis un mesaj cu id-ul clientului
        if msg[0] == "A":
            return int(msg[1:])
        # serverul a trimis un mesaj cu 'x' sau '0'
        elif msg[0] == "R":
            return msg[1:]
        # serverul a trimis un mesaj legat de starea jocului
        elif msg[0] == "G":
            return msg[1:]
            
        # Serverul a trimis un mesaj legat de oponent
        elif msg[0] == "M":
            return int(msg[1:])
            
        # Serverul a trimis un mesaj necunoscut
        elif msg[0] != msg_type:
           
            print "Eroare"
            print "Clientul a receptionat un mesaj necunoscut: " + msg[0]
            print "Mesajul cunoscut:                  " + msg_type
            
            
        return msg
       

    # inchiderea socketului clientului
    def close(self):
      
        self.client_socket.shutdown(socket.SHUT_RDWR)
        self.client_socket.close()


class jucatorClient(Client):
    def __init__(self):
        Client.__init__(self)

    def start(self):
        self.id = self.recv(128, "A")
        self.send("C", "1")
        nume = raw_input("Introdu numele tau: ")
        print "Salut " + nume+ "! Esti jucatorul cu numarul " + str(self.id)
        
        
        self.semn = self.recv(2, "R")
        self.send("C", "2")
        print "Tu vei juca cu semnul " + self.semn + "!"
        print "Asteapta un oponent.."
        self.opp_id = int(self.recv(128, "M"))
        self.send("C", "3")
        self.joc_nou()

    def joc_nou(self):
        while True:
            print "**************************************************************************"
 
            self.board = self.recv(17, "G")
            self.send("C", "1")
            action = self.recv(5, "G")
            self.send("C", "2")

            if action == "Go":
               self.executa_mutare()
            elif action == "Wait":
                print "Asteapta ca oponentul sa faca o mutare."
                self.asteapta_mutare()
            elif action == "Draw":
                print
                print self.format_board()
                print "Remiza!  Jocul s-a incheiat."
                print
                break
            elif action == "Win":
                print
                print self.format_board()
                print "Ai castigat! Jocul s-a terminat"
                print
                break
            elif action == "Lose":
                print
                print self.format_board()
                print "Ai pierdut! Jocul s-a terminat"
                print
                break
            else:
               
                print "O eroare a aparut in timpul jocului"
              
                break
   
    def executa_mutare(self):
        
        print "Afiseaza pozitia pe care o alegi (numar intre 1-16)"
        print self.format_board()
        while True:
            mutare = raw_input("Mutarea ta este: ")
            if not mutare.isdigit():
                print "Mutare gresita! Introdu un numar intre 1-16"
            elif int(mutare) < 1 or int(mutare) > 16:
                print "Mutare gresita! Introdu un numar intre 1-16"
            elif self.board[ int(mutare)-1 ] != "E":
                print "Mutare gresita! Oponentul tau a ales deja aceasta mutare"
            
            else:
                self.send("G", str(mutare))
                break

    
    def asteapta_mutare(self):
        
        print self.format_board()
        mutare_opp = self.recv(3, "G")
        print "Oponentul a ales mutarea " + mutare_opp 

    def format_board(self):
        board_arr = [str(i) for i in range(1,17)]
        
        try:
            for i in range(len(self.board)):
                if self.board[i] != "E":
                    board_arr[i] = self.board[i]
    
            return "| " + board_arr[0] + "| " + board_arr[1] + "| " + board_arr[2]  + "| " + board_arr[3] + "|\n"+"| " + board_arr[4] + "| " + board_arr[5]  + "| " + board_arr[6] + "| " + board_arr[7] + "|\n" + "| " + board_arr[8] + "|" + board_arr[9] + "|" + board_arr[10]+ "|" + board_arr[11] + "|\n" + "|" + board_arr[12]+ "|"+ board_arr[13] + "|" + board_arr[14]+ "|" + board_arr[15]+"|\n"
        except:
            print "nu a mers sa faci tabela"

if __name__ == "__main__":
    client = jucatorClient()
    try:
        client.start()
    except:
        
        print "Eroare: jocul s-a sfarsit!"
       
    finally:
        client.close()
