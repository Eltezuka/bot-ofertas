import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import requests
from bs4 import BeautifulSoup
import sqlite3
import random
from config import BOT_TOKEN, AMAZON_API_KEY, ML_API_KEY

# Configuración
logging.basicConfig(level=logging.INFO)
TOKEN = BOT_TOKEN

# Base de datos
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, chat_id INTEGER, categoria TEXT, premium INTEGER)''')
    conn.commit()
    conn.close()

# Función para buscar ofertas en Mercado Libre (simulado)
def buscar_ml(producto):
    # En producción usarías la API oficial
    ofertas = [
        {"nombre": "Smart TV 50\"", "precio": "$299", "link": "https://mercadolibre.com/oferta1"},
        {"nombre": "Auriculares Bluetooth", "precio": "$25", "link": "https://mercadolibre.com/oferta2"},
    ]
    return random.choice(ofertas) if ofertas else None

# Función para buscar ofertas en Amazon (con API)
def buscar_amazon(producto):
    # Aquí conectarías con Amazon Product Advertising API
    ofertas = [
        {"nombre": "Echo Dot 5ta Gen", "precio": "$39.99", "link": "https://amazon.com/oferta1"},
        {"nombre": "Tablet Fire HD 8", "precio": "$89.99", "link": "https://amazon.com/oferta2"},
    ]
    return random.choice(ofertas) if ofertas else None

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛒 Ofertas del día", callback_data='ofertas')],
        [InlineKeyboardButton("🔔 Activar alertas", callback_data='alertas')],
        [InlineKeyboardButton("⭐ Premium (sin anuncios)", callback_data='premium')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "¡Bienvenido al Bot de Ofertas!\n\n"
        "Elige una opción:",
        reply_markup=reply_markup
    )
    # Guardar usuario en DB
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (chat_id, categoria, premium) VALUES (?, ?, ?)",
              (update.effective_chat.id, 'general', 0))
    conn.commit()
    conn.close()

# Manejar botones
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'ofertas':
        # Buscar ofertas aleatorias
        oferta_ml = buscar_ml("producto")
        oferta_amazon = buscar_amazon("producto")
        
        mensaje = "🔥 *Ofertas destacadas de hoy:*\n\n"
        if oferta_ml:
            mensaje += f"🟡 Mercado Libre:\n{oferta_ml['nombre']} - {oferta_ml['precio']}\n[Comprar]({oferta_ml['link']})\n\n"
        if oferta_amazon:
            mensaje += f"🔵 Amazon:\n{oferta_amazon['nombre']} - {oferta_amazon['precio']}\n[Comprar]({oferta_amazon['link']})\n"
        
        # Enlaces de afiliado (cambia TU_ID por tu ID)
        mensaje += "\n🤝 *Compras con nuestros enlaces nos ayudan a seguir ofreciendo ofertas*"
        
        await query.edit_message_text(mensaje, parse_mode='Markdown')

    elif query.data == 'alertas':
        await query.edit_message_text(
            "🔔 *Configura tus alertas:*\n"
            "Envía /alertar [producto] y te avisaremos cuando baje de precio.\n"
            "Ejemplo: /alertar iPhone 15"
        )

    elif query.data == 'premium':
        await query.edit_message_text(
            "⭐ *Plan Premium*\n\n"
            "Beneficios:\n"
            "✅ Sin anuncios\n"
            "✅ Alertas en tiempo real\n"
            "✅ Ofertas exclusivas\n"
            "✅ Prioridad en búsquedas\n\n"
            "Precio: *$3.99/mes*\n"
            "Paga con: [Mercado Pago](https://link.mercadopago.com/tu_link)\n\n"
            "Después de pagar, envía /confirmar_pago [código]",
            parse_mode='Markdown'
        )

# Comando /alertar
async def alertar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    producto = ' '.join(context.args)
    if not producto:
        await update.message.reply_text("Usa: /alertar [nombre del producto]")
        return
    
    await update.message.reply_text(
        f"✅ ¡Listo! Te avisaremos cuando '{producto}' baje de precio.\n"
        "(Por ahora es simulación, en producción conectaríamos con APIs reales)"
    )

# Comando /confirmar_pago (simulación)
async def confirmar_pago(update: Update, context: ContextTypes.DEFAULT_TYPE):
    codigo = ' '.join(context.args)
    if not codigo:
        await update.message.reply_text("Envía: /confirmar_pago [código de pago]")
        return
    
    # Aquí verificarías el pago con Mercado Pago API
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET premium = 1 WHERE chat_id = ?", (update.effective_chat.id,))
    conn.commit()
    conn.close()
    
    await update.message.reply_text("🎉 ¡Felicidades! Ya eres usuario Premium. Disfruta de todas las ventajas.")

# Comando /ayuda
async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Comandos disponibles:*\n"
        "/start - Menú principal\n"
        "/ofertas - Ver ofertas del día\n"
        "/alertar [producto] - Activar alerta de precio\n"
        "/premium - Info del plan premium\n"
        "/confirmar_pago [código] - Activar premium\n"
        "/ayuda - Este mensaje"
    )

# Main
def main():
    init_db()
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ofertas", start))  # Redirige al menú
    app.add_handler(CommandHandler("alertar", alertar))
    app.add_handler(CommandHandler("premium", start))
    app.add_handler(CommandHandler("confirmar_pago", confirmar_pago))
    app.add_handler(CommandHandler("ayuda", ayuda))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("🤖 Bot iniciado...")
    app.run_polling()

if _name_ == "_main_":
    main()