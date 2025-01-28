import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from util import generate_time_slots, generate_day_slots

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot('/', intents=intents)

# Create day slot list -> limited to 25 days in advance due to Discord's API
days = generate_day_slots()

# Create time slot list
time_slots = generate_time_slots()

locations = ["BEC", "CALL", "CHD", "CLE", "HSD", "TSC"]

class Questionnaire(discord.ui.Modal, title='Questionnaire Response'):
    name = discord.ui.TextInput(label='Name')
    answer = discord.ui.TextInput(label='Answer', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Thanks for your response, {self.name}!', ephemeral=True)

class ShiftDecisionView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(
        row=4,
        label="Submit",
        style=discord.ButtonStyle.success
    )
    async def submit_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        return await interaction.response.send_message(f"Thanks for your response, {button.label}")

    @discord.ui.button(
        row=4,
        label="Cancel",
        style=discord.ButtonStyle.danger
    )
    async def cancel_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        return await interaction.response.send_message(f"Thanks for your response, {button.label}")

    @discord.ui.button(
        row=4,
        label="Add Shift",
        style=discord.ButtonStyle.primary
    )
    async def add_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        return await interaction.response.send_message(f"Thanks for your response, {button.label}")

class ShiftTradeView(discord.ui.View):
    def __init__(self):
        super().__init__()

    chosen_location = ""
    chosen_from = ""
    chosen_to = ""
    chosen_date = ""
    cancel = False
    add_new = False

    @discord.ui.select(
        placeholder = "Choose a location",
        min_values = 1,
        max_values = 1,
        options = [discord.SelectOption(label=location) for location in locations])
    async def select_location_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.chosen_location = select.values[0]
        return await interaction.response.send_message(f"You chose {select.values[0]}!")

    @discord.ui.select(
        placeholder = "From",
        min_values = 1,
        max_values = 1,
        options = [discord.SelectOption(label=time.strftime("%I:%M %p"), value=time.strftime("%H:%M")) for time in time_slots]
    )
    async def select_from_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.chosen_from = select.values[0]
        return await interaction.response.send_message(f"You chose {select.values[0]}!")

    @discord.ui.select(
        placeholder = "To",
        min_values = 1,
        max_values = 1,
        options = [discord.SelectOption(label=time.strftime("%I:%M %p"), value=time.strftime("%H:%M")) for time in time_slots]
    )
    async def select_to_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.chosen_to = select.values[0]
        return await interaction.response.send_message(f"You chose {select.values[0]}!")

    @discord.ui.select(
        placeholder = "Date",
        min_values = 1,
        max_values = 1,
        options = [discord.SelectOption(label=day.isoformat(), value=day.isoformat()) for day in days]
    )
    async def select_date_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.chosen_date = select.values[0]
        return await interaction.response.send_message(f"You chose {select.values[0]}!")

    @discord.ui.button(
        row=4,
        label="Submit",
        style=discord.ButtonStyle.success
    )
    async def submit_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        return await interaction.response.send_message(f"Thanks for your response, {button.label}")

    @discord.ui.button(
        row=4,
        label="Cancel",
        style=discord.ButtonStyle.danger
    )
    async def cancel_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.cancel = True
        await interaction.message.delete()
        return await interaction.response.send_message("Operation cancelled.", ephemeral=True)

    @discord.ui.button(
        row=4,
        label="Add Shift",
        style=discord.ButtonStyle.primary
    )
    async def add_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.add_new = True
        next_view = ShiftTradeView()  # Create another instance of ShiftTradeView
        # Send new message with new view
        await interaction.channel.send("Add another shift:", view=next_view)
        return await interaction.response.send_message("Shift added.", ephemeral=True)

@client.command()
async def shift(ctx):
    """Open shift trade interface"""
    view = ShiftTradeView()
    await ctx.send("Select shift to trade:", view=view)
    await ctx.message.delete()

@client.command()
async def add(ctx, first: int, second: int):
    """Add two numbers"""
    result = first + second
    await ctx.send(f"{first} + {second} = {result}", ephemeral=True)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

if __name__ == "__main__":
    client.run(TOKEN)