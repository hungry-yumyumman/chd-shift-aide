import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix='/', intents=intents)



class ShiftTradeView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Shift 1", style=discord.ButtonStyle.primary)
    async def shift_one(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"{interaction.user.name} wants to trade Shift 1", ephemeral=True)

    @discord.ui.button(label="Shift 2", style=discord.ButtonStyle.secondary)
    async def shift_two(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"{interaction.user.name} wants to trade Shift 2", ephemeral=True)


@client.command()
async def shift(ctx):
    view = ShiftTradeView()
    await ctx.send("Which shift do you want to trade?", view=view)


@client.command()
async def add(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(f'<span style="font-size:12px;">{left} + {right} = {left + right}\n(Only you can see this)</span>', ephemeral=True)


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

def main():
    client.run(token=token)


if __name__ == "__main__":
    main()