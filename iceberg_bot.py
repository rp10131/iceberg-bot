import discord, os, random
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# La variable intents almacena los privilegios del bot
intents = discord.Intents.all()
# Activar el privilegio de lectura de mensajes
intents.message_content = True
# Crear un bot en la variable cliente y transferirle los privilegios
client = commands.Bot(command_prefix=';', intents=intents)

@client.event
async def on_ready():
    presencia = discord.Activity(type=discord.ActivityType.watching, name="mis comandos")
    await client.change_presence(activity=presencia)
    print(f'\n{client.user} está en línea! \nActividad: {presencia}\nLatencia: {round(client.latency * 1000)}ms')

@client.event
async def on_message(message):

    if message.author == client.user:
        return
    if message.content.startswith('hola'):
        await message.channel.send("Hola!")
    elif message.content.startswith('adiós'):
        await message.channel.send("\U0001f642")
    elif message.content.startswith('!ping'):
        await message.channel.send(f"Pong!\nLatencia: {round(client.latency * 1000)}ms")

    await client.process_commands(message)

@client.command(name='manualidad')
async def manualidad(ctx):
    manualidad = {
        'Maceta': {'descripcion': 'Maceta con botellas de plástico', 'paso1':'Limpia el envase que tengas y remuévele las etiquetas.','paso2':'Corta la parte superior del envase si es necesario (Ej. Si es una botella)','paso3':'Rellena el envase con tierrita y siembra algo!'},
        'Comedero': {'descripcion': 'Comedero para pájaros hecho con cartón', 'paso1': 'Limpia el envase que tengas. Puede ser una cajita de jugo','paso2':'Haz una abertura grande en el costado para que las aves puedan acceder a la comida','paso3':'Llena el interior con semillas para aves y déjalo en un lugar seguro donde pueda ser usado!'}
    }

    cual_m = random.choice(list(manualidad.keys()))

    embed = discord.Embed(
        title=f"Manualidad ecológica: {cual_m}", 
        description=f"{manualidad[cual_m]['descripcion']}.", 
        color=discord.Color.green() 
    )

    embed.add_field(name="Paso 1", value=f"{manualidad[cual_m]['paso1']}.", inline=False)
    embed.add_field(name="Paso 2", value=f"{manualidad[cual_m]['paso2']}.", inline=True)
    embed.add_field(name="Paso 3", value=f"{manualidad[cual_m]['paso3']}.", inline=True)

    embed.set_footer(text="Listo!")
    embed.set_author(name="Autor", icon_url="https://cdn.discordapp.com/avatars/751880654463172639/ba126d52a8e695cd0138c06a429d76c4.webp?size=2048")

    await ctx.send(embed=embed)



client.run(TOKEN)