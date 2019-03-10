from http.server import BaseHTTPRequestHandler, HTTPServer
import random

hostName = "localhost"
serverPort = 8080
randomRange = 1000
games = {}
choices = ["Rock", "Paper", "Scissors"]


def RPS(me, you):
    if me == you:
        return 2
    elif me == "Rock":
        if you == "Paper":
            return 1
        else:
            return 0
    elif me == "Paper":
        if you == "Scissors":
            return 1
        else:
            return 0
    elif me == "Scissors":
        if you == "Rock":
            return 1
        else:
            return 0


def findUniqueId(games):        # no two games can have the same id, so we need to find a unique id
    if randomRange == len(games):   # user reached the max number of unfinished games, make a request to play them
        return None
    sessionId = str(random.randint(0, randomRange))
    if sessionId in games:      # if random id is in use then try another random id
        return findUniqueId(games)
    else:                       # if random id is unique id then return it
        return sessionId


class MyServer(BaseHTTPRequestHandler):

    def do_GET(self):

        request = str(self.path)
        command = request.split("?")
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        if command[0] == "/newGame":
            sessionId = findUniqueId(games)

            # incase of there is no more unique id, give an error and quit the function
            if sessionId == None:
                self.wfile.write(bytes("\nYou exceed the number of total games. Please play unfinished games.\n\n", "utf-8"))
                return

            roundNum = command[1].split("=")[1]
            rounds = []
            games[sessionId] = [int(roundNum), 0, rounds, 0, 0]   # totalRounds, currentRound, roundResults, wins, loses

            if int(roundNum) <= 0:      # to play a game round number can not be equal or smaller than zero
                self.wfile.write(bytes("\nRound number must be greater than 0 to start the game!\n\n", "utf-8"))
            else:
                self.wfile.write(bytes("\nNew Rock-Paper-Scissors game started\n", "utf-8"))
                self.wfile.write(bytes("Session ID = %s\n" % str(sessionId), "utf-8"))
                self.wfile.write(bytes("\nto play Rock: http://localhost:8080/play?choose=rock&id=%s" % str(sessionId), "utf-8"))
                self.wfile.write(bytes("\nto play Paper: http://localhost:8080/play?choose=paper&id=%s" % str(sessionId), "utf-8"))
                self.wfile.write(bytes("\nto play Scissors: http://localhost:8080/play?choose=scissors&id=%s\n\n" % str(sessionId), "utf-8"))

        elif command[0] == "/play":

            playCommands = command[1].split("&")
            idOrChoose = playCommands[0].split("=")

            # "id" and "choose" keywords have no order so check which one is first
            if idOrChoose[0] == "id":
                id = idOrChoose[1]
                choose = playCommands[1].split("=")[1]

            elif idOrChoose[0] == "choose":
                choose = idOrChoose[1]
                id = playCommands[1].split("=")[1]

            if id in games:         # if there is a game has that id, user can play it
                gameInfo = games[id]
                totalRound = gameInfo[0]
                gameInfo[1] += 1        # increase round number
                curRound = gameInfo[1]
                me = choices[random.randint(0, 2)]
                status = RPS(me.capitalize(), choose.capitalize())

                self.wfile.write(bytes("\n-> ROUND %s\n" % curRound, "utf-8"))
                self.wfile.write(bytes("\nme: %s\n" % me.upper(), "utf-8"))
                self.wfile.write(bytes("you: %s\n\n" % choose.upper(), "utf-8"))

                if status == 0:     # status lose
                    self.wfile.write(bytes("YOU LOST THIS ROUND!!\n", "utf-8"))
                    gameInfo[4] += 1
                elif status == 1:   # status win
                    self.wfile.write(bytes("YOU WON THIS ROUND!!\n", "utf-8"))
                    gameInfo[3] += 1
                else:       # status tie
                    self.wfile.write(bytes("TIE!!\n", "utf-8"))

                gameInfo[2].append([me.capitalize(), choose.capitalize()])
                rounds = gameInfo[2]

                if curRound >= totalRound:      # user played all rounds
                    self.wfile.write(bytes("\n-> GAME COMPLETED", "utf-8"))
                    for i in range(totalRound):
                        self.wfile.write(bytes("\nRound %s: " % str(i+1), "utf-8"))
                        self.wfile.write(bytes("%s vs %s" % (rounds[i][0], rounds[i][1]), "utf-8"))

                    self.wfile.write(bytes("\n\n%s vs %s\n" % (gameInfo[4], gameInfo[3]), "utf-8"))
                    if gameInfo[3] > gameInfo[4]:
                        self.wfile.write(bytes("YOU WON !!\n\n", "utf-8"))
                    elif gameInfo[4] > gameInfo[3]:
                        self.wfile.write(bytes("YOU LOST !!\n\n", "utf-8"))
                    else:
                        self.wfile.write(bytes("TIE !!\n\n", "utf-8"))
                    games.pop(id)       # if game is completed then delete it

                else:
                    self.wfile.write(bytes("\nThere is %s more round.\n\n" % str(totalRound-curRound), "utf-8"))

            else:       # if there is no game has that id give an error
                self.wfile.write(bytes("\nFirst you need to create a new game.\n\n", "utf-8"))


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
