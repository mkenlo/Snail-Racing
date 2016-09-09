# Snail Racing

Snail Race is a two players-game. Players run a distance of 100m. The first player to arrive at position 100 has won the race. The running distance is 100m.

This repo provides with various endpoints for the game front-end implementation

# Setup and Installation

 - Install Python and Google App Engine Launcher
 - Clone this repo and Open the clone folder into Google App Engine Launcher
 - Select project and click the Run button
 - Run the app with the devserver using dev_appserver.py DIR, and ensure it's running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer

# Game Description

The running distance is 100m. At the beginning of the game, each player position is set to 0.
To move on the runway, player rolls a dice. A number between 1 and 6 is generated.

The runway has multiples positions that can make the runner moves faster or not: 
 - **TRIPLE POSITION**: If the player is on a triple position, his new position is triple of dice number.
 - **DOUBLE POSITION**: If the player is on a double position, his new position is double of dice number.
 - **NULL POSITION**  : If the player is on a null position, he is stuck, he can not move until he plays 6 by rolling the dice.

**Position values**:
 - TRIPLE = (10, 20, 30, 40, 50, 60, 70, 80, 90)
 - DOUBLE = (5, 15, 25, 35, 45, 55, 65, 75, 85)
 - NULL   = (7, 14, 21, 28, 42, 49, 56, 63, 77, 84)

### Constraints
 - If his opponent is at the new position of player, the opponent looses its position, he regress by 1.
 - If the new position computed is greater than 100, the player stays in his position. No move.

### Game over
The game is over when one of players arrives at position 100. 

### Score 
Each move computes a new position which is added to the player's score. The highest score is not necessary the winner of the race.
Players are ranks by the most won races. The best player is the one who won a maximun of race.

# Endpoints
 - signIn
 	- Path: /signin
 	- Method: POST
 	- Parameters: username(required), email(required)
 	- Returns: MessageForm
 	- Description: register a new user as player
 - new_game 
 	- Path: /new_game
 	- Method: POST
 	- Parameters: player's username(required), opponent's username
 	- Returns: NewGameForm
 	- Description: creates a new game.
 - roll_dice
 	- Path: /roll_dice
 	- Method: GET
 	- Parameters: none
 	- Returns: MessageForm
 	- Description: renders a random integer between 1 and 6
 - set_firstPlayer
 	- Path: /set_first_player
 	- Method: PUT
 	- Parameters: game's urlsafekey, player's username.(All required)
 	- Returns: MessageForm
 	- Description: sets the first player(to make a move) of the race
 - make_a_move
 	- Path: /make_a_move
 	- Method: PUT
 	- Parameters: game's urlsafekey, player's username, dice number.(All required)
 	- Returns: MakeMoveForm
 	- Description: enables a player to move during the race. Computes a new position with dice number and update players position and score
 - get_user_games
 	- Path: /get_user_games
 	- Method: GET
 	- Parameters: player's username (required)
 	- Returns: ListHistoryForm
 	- Description: returns all games of a given player
 - cancel_game
 	- Path: /cancel_game
 	- Method: DELETE
 	- Parameters: game urlsafekey (required)
 	- Returns: MessageForm
 	- Description: cancel/delete a given game
 - save_game
 	- Path: /save_game
 	- Method: PUT
 	- Parameters: game urlsafekey (required)
 	- Returns: MessageForm
 	- Description: save ongoing game to be played later
 - resume_game
 	- Path: /resume_game
 	- Method: PUT
 	- Parameters: game urlsafekey (required)
 	- Returns: MessageForm
 	- Description: resume a saved game
 - get_game_history
 	- Path: /get_game_history
 	- Method: GET
 	- Parameters: game urlsafekey (required)
 	- Returns: ListGameHistory
 	- Description: returns all moves made in a game
 - get_user_rankings
 	- Path: /get_user_rankings
 	- Method: GET
 	- Parameters: none
 	- Returns: ListRanking
 	- Description: returns all players and their perfomance

# How to test the API
 1. Create a player A with <code>signin</code> endpoint
 2. Create a game with <code>new_game</code> endpoint: If the second parameter is not given, a default player will be associated in the race. The default player username is "computer"
 3. Set first player of the game with <code>set_first_player</code> endpoint
 4. Get a diveValue with <code>roll_dice</code> endpoint
 5. Make a move with <code>make_a_move</code> endpoint
 6. Repeat the last two step with the opponent. Repeat vice-versa until the game is over

