import os
from dotenv import load_dotenv
from swarms_client import SwarmsClient

load_dotenv()
client = SwarmsClient(api_key=os.getenv("SWARMS_API_KEY"))

def main():
    resp = client.swarms.run(
        name="hello-check",
        description="Minimal hello swarm",
        swarm_type="ConcurrentWorkflow",
        task="Reply exactly: Hello from Urban Crisis Planner!",
        agents=[{
            "agent_name": "Greeter",
            "description": "Says hello",
            "system_prompt": "You are concise.",
            "model_name": "gpt-4o-mini",
            "role": "greeter",
            "max_loops": 1,
            "max_tokens": 256,
            "temperature": 0.0
        }]
    )
    print(resp)

if __name__ == "__main__":
    main()
