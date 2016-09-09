## Snail Racing : Design explanation

Snail Race is a two players-game. Players run a distance of 100m. The first player to arrive at position 100 has won the race. The running distance is 100m.

### What additional properties did you add to your models and why?
 - Snail Race is a two players-game. In the game class model, I kept track of the two players key and the game status(start, save, resume or over)
 - I added the Position model class. The class represents a plyer position in a game. This model is very useful when a game is save and later on resume
	- Position : mapped a player position on a game. This model class is very useful when a game is save and resumed
	 	- game : the game key
	 	- player : the player key 
	 	- position : player's current position in the game
 		- isPlayingNow : boolean property to know who's turn is to play
 - I also added the GameHistory model class to keep track of each move in a game. 
 	- GameHistory : logs data of all games
	 	- game : the game key
	 	- message : the log message I wan to record
	 	- date 
 - The Score model class recors player's score on differents games. I added a property "won" to know which player actually won the race.


### What were some of the trade-offs or struggles you faced when implementing the new game logic?
 - How to implement a two players game if the second player is not available to play?
 	- I choose to add a "computer" player. Which will be the default player if the first player did not select any an opponent
 - How to implement the "computer" moves?
  	- Since a computer is also a player, I had to decide if to code the functionnality of an automate playing. But this would have been to repeat my code. So I though it would be up to the API's user to make endpoints's calls for the computer to move.
 - How to rank players?
 	- While testing, I noticed that the winner wasn't necessarly the one with the highest score. Also, in analogy with a championship race, the gold winner was the one who when first at the most of the races. So I decided to rank the players by the number of winning race



 


