import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests
from dateutil import parser


import os

# Leer el token del entorno
TOKEN = os.getenv("TELEGRAM_TOKEN")


# Función para convertir la fecha en formato ISO 8601 a un formato legible
def format_date(iso_date_str):
    try:
        date_obj = parser.isoparse(iso_date_str)
        return date_obj.strftime("%d-%m-%Y %H:%M:%S")
    except (ValueError, TypeError):
        return "N/A"

# Función para calcular el porcentaje de progreso de corazones
def calculate_progress(current, total):
    if total > 0:
        return round((current / total) * 100, 2)
    return 0

# Función que maneja el comando /titanesinfo
async def titanesinfo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = "https://dcoh.watch/api/v1/overwatch/titans"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        maelstroms = data.get("maelstroms", [])

        if isinstance(maelstroms, list):
            message = ""

            # Maelstrom completamente vulnerable
            maelstrom_vulnerable = next(
                (maelstrom for maelstrom in maelstroms if maelstrom.get("damageResistance", {}).get("name") == "Completely vulnerable"), 
                None
            )

            if maelstrom_vulnerable:
                name = maelstrom_vulnerable.get("name", "N/A")
                system_name = maelstrom_vulnerable.get("systemName", "N/A")
                hearts_remaining = maelstrom_vulnerable.get("heartsRemaining", 0)
                total_hearts = maelstrom_vulnerable.get("totalHearts", 0)
                current_heart_progress = maelstrom_vulnerable.get("heartProgress", 0)
                tiempo_estimado = format_date(maelstrom_vulnerable.get("completionTimeEstimate", "N/A"))
                progress_percentage = current_heart_progress*100

                message += "\n\n🟢 Maelstrom Completamente Vulnerable \n"
                message += f"Nombre: {name}\n"
                message += f"Sistema: {system_name}\n"
                message += f"Corazones Restantes: {hearts_remaining}\n"
                message += f"Progreso de Corazones: {progress_percentage}%\n"
                message += f"Fecha de Destrucción Estimada: {tiempo_estimado}\n"
                message += "-"*50 + "\n"
            else:
                message += "\n\nNo hay maelstroms completamente vulnerables.\n"

            # Maelstroms activos
            activos = [maelstrom for maelstrom in maelstroms if maelstrom.get("state") == "Active" and maelstrom != maelstrom_vulnerable]

            if activos:
                message += "\n\n🟠 Maelstroms Activos \n"
                for maelstrom in activos:
                    name = maelstrom.get("name", "N/A")
                    system_name = maelstrom.get("systemName", "N/A")
                    hearts_remaining = maelstrom.get("heartsRemaining", "0")
                    
                    message += f"Nombre: {name}\n"
                    message += f"Sistema: {system_name}\n"
                    message += f"Corazones Restantes: {hearts_remaining}\n"
                    message += "-"*50 + "\n"
            else:
                message += "\n\nNo hay maelstroms activos.\n"

            # Maelstroms destruidos
            destruidos = [maelstrom for maelstrom in maelstroms if maelstrom.get("state") == "Destroyed"]

            if destruidos:
                message += "\n\n💀 Maelstroms Destruidos 💀\n"
                for maelstrom in destruidos:
                    name = maelstrom.get("name", "N/A")
                    system_name = maelstrom.get("systemName", "N/A")
                    hearts_remaining = maelstrom.get("heartsRemaining", 0)
                    tiempo_destruccion = format_date(maelstrom.get("meltdownTimeEstimate", "N/A"))
                    
                    message += f"Nombre: {name}\n"
                    message += f"Sistema: {system_name}\n"
                    message += f"Corazones Restantes: {hearts_remaining}\n"
                    message += f"Fecha de Destrucción: {tiempo_destruccion}\n"
                    message += "-"*50 + "\n"
            else:
                message += "\n\nNo hay maelstroms destruidos.\n"

            await update.message.reply_text(message)
        else:
            await update.message.reply_text("La clave 'maelstroms' no contiene una lista.")
    
    except requests.exceptions.HTTPError as http_err:
        await update.message.reply_text(f"Error HTTP: {http_err}")
    except requests.exceptions.RequestException as req_err:
        await update.message.reply_text(f"Error de solicitud: {req_err}")
    except Exception as err:
        await update.message.reply_text(f"Error inesperado: {err}")

# Función principal para iniciar el bot
def main():
    application = Application.builder().token(TOKEN).build()

    # Añadir el manejador de comandos
    application.add_handler(CommandHandler("titanesinfo", titanesinfo))

    # Iniciar el bot
    application.run_polling()

if __name__ == '__main__':
    main()
