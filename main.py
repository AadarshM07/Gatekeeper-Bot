import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
from sheet import GoogleSheet
import json
import asyncio

load_dotenv()

token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

sheet = GoogleSheet("Gatekeeper")

# log channel 
log_channel_id = 1384956509200449708

with open("invite.json", "r") as f:
    faction_welcome_data = json.load(f)

faction_roles = [
    "Jedi-Order", "Sith-Legion", "Rebel-Alliance", "Galactic-Empire", "Mandalorian-Clan",
    "Clone-Battalion", "Droid-Assembly", "Wookiee-Tribe", "Tusken-Raiders", "Naboo-Royal-Guard",
    "Ewok-Village", "First-Order", "Resistance-Cell", "Shadow-Collective", "Republic-Senate"
]

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')

@bot.event
async def on_member_join(member):
    print("Member joined:", member.name)
    await asyncio.sleep(2)

    log_channel = bot.get_channel(log_channel_id)
    if log_channel is None:
        print("Log channel not found.")
        return

    checkmember = sheet.find_user(member.name)
    log_status = ""
    
    if checkmember:
        print(f'{member.name} is registered.')
        try:
            row = sheet.get_row(checkmember)
            role_name = row[1]  

        except Exception as e:
            print(f"[Sheet Error] Failed to render data for {member.name}: {e}")
            try:
                await member.send(
                    f"⚠️ Hi {member.name}, we encountered an issue loading your data from the system.\n"
                    f"Please try again later or contact <@758363520986775672> or <@891581154765979668> if the issue persists."
                )
            except discord.Forbidden:
                log_status = f"⚠️ Sheet error (DM failed): {str(e)}"
            else:
                log_status = f"⚠️ Sheet error: {str(e)}"

            await log_channel.send(
                f" **Sheet rendering issue for:** {member.mention} ({member.name}#{member.discriminator}, ID: {member.id})\n"
                f"{log_status}"
            )
            return

        if not role_name or (role_name not in faction_roles and role_name not in ["Knight", "Master","S3"]):
           
            try:
                await member.send(
                  f"👋 Hey {member.name}, you're registered but haven't been assigned a faction yet.\n"
                  f"If you don't get assigned within the next 6 hours, please reach out to <@758363520986775672> or <@891581154765979668> for assistance.\n"

                )
            except discord.Forbidden:
                log_status = "⚠️ Registered but no faction assigned (DM failed)"
            else:
                log_status = "⚠️ Registered but no faction assigned"
        
        else:
            
            await assign_role(member, role_name)
            await member_welcome(member, role_name)
            if role_name in faction_roles:
                await assign_role(member, "Padawan")
 
            try:
                if role_name in faction_roles:
                     await member.send(f"👋 Welcome! You've been assigned to **{role_name}**.")
            except discord.Forbidden:
                log_status = f"Assigned to: {role_name}" + (", Padawan" if role_name in faction_roles else "") + " (DM failed)"
            else:
                log_status = f"Assigned to: {role_name}" + (", Padawan" if role_name in faction_roles else "")

    else:
        print(f'{member.name} is not registered.')
        try:
            await member.send(
                f'👋 Welcome to the amFOSS 2025 Praveshan server, {member.name}!\n\n'
                f"It looks like you're not yet registered in our system. Access is currently limited to registered participants.\n\n"
                f"If you've already registered and believe this is a mistake, please contact <@758363520986775672> or <@891581154765979668>."
            )
        except discord.Forbidden:
            log_status = "Not registered (DM failed)"
        else:
            log_status = "Not registered"


    await log_channel.send(
        f" **New member joined:** {member.mention} ({member.name}#{member.discriminator})\n"
        f"{log_status}\n\n"
    )

async def member_welcome(name, role):
    if role in faction_welcome_data:
        welcome_info = faction_welcome_data[role]
        faction_channel_id = int(welcome_info["channel_id"])
        faction_mention = f"<#{faction_channel_id}>"

        await name.send(
            f"{welcome_info['message']} Head over to {faction_mention} to meet your fellow members!"
        )
    
    elif role == "S3":
        await name.send(
            f"Welcome to **amFOSS Praveshan 2025**, **{name.mention}**.\n\n"
            f"This is your chance to challenge yourself — not just to prove your skills, but to grow through discipline and consistency.\n"
            f"Go through the tasks sincerely, stay committed, and give it your best 💪\n\n"
            f"Wishing you all the best on this journey."
        )



async def assign_role(member, role_name):
    role = discord.utils.get(member.guild.roles, name=role_name)
    if role:
        try:
            await member.add_roles(role)
            print(f"Assigned role '{role_name}' to {member.name}")
        except discord.Forbidden:
            print(f"Missing permissions to assign role '{role_name}'")
        except Exception as e:
            print(f"Error assigning role: {e}")
    else:
        print(f"Role '{role_name}' not found in guild.")

@bot.command()
async def testjoin(ctx):
    await on_member_join(ctx.author)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
