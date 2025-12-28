from agents.agent import DevOpsAgent
from agents.logger import setup_logger

log = setup_logger("MAIN")


def main():
    log.info("Starting DevOps AI Agent")

    agent = DevOpsAgent()

    print("\n=== DevOps AI Agent (Local) ===")
    print("Type your issue (or 'exit'):\n")

    while True:
        log.info("Waiting for user input")
        user_input = input("> ")

        if user_input.lower() in ["exit", "quit"]:
            log.info("Exit requested")
            break

        log.info("User input received")
        response = agent.analyze(user_input)

        print("\n--- Analysis ---")
        print(response)
        print("\n")


if __name__ == "__main__":
    main()
