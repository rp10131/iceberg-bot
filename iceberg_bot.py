import discord, os, random, asyncio
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

impacto_usuarios = {}
suscripciones = {}

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
    print(f'\n{client.user} está en línea! \nLatencia: {round(client.latency * 1000)}ms')
    enviar_recordatorios.start()

@client.command()
@commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
async def descansar(ctx):
    await ctx.send(f"{ctx.author.mention}, has llamado al comando. Debes esperar 10 segundos antes de usarlo nuevamente.")

@client.event
async def on_message(message):

    if message.author == client.user:
        return
    if message.content.startswith('!ping'):
        await message.channel.send(f"Pong!\nLatencia: {round(client.latency * 1000)}ms")

    await client.process_commands(message)

@tasks.loop(hours=4)
async def enviar_recordatorios():
    recordatorios = [
    "💡 Recuerda apagar las luces si nadie está ahí!",
    "💧 Has regado tus plantas hoy? Si tienes plantas, claro.",
    "♻️ Si te es posible, intenta separar la basura reciclable!",
    "🚲 Si te es posible, usa tu bicicleta en lugar del auto. El planeta lo agradecerá!",
    "👜 Cuando tengas basura contigo afuera de casa, no la tires hasta encontrar un bote de basura.",
    "🍄‍🟫 Los descomponedores son indispensables en la naturaleza, así que vigila que no muchos otros animales los persigan."
]
    for user_id, suscrito in suscripciones.items():
        if suscrito:
            user = await client.fetch_user(user_id)  # Obtiene el objeto del usuario
            try:
                mensaje = random.choice(recordatorios)  # Selecciona un recordatorio al azar
                await user.send(mensaje)
            except discord.Forbidden:
                print(f"No se pudo enviar un mensaje a {user_id}. Posiblemente tienen bloqueados los DMs.")

@client.command()
@commands.cooldown(rate=2, per=10, type=commands.BucketType.user)
async def suscribirse(ctx):
    usuario = ctx.author.id  # Usa el ID del usuario para identificarlo
    if usuario in suscripciones and suscripciones[usuario]:
        suscripciones[usuario] = False
        await ctx.author.send(f"No recibirás más recordatorios hasta que los vuelvas a activar 💤")
    else:
        try:
            suscripciones[usuario] = True
            await ctx.author.send("Gracias por suscribirte a los recordatorios! 🎉🌍. Tendrás uno cada 4 horas! ❤")
        except discord.Forbidden:
            await ctx.send(f"... No pude enviarte un DM 🥹. Asegúrate de tener habilitados los mensajes directos y vuelve a llamar al comando.")

@client.command(name='manualidad')
@commands.cooldown(rate=1, per=30, type=commands.BucketType.user)
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

@client.command(name='tip_reciclaje',help='Muestra tips para reciclar.')
async def reciclar(ctx):
    tips = [
        "Antes de reciclar botellas de plástico, asegúrate de enjuagarlas para eliminar residuos.",
        "Separa el papel limpio del que tiene restos de grasa o comida; este último no se puede reciclar.",
        "Recuerda retirar las tapas de los frascos de vidrio antes de reciclarlos.",
        "No aplastes las botellas de plástico, ya que esto puede dificultar su clasificación en las plantas de reciclaje.",
        "Reciclar una lata de aluminio puede ahorrar suficiente energía para mantener encendida una bombilla por 3 horas."
    ]
    await ctx.reply(f"Un tip! ♻️\n{random.choice(tips)}")

@client.command()
@commands.cooldown(rate=3, per=60, type=commands.BucketType.user)
async def registrar(ctx, accion: str=None):
    acciones_ecologicas = {
    "reciclar": 1,  # 1 kg de CO₂ evitado
    "transporte_publico": 2,  # 2 kg de CO₂ evitados
    "ahorrar_agua": 0.5  # 0.5 kg de CO₂ equivalente por ahorro
}
    usuario = str(ctx.author)

    if accion in acciones_ecologicas: # Verifica si la acción existe en las acciones ecológicas
        impacto = acciones_ecologicas[accion]
        
        if usuario not in impacto_usuarios:
            impacto_usuarios[usuario] = {'impacto': 0, 'coins': 0,'dms':False}
            if impacto_usuarios[usuario]['dms'] == False:
                try:
                    await ctx.author.send(f"Gracias por usar este bot. Se usarán DMs con frecuencia.")
                    await ctx.send(f"Te he enviado un mensaje directo. 📩",delete_after=10.0)
                    impacto_usuarios[usuario]['dms'] = True
                except discord.Forbidden:
                    await ctx.reply(f"{client.name} usa DMs con frecuencia. Por favor, habilita tus DMs para asegurar que el bot funcione correctamente.")

        impacto_usuarios[usuario]['impacto'] += impacto
        impacto_usuarios[usuario]['coins'] += random.randint(1,3)

        await ctx.send(f"♻️ ¡{ctx.author.mention} ha registrado la acción '{accion}'! Has contribuido a evitar {impacto} kg de CO₂. 🌍")
    else:
        await ctx.message.delete()
        await ctx.send(f"⚠️ No se reconoce '{accion}'. Las acciones disponibles son: {', '.join(acciones_ecologicas.keys())}.",delete_after=60.0)

@client.command()
async def impacto(ctx, persona: str = 'yo'):
    if persona not in ['yo','servidor']:
        persona = 'yo'
    if persona == 'yo':
        usuario = str(ctx.author)
        if usuario in impacto_usuarios:
            total = impacto_usuarios[usuario]['impacto']
            await ctx.reply(f"🌱 Has evitado un total de {total} kg de CO₂. Bien hecho!")
        else:
            await ctx.reply(f"🌱 Aún no has registrado ninguna acción. Registra tus apoyos ecológicos pronto!")
    elif persona == 'servidor':
        total_servidor = 0

        for usuario in impacto_usuarios.keys():
            total_servidor += impacto_usuarios[usuario]['impacto']

        await ctx.send(f"{client.guild} ha evitado un total de {total_servidor} kg de CO₂. Bien hecho!")

@client.command(description="Comprar artículos en la tienda del bot")
@commands.cooldown(rate=2, per=20, type=commands.BucketType.user)
async def comprar(ctx, *, articulo: str=None):
    tienda_items = {
        "Chincheta": 8,
        "Color de rol": 15
    }
    mensaje = "🛍️ **Tienda del Bot** 🛍️\n"
    for item, precio in tienda_items.items():
        mensaje += f"- {item}: {precio} monedas\n"
    mensaje += "Usa `;comprar <nombre del artículo>` para adquirir algo."

    usuario = str(ctx.author)

    if articulo in tienda_items:
        precio = tienda_items[articulo]

        if usuario in impacto_usuarios and impacto_usuarios[usuario]['coins'] >= precio:
            impacto_usuarios[usuario]['coins'] -= precio
            
            # Añadir el permiso al usuario
            if articulo == 'Chincheta':
                if "permisos" not in impacto_usuarios[usuario]:
                    impacto_usuarios[usuario]["permisos"] = 0
                impacto_usuarios[usuario]["permisos"] += 1

            elif articulo == 'Color de rol':
                await ctx.send('Los colores de rol disponible son los 3 colores primarios.')
                colores_roles = {
        "rojo": 1361824783372779530,  # ID del rol rojo
        "azul": 1361824929078837311,  # ID del rol azul
        "amarillo": 1361825006484590702  # ID del rol amarillo
    }
                def color_correcto(m):
                    return (m.author == ctx.author) and (m.content.lower() in colores_roles.keys()) and (m.channel == ctx.channel)
                
                try:
                    color = await client.wait_for('message', check=color_correcto, timeout=15.0)
                    rol_nuevo = discord.utils.get(ctx.guild.roles, id=colores_roles[color.content.lower()])

                    if rol_nuevo: # Revisa los roles actuales del usuario y elimina otros roles de color
                        roles_usuario = ctx.author.roles
                        roles_color_actuales = [discord.utils.get(ctx.guild.roles, id=id) for id in colores_roles.values()]
                        
                        for rol in roles_color_actuales:
                            if rol in roles_usuario and rol != rol_nuevo:
                                await ctx.author.remove_roles(rol)
                        
                        # Asigna el nuevo rol
                        await ctx.author.add_roles(rol_nuevo)
                        await ctx.send(f"Se ha asignado el rol '{rol_nuevo.name}' a {ctx.author.mention}! Los roles anteriores de color han sido removidos.")
                    else:
                        await ctx.send("Verifica el ID del rol.",delete_after=10.0)
                except asyncio.TimeoutError:
                    impacto_usuarios[usuario]['coins'] += precio
                    await ctx.send('⏳ Los colores de rol disponibles son los 3 colores primarios.')

            await ctx.send(f"🎉 ¡{ctx.author.mention} ha comprado '{articulo}' por {precio} monedas! Ahora tienes {impacto_usuarios[usuario]['coins']} monedas y {impacto_usuarios[usuario]['permisos']} permiso(s) para fijar mensajes.")
        else:
            await ctx.message.delete()
            await ctx.author.send(f"⚠️ {ctx.author.name}, no tienes suficientes monedas para comprar '{articulo}'.")
    else:
        await ctx.send(mensaje)

@client.command()
async def fijar(ctx, message_id: int):
    usuario = str(ctx.author)

    # Verifica si el usuario tiene permisos disponibles
    if usuario in impacto_usuarios and impacto_usuarios[usuario].get("permisos", 0) > 0:
        try:
            # Intenta fijar el mensaje
            mensaje = await ctx.channel.fetch_message(message_id)
            await mensaje.pin()

            # Reduce el contador de permisos
            impacto_usuarios[usuario]["permisos"] -= 1
            await ctx.author.send(f"📌 Fijaste un mensaje con éxito! Te queda(n) {impacto_usuarios[usuario]['permisos']} permiso(s).")
        except discord.Forbidden:
            await ctx.send("❌ No tengo permiso para fijar mensajes en este canal. Contacta a un moderador")
        except discord.NotFound:
            await ctx.send("❌ No se encontró el mensaje con ese ID.")
    else:
        await ctx.message.delete()
        await ctx.author.send(f"⚠️ No puedes fijar mensajes. Compra en la tienda usando `/comprar Chincheta`!")

@client.command()
@commands.cooldown(rate=1, per=60, type=commands.BucketType.user)
async def dato(ctx):
    # Diccionario con datos sobre energías y gases en el aire
    mini_articulos = [
    {
        "titulo": "Energía Solar",
        "contenido": "La energía solar es una fuente renovable que aprovecha la luz del sol para generar electricidad. Es limpia y sostenible.",
        "detalles": "Los paneles solares están hechos de células fotovoltaicas que convierten la luz solar en electricidad. Cada metro cuadrado de panel solar puede generar hasta 150 watts en condiciones óptimas.\nSin embargo, los paneles solares son poco resistentes a desastres naturales y costosos de implementar en casa.",
        "imagen" : "https://c1.wallpaperflare.com/preview/457/293/258/solar-panel-solar-panels-renewable.jpg"
    },
    {
        "titulo": "Impacto del CO₂",
        "contenido": "El dióxido de carbono (CO₂) es el principal gas de efecto invernadero que contribuye al cambio climático.",
        "detalles": "El CO₂ proviene principalmente de la quema de combustibles fósiles. Desde la Revolución Industrial, las concentraciones han aumentado de 280 ppm a más de 400 ppm hoy en día.",
        "imagen" : "https://www.meteorologiaenred.com/wp-content/uploads/2016/05/emisiones_dioxido_carbono-830x553.jpg.webp"
    },
    {
        "titulo": "Bicicletas y Medio Ambiente",
        "contenido": "Usar la bicicleta como medio de transporte ayuda a reducir las emisiones de CO₂ y mejora la salud física.",
        "detalles": "Una bicicleta emite 0 gramos de CO₂ por kilómetro recorrido, en comparación con los 271 gramos que emite un automóvil promedio.",
        "imagen" : "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiMvgT5FF2qExU4yjVSFCjGnXsFJ1Y2kDEJp58DTW5wfjpK63E4IekaDdVy81W3ghfJRyFhlz_o2nw7mLTveWhf32Lm2T0-EANFnP578lbmN9QYDQAHnDAy0pR635f_SgkP_YXuGkDM_O8/s400/jitensya_jitensyadou.png"
    },
    {
        "titulo": "Reciclar",
        "contenido": "El reciclaje, como lo conocemos hoy, comenzó a desarrollarse en el siglo XX, aunque desde mucho antes ya se practicaba. Aproximadamente en la década de 1970, el reciclaje moderno comenzó a promover la separación de residuos y el uso de productos reciclados. Las 3 R del reciclaje son: Reducir, Reutilizar y Reciclar.",
        "detalles": "**Las 3 R del reciclaje:**\n1. **Reducir**: Minimizar el consumo y los desechos generados.\n2. **Reutilizar**: Dar un nuevo uso a materiales y objetos en lugar de desecharlos.\n3. **Reciclar**: Transformar residuos en nuevos productos para evitar el desperdicio.\n\n**Los 3 tipos de basureros para reciclaje:**\n- **Amarillo:** Plásticos y metales como botellas y latas.\n- **Azul:** Papeles y cartón limpio y seco.\n- **Verde:** Vidrio, como botellas y frascos.",
        "imagen" : "https://cdn.pixabay.com/photo/2012/04/11/18/14/recycle-29231_960_720.png"
    }
]
    
    articulo = random.choice(mini_articulos)
    titulo = articulo["titulo"]
    contenido = articulo["contenido"]
    imagen = articulo["imagen"]
    embed = discord.Embed(
        title=f'**{titulo}**', 
        color=discord.Color.green()  # Puedes elegir otro color
    )

    embed.add_field(name="", value=f"{contenido}", inline=False)
    embed.set_footer(text="Di 'cuéntame más' para profundizar un poquito más!")
    embed.set_image(url=imagen)

    await ctx.send(embed=embed)
    def continuar(m):
        return m.author == ctx.author and m.content.lower() == 'cuéntame más' and m.channel == ctx.channel
    try:
        await client.wait_for('message', check=continuar, timeout=30.0)
        await ctx.send(f'{articulo['detalles']}')
    except asyncio.TimeoutError:
        return

@client.event
async def on_command_error(ctx, error):
    await ctx.message.delete()

    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Vas demasiado rápido! Espera unos segundos antes de usar más comandos",delete_after=10.0)
    else:
        pass
    
client.run(TOKEN)
