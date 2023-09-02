
import pygame as p
import ChessEngine, ChessAI
import sys
from multiprocessing import Process, Queue

BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQUARE_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


def loadImages():
    """
    Initialize a global directory of images.
    This will be called exactly once in the main.
    """
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))
        

import speech_recognition as sr
recognizer = sr.Recognizer()



def recognize_speech():
    with sr.Microphone() as source:
        print("Listening...")
        engine.say("Listening...")
        engine.runAndWait()
         # Set timeout to 5 seconds and phrase_time_limit to 10 seconds
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

    try:
        recognized_text = recognizer.recognize_google(audio)
        print("Recognized Text:", recognized_text)
        return recognized_text.lower()
    except sr.UnknownValueError:
        print("Speech Recognition could not understand audio")
        engine.say("can you repeat once again")
        engine.runAndWait()
        return None
    except sr.RequestError as e:
        print("Could not request results from Speech Recognition service; {0}".format(e))
        return None



def process_speech_input(input_text):
    # Convert the recognized text into chess positions
    positions = input_text.split()
    if len(positions) > 2:
        print("Invalid input. Please provide two positions.")
        engine.say("Invalid input. Please provide two positions.")
        engine.runAndWait()
        return None, None

    # Convert chess positions to row and column indices
    try:
        if(len(input_text.split(' '))>1):
            if(len(positions[0])==2):
                current_position = (int(positions[0][1]) , ord(positions[0][0])-ord('a'))
                #next_position = (int(positions[1][1]) - 1, ord(positions[1][0]) - ord('a'))
            else:
                engine.say("voice not recognised . Please try again")
                engine.runAndWait()
                return None, None
            if(len(positions[1])==2):
                next_position = (int(positions[1][1]) , ord(positions[1][0])-ord('a'))
            else:
                engine.say("voice not recognised . Please try again")
                engine.runAndWait()
                return None, None
            if(next_position[0] >=0 and next_position[0]<=7 and next_position[1] >=0 and next_position[1]<=7):
                print("current_position",current_position)
                print("next_position",next_position)
                return current_position, next_position
            else:
                engine.say("voice not recognised . Please try again")
                engine.runAndWait()
                return None, None

        elif(len(input_text.split(' '))==1):
            if(len(positions[0])==4):
                current_position=(int(positions[0][0]), ord(positions[0][1])-ord('a'))
                next_position = (int(positions[0][2]), ord(positions[0][3])-ord('a'))
                print("current_position",current_position)
                print("next_position",next_position)
                return current_position, next_position
            else:
                engine.say("voice not recognised . Please try again")
                engine.runAndWait()
                return None, None

    except ValueError:
        print("Invalid input. Please provide valid chess positions.")
        engine.say("Invalid input. Please provide two positions.")
        engine.runAndWait()
        return None, None
    


import pyttsx3
engine = pyttsx3.init()
# engine.say("I will speak this text")
# engine.runAndWait()



def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    game_state = ChessEngine.GameState()
    valid_moves = game_state.getValidMoves()
    move_made = False  # flag variable for when a move is made
    animate = False  # flag variable for when we should animate a move
    loadImages()  # do this only once before while loop
    running = True
    square_selected = ()  # no square is selected initially, this will keep track of the last click of the user (tuple(row,col))
    player_clicks = []  # this will keep track of player clicks (two tuples)
    game_over = False
    ai_thinking = False
    move_undone = False
    move_finder_process = None
    move_log_font = p.font.SysFont("Arial", 14, False, False)
    #if false game is between ai vs ai
    player_one = True  # if a human is playing white, then this will be True, else False    
    player_two = False  # if a human is playing white, then this will be True, else False


#-------------------------------------------------------------------
#-------------------------------------------------------------------
#  from top to bottom 0,7
# from left to right a,b,c,d,e,f,g,h
#-------------------------------------------------------------------
#--------------------------------------------------------------------

    while running:
        human_turn = (game_state.white_to_move and player_one) or (not game_state.white_to_move and player_two)
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                sys.exit()
            elif e.type == p.KEYDOWN:
                if e.key == p.K_v:  # Use 'v' key to initiate voice input
                    if human_turn:
                        input_text = recognize_speech()
                        if input_text:
                            current_position, next_position = process_speech_input(input_text)
                            print("move")
                            print("current_position",current_position)
                            print("next_position",next_position)
                            if current_position and next_position:
                                print("move1")
                                move = ChessEngine.Move(current_position, next_position, game_state.board)
                                print("move2",move)
                                fl=True
                                for i in range(len(valid_moves)):
                                    if move == valid_moves[i]:
                                        game_state.makeMove(valid_moves[i])
                                        fl=False
                                        print("valid move",valid_moves[i])
                                        move_made = True
                                        animate = True
                                        square_selected = ()  # reset user clicks
                                        player_clicks = []
                                    # else:
                                    #     print("not valid")
                                    #     print(valid_moves[i])
                                if(fl==True):
                                    print("not valid move")
                                    engine.say("not valid move")
                                    engine.runAndWait()
                                if not move_made:
                                    player_clicks = [square_selected]
                elif e.key == p.K_z:  # undo when 'z' is pressed
                    print("z")
                    game_state.undoMove()
                    engine.say("undo move pressed")
                    engine.runAndWait()
                    move_made = True
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True
                elif e.key == p.K_r:  # reset the game when 'r' is pressed
                    game_state = ChessEngine.GameState()
                    valid_moves = game_state.getValidMoves()
                    square_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos()  # (x, y) location of the mouse
                    col = location[0] // SQUARE_SIZE
                    row = location[1] // SQUARE_SIZE
                    print("row,col",row,col)
                    if square_selected == (row, col) or col >= 8:  # user clicked the same square twice
                        square_selected = ()  # deselect
                        player_clicks = []  # clear clicks
                    else:
                        square_selected = (row, col)
                        player_clicks.append(square_selected)  # append for both 1st and 2nd click
                    if len(player_clicks) == 2 and human_turn:  # after 2nd click
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], game_state.board)
                        # print("move1",player_clicks[0])
                        # print("move2",player_clicks[1])
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                game_state.makeMove(valid_moves[i])
                                #print("valid",valid_moves[i])
                                move_made = True
                                animate = True
                                square_selected = ()  # reset user clicks
                                player_clicks = []
                        if not move_made:
                            player_clicks = [square_selected]
            



# # change it to voice input
#     while running:
#         human_turn = (game_state.white_to_move and player_one) or (not game_state.white_to_move and player_two)
#         for e in p.event.get():
#             if e.type == p.QUIT:
#                 p.quit()
#                 sys.exit()
#             # mouse handler
#             elif e.type == p.MOUSEBUTTONDOWN:
#                 if not game_over:
#                     location = p.mouse.get_pos()  # (x, y) location of the mouse
#                     col = location[0] // SQUARE_SIZE
#                     row = location[1] // SQUARE_SIZE
#                     print("row,col",row,col)
#                     if square_selected == (row, col) or col >= 8:  # user clicked the same square twice
#                         square_selected = ()  # deselect
#                         player_clicks = []  # clear clicks
#                     else:
#                         square_selected = (row, col)
#                         player_clicks.append(square_selected)  # append for both 1st and 2nd click
#                     if len(player_clicks) == 2 and human_turn:  # after 2nd click
#                         move = ChessEngine.Move(player_clicks[0], player_clicks[1], game_state.board)
#                         # print("move1",player_clicks[0])
#                         # print("move2",player_clicks[1])
#                         for i in range(len(valid_moves)):
#                             if move == valid_moves[i]:
#                                 game_state.makeMove(valid_moves[i])
#                                 #print("valid",valid_moves[i])
#                                 move_made = True
#                                 animate = True
#                                 square_selected = ()  # reset user clicks
#                                 player_clicks = []
#                         if not move_made:
#                             player_clicks = [square_selected]




            # # key handler
            # elif e.type == p.KEYDOWN:
            #     if e.key == p.K_z:  # undo when 'z' is pressed
            #         print("z")
            #         game_state.undoMove()
            #         print("z")
            #         move_made = True
            #         animate = False
            #         game_over = False
            #         if ai_thinking:
            #             move_finder_process.terminate()
            #             ai_thinking = False
            #         move_undone = True
            #     if e.key == p.K_r:  # reset the game when 'r' is pressed
            #         game_state = ChessEngine.GameState()
            #         valid_moves = game_state.getValidMoves()
            #         square_selected = ()
            #         player_clicks = []
            #         move_made = False
            #         animate = False
            #         game_over = False
            #         if ai_thinking:
            #             move_finder_process.terminate()
            #             ai_thinking = False
            #         move_undone = True




        # AI move finder
        if not game_over and not human_turn and not move_undone:
            if not ai_thinking:
                ai_thinking = True
                return_queue = Queue()  # used to pass data between threads
                move_finder_process = Process(target=ChessAI.findBestMove, args=(game_state, valid_moves, return_queue))
                print("move_finder_process",move_finder_process)
                move_finder_process.start()

            if not move_finder_process.is_alive():
                ai_move = return_queue.get()
                if ai_move is None:
                    ai_move = ChessAI.findRandomMove(valid_moves)
                game_state.makeMove(ai_move)
                print("ai move",ai_move)
                move_made = True
                animate = True
                ai_thinking = False

        if move_made:
            if animate:
                animateMove(game_state.move_log[-1], screen, game_state.board, clock)
            valid_moves = game_state.getValidMoves()
            move_made = False
            animate = False
            move_undone = False

        drawGameState(screen, game_state, valid_moves, square_selected)

        if not game_over:
            drawMoveLog(screen, game_state, move_log_font)

        if game_state.checkmate:
            game_over = True
            if game_state.white_to_move:
                engine.say("Black wins by checkmate")
                engine.runAndWait()
                drawEndGameText(screen, "Black wins by checkmate")
            else:
                engine.say("White wins by checkmate")
                engine.runAndWait()
                drawEndGameText(screen, "White wins by checkmate")

        elif game_state.stalemate:
            game_over = True
            engine.say("Stalemate")
            engine.runAndWait()
            drawEndGameText(screen, "Stalemate")

        clock.tick(MAX_FPS)
        p.display.flip()







def drawGameState(screen, game_state, valid_moves, square_selected):
    #Responsible for all the graphics within current game state.
    drawBoard(screen)  # draw squares on the board
    highlightSquares(screen, game_state, valid_moves, square_selected)
    drawPieces(screen, game_state.board)  # draw pieces on top of those squares


# def drawBoard(screen):
#     #Draw the squares on the board.
#     global colors
#     colors = [p.Color("white"), p.Color("gray")]
#     for row in range(DIMENSION):
#         for column in range(DIMENSION):
#             color = colors[((row + column) % 2)]
#             p.draw.rect(screen, color, p.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def drawBoard(screen):
    # Draw the squares on the board.
    global colors
    colors = [p.Color("white"), p.Color("gray")]

    
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[(row + column) % 2]
            p.draw.rect(screen, color, p.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

            if column == 0:
                number = str(row)  # Number from top to bottom
                font = p.font.Font(None, 24)  # Customize the font size as needed
                number_text = font.render(number, True, p.Color("black"))  # Customize the text color as needed
                text_rect = number_text.get_rect(topleft=(0, row * SQUARE_SIZE))
                screen.blit(number_text, text_rect)
            # Add numbers on the last row
            if row == DIMENSION - 1:
                number = chr(column + ord('a'))
                font = p.font.Font(None, 24)  # Customize the font size as needed
                number_text = font.render(number, True, p.Color("black"))  # Customize the text color as needed
                text_rect = number_text.get_rect(topleft=(column * SQUARE_SIZE, (DIMENSION - 1) * SQUARE_SIZE))
                screen.blit(number_text, text_rect)

    # for row in range(DIMENSION):
    #     for column in range(DIMENSION):
    #         if column == 0:
    #             number = str(column)
    #             font = p.font.Font(None, 24)  # Customize the font size as needed
    #             number_text = font.render(number, True, p.Color("black"))  # Customize the text color as needed
    #             text_rect = number_text.get_rect(topleft=(column * SQUARE_SIZE, (DIMENSION - 1) * SQUARE_SIZE))
    #             screen.blit(number_text, text_rect)
        
    

        





def highlightSquares(screen, game_state, valid_moves, square_selected):
    #Highlight square selected and moves for piece selected.
    if (len(game_state.move_log)) > 0:
        last_move = game_state.move_log[-1]
        s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
        s.set_alpha(100)
        s.fill(p.Color('green'))
        screen.blit(s, (last_move.end_col * SQUARE_SIZE, last_move.end_row * SQUARE_SIZE))
    if square_selected != ():
        row, col = square_selected
        if game_state.board[row][col][0] == (
                'w' if game_state.white_to_move else 'b'):  # square_selected is a piece that can be moved
            # highlight selected square
            s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(100)  # transparency value 0 -> transparent, 255 -> opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))
            # highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.start_row == row and move.start_col == col:
                    screen.blit(s, (move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE))


def drawPieces(screen, board):
    """
    Draw the pieces on the board using the current game_state.board
    """
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def drawMoveLog(screen, game_state, font):
    """
    Draws the move log.

    """
    move_log_rect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color('black'), move_log_rect)
    move_log = game_state.move_log
    move_texts = []
    for i in range(0, len(move_log), 2):
        move_string = str(i // 2 + 1) + '. ' + str(move_log[i]) + " "
        if i + 1 < len(move_log):
            move_string += str(move_log[i + 1]) + "  "
        move_texts.append(move_string)

    moves_per_row = 3
    padding = 5
    line_spacing = 2
    text_y = padding
    for i in range(0, len(move_texts), moves_per_row):
        text = ""
        for j in range(moves_per_row):
            if i + j < len(move_texts):
                text += move_texts[i + j]

        text_object = font.render(text, True, p.Color('white'))
        text_location = move_log_rect.move(padding, text_y)
        screen.blit(text_object, text_location)
        text_y += text_object.get_height() + line_spacing


def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    text_object = font.render(text, False, p.Color("gray"))
    text_location = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - text_object.get_width() / 2,
                                                                 BOARD_HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, False, p.Color('black'))
    screen.blit(text_object, text_location.move(2, 2))


def animateMove(move, screen, board, clock):
    """
    Animating a move
    """
    global colors
    d_row = move.end_row - move.start_row
    d_col = move.end_col - move.start_col
    frames_per_square = 10  # frames to move one square
    frame_count = (abs(d_row) + abs(d_col)) * frames_per_square
    for frame in range(frame_count + 1):
        row, col = (move.start_row + d_row * frame / frame_count, move.start_col + d_col * frame / frame_count)
        drawBoard(screen)
        drawPieces(screen, board)
        # erase the piece moved from its ending square
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        p.draw.rect(screen, color, end_square)
        # draw captured piece onto rectangle
        if move.piece_captured != '--':
            if move.is_enpassant_move:
                enpassant_row = move.end_row + 1 if move.piece_captured[0] == 'b' else move.end_row - 1
                end_square = p.Rect(move.end_col * SQUARE_SIZE, enpassant_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            screen.blit(IMAGES[move.piece_captured], end_square)
        # draw moving piece
        screen.blit(IMAGES[move.piece_moved], p.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        p.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
