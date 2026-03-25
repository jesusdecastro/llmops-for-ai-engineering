"""Quick demo of the TechShop agent."""

from dotenv import load_dotenv

from techshop_agent import create_agent

load_dotenv()

agent = create_agent()
result = agent("¿Qué portátiles tenéis disponibles?")
print(result)
