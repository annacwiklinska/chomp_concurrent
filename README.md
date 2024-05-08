# Repository for university project - Concurrent Programming course

## Chomp

A game for two players

## 1. Board

The size of the board is determined by the first player, default size should be 5×4 (max 20×20).
The board is divided into smaller, square blocks - imitation of a chocolate bar.

## 2. Gameplay

During their turn, the player must choose one of the blocks and "eat it", i.e., remove it from the board along with the blocks below and to the right of it. The block in the upper left corner is poisoned – the player who takes it loses. The game starts with a random player. Only one player can make a move at a time. The selection of the "chocolate block" is done using the keyboard or mouse. It should be clearly indicated which player is currently making the move.

## 3. Winning Conditions

The player who "does not eat" the poisoned block wins. The game result should be announced with an appropriate message, and there should also be an option to start a new game.
