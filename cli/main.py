# cli/main.py
from core.game import Game
from controller.game_controller import GameController
from agents.cli_human_agent import CliHumanAgent
from agents.simple_ai_agent import SimpleAIAgent

def main():
    game = Game(num_players=2)
    agents = {
        0: CliHumanAgent(),
        1: SimpleAIAgent(name="Computer"),
    }
    controller = GameController(game, agents)
    controller.run()

if __name__ == "__main__":
    main()
