import discord
from discord.ext import commands
from dotenv import load_dotenv
import time
import os
import sqlite3

from util import generate_time_slots, generate_day_slots, setup_db

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot('/', intents=intents)

# Create day slot list -> limited to 25 days in advance due to Discord's API
days = generate_day_slots()

# Create time slot list
time_slots = generate_time_slots()

locations = ["Entire Shift","BEC", "CALL", "CHD", "CLE", "HSD", "TSC"]

class ClaimableShiftView(discord.ui.View):
    def __init__(self, invoker_username):
        self.invoker_username = invoker_username
        super().__init__(timeout=None)



    @discord.ui.button(
        custom_id="take_btn",
        label="Take this Shift",
        style = discord.ButtonStyle.success
    )
    async def take_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.display_name == self.invoker_username:
            return await interaction.response.send_message("You can't take your own shift", ephemeral=True)

        # Disable the button for everyone
        button.disabled = True
        button.label = "Shift has been taken"
        await interaction.message.edit(view=self)

        # Delete message from DB
        conn = sqlite3.connect('shifts.db')
        c = conn.cursor()
        c.execute('DELETE FROM active_shifts WHERE message_id = ?', (str(interaction.message.id),))
        conn.commit()
        conn.close()

        # Send confirmation message
        return await interaction.response.send_message(f"{interaction.user.display_name} has taken this shift given up by {self.invoker_username}")

class ShiftTradeFormView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=600)

    chosen_location = ""
    chosen_from = ""
    chosen_to = ""
    chosen_date = ""
    cancel = False
    add_new = False

    # Add a timeout handler
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        try:
            # Try to edit the message if it still exists
            if hasattr(self, 'message') and self.message:
                await self.message.edit(content="This form has expired. Please create another form", view=self)
        except Exception as e:
            print(f"Error handling timeout: {e}")
            pass

    @discord.ui.select(
        placeholder = "Choose a location",
        min_values = 1,
        max_values = 1,
        options = [discord.SelectOption(label=location) for location in locations])
    async def select_location_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.chosen_location = select.values[0]
        await interaction.response.defer()

    @discord.ui.select(
        placeholder = "From",
        min_values = 1,
        max_values = 1,
        options = [discord.SelectOption(label=time.strftime("%I:%M %p"), value=time.strftime("%I:%M %p")) for time in time_slots]
    )
    async def select_from_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.chosen_from = select.values[0]
        await interaction.response.defer()

    @discord.ui.select(
        placeholder = "To",
        min_values = 1,
        max_values = 1,
        options = [discord.SelectOption(label=time.strftime("%I:%M %p"), value=time.strftime("%I:%M %p")) for time in time_slots]
    )
    async def select_to_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.chosen_to = select.values[0]
        await interaction.response.defer()

    @discord.ui.select(
        placeholder = "Date",
        min_values = 1,
        max_values = 1,
        options = [discord.SelectOption(label=day.strftime("%A, %d %B %Y"), value=day.strftime("%A, %d %B %Y")) for day in days]
    )
    async def select_date_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.chosen_date = select.values[0]
        await interaction.response.defer()

    @discord.ui.button(
        row=4,
        label="Submit",
        style=discord.ButtonStyle.success
    )
    async def submit_callback(self, interaction: discord.Interaction, button: discord.ui.Button):

        missing = []

        if not self.chosen_location:
            missing.append("Location")
        if not self.chosen_from:
            missing.append("From")
        if not self.chosen_to:
            missing.append("To")
        if not self.chosen_date:
            missing.append("Date")

        if missing:
            missing_fields = '\n'.join(missing)
            error_message = f"Please select the following fields: \n" + f"{missing_fields}"
            return await interaction.response.send_message(error_message, ephemeral=True)

        if time.strptime(self.chosen_from, "%I:%M %p") > time.strptime(self.chosen_to, "%I:%M %p"):
            error_message = f"The From time cannot later than the To time"
            return await interaction.response.send_message(error_message, ephemeral=True)

        embed = discord.Embed(
            title="Shift up for grabs",
            color=discord.Color.blurple()
        )

        if self.chosen_location == "Entire Shift":
            embed.add_field(name="**Shift Details**", value=f"**{interaction.user.display_name}** would like their entire shift on **{self.chosen_date}** from **{self.chosen_from}** to **{self.chosen_to}** to be taken")
        else:
            embed.add_field(name="**Shift Details**", value=f"**{interaction.user.display_name}** would  like their shift in **{self.chosen_location}** on **{self.chosen_date}** from **{self.chosen_from}** to **{self.chosen_to}** to be taken")
        view = ClaimableShiftView(interaction.user.display_name)
        await interaction.message.delete()
        shift_message = await interaction.channel.send(embed=embed, view=view)

        conn = sqlite3.connect('shifts.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO active_shifts 
            (message_id, channel_id, invoker_username, location, shift_date, time_from, time_to) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(shift_message.id),
                str(interaction.channel.id),
                interaction.user.display_name,
                self.chosen_location,
                self.chosen_date,
                self.chosen_from,
                self.chosen_to
            )
        )

        conn.commit()
        conn.close()

        return shift_message


    @discord.ui.button(
        row=4,
        label="Cancel",
        style=discord.ButtonStyle.danger
    )
    async def cancel_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.cancel = True
        await interaction.message.delete()
        return await interaction.response.send_message("Shift Request Form has been deleted", ephemeral=True)

    @discord.ui.button(
        row=4,
        label="Add Shift",
        style=discord.ButtonStyle.primary
    )
    async def add_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.add_new = True
        next_view = ShiftTradeFormView()  # Create another instance of ShiftTradeView
        # Send new message with new view
        await interaction.channel.send("Add another shift:", view=next_view)
        return await interaction.response.send_message("Shift added.", ephemeral=True)

@client.command()
async def shift(ctx):
    """Open shift trade interface"""
    view = ShiftTradeFormView()
    message = await ctx.send("Select shift to trade:", view=view, ephemeral=True)
    view.message = message
    await ctx.message.delete()

@client.command()
async def add(ctx, first: int, second: int):
    """Add two numbers"""
    result = first + second
    await ctx.send(f"{first} + {second} = {result}", ephemeral=True)
    await ctx.message.delete()

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

    # Load database
    setup_db()

    # Load active shifts from database
    conn = sqlite3.connect('shifts.db')
    c = conn.cursor()
    c.execute('SELECT message_id, channel_id, invoker_username FROM active_shifts')
    active_shifts = c.fetchall()
    conn.close()

    # Register persistent views for each active shift
    for message_id, channel_id, invoker_username in active_shifts:
        client.add_view(ClaimableShiftView(invoker_username), message_id=int(message_id))

    print(f"Loaded {len(active_shifts)} active shifts.")

if __name__ == "__main__":
    client.run(TOKEN)