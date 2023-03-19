# fraudle

I developed a Wordle-like game where the computer tries to make you lose.

Each time you input a word, the computer will present you a color coded response that will allow the most words as possible.

While there are two or more words that fit the color constraints, the computer will not let you win! It's like playing Wordle with someone that said they chose a word, but can secretly swap words, given that the words still respect the contraints the cheater gave you.

If you can beat this algorithm in 6 guesses or less, contact me!

## How to run

### Locally
- To play in your terminal, launch `python main.py`
- In the terminal you can only play with english words

### Web app
- To run the flask app: `flask run` 
- In the web app you can only play with french words

## How to play
- Enter 5 letters words, case doesn't matter
- The game is a bit slow on the first guess, but after that it should be fine.
    - The computer does a lot of verification, with a lot of words. After eliminating a big part of these words, the rest of the game should be fast.
- The color coded response is the same as the Wordle:
    - Green = letter is in the right spot
    - Yellow = letter is present in the word, but somewhere else
    - Gray = letter is not in the word
- When you find the word (i.e. when you narrow the list of possible candidates down to one word), all squares will be green

## How to play in the web app
- Go to the URL and enter some words
- Go to [url]/reset to reset your game and start a new one

# Remarks 
 
## Solver
I included the solver made by [Chimrod](https://gist.github.com/Chimrod/575a2fe70e756c1f731fac6404320249) in "solver.ml" if you want to give it a try