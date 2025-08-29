from Polymer_waste_recycling import team_Config, analyzer
import asyncio

async def main():
    plastic_type= input("Describe the polymer (plastic) waste type eg.- PET bottles, HDPE containers, PP packaging. " \
    "Mention the Scale like Daily/annual waste amount (e.g., 10 tons/day) and Constraints like Cost limits, maximum acceptable CO₂ emissions, preferred recycling method if any: ")  # User input

    team = await team_Config(plastic_type)

    async for message in analyzer(team):
        print('-' * 70)
        print(message)

if __name__ == "__main__":
    asyncio.run(main())
