import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.user_model import User
from models.table_model import Table

# Bot configuration
BOT_TOKEN = "8265367568:AAF39Ckal4XiGbF_vIHlG_WgTSiJT5jOD70"
ADMIN_IDS = ["7002989319"]
GROUP_ID = "-1003126963687"  # Negative sign added for group
BASE_URL = "https://7375253057ab77.lhr.life"

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class LudoBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """All bot handlers setup karein"""
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("balance", self.balance_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("newtable", self.newtable_command))
        self.application.add_handler(CommandHandler("tables", self.tables_command))
        self.application.add_handler(CommandHandler("admin", self.admin_command))
        
        # Callback query handlers
        self.application.add_handler(CallbackQueryHandler(self.button_click, pattern='.*'))
        
        # Message handlers
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, self.handle_message
        ))
        
        # Group members join/leave handlers
        self.application.add_handler(MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS, self.handle_new_members
        ))
        
        print("✅ Bot handlers setup completed!")
    
    async def start_command(self, update: Update, context: CallbackContext):
        """Start command handler"""
        user = update.effective_user
        
        # User create/update karein
        db_user = User.find_or_create(
            telegram_id=str(user.id),
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        if db_user:
            welcome_msg = f"""
🎮 *Welcome {user.first_name} to Ludo Tournament Bot!*

💰 *Your Balance:* ₹{db_user['balance']}
🏆 *Total Wins:* {db_user['total_wins']}
📊 *Total Games:* {db_user['total_wins'] + db_user['total_losses']}

*Click below to create table:*
            """
            
            # Mini web app button
            keyboard = [
                [InlineKeyboardButton("📍 Place New Table", web_app={"url": f"{BASE_URL}/mini-app"})]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(welcome_msg, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def send_group_welcome(self):
        """Group mein welcome message"""
        try:
            message = """
🎮 *LUDO TOURNAMENT BOT* 🎮

*Create New Table & Challenge Friends!*

👇 *Click below to create table:*
            """
            
            keyboard = [
                [InlineKeyboardButton("📍 Place New Table", web_app={"url": f"{BASE_URL}/mini-app"})]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await self.application.bot.send_message(
                chat_id=GROUP_ID,
                text=message,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
            print("✅ Group welcome message sent!")
        except Exception as e:
            print(f"❌ Error sending group message: {e}")
    
    async def newtable_command(self, update: Update, context: CallbackContext):
        """Create new table command"""
        keyboard = [
            [InlineKeyboardButton("📍 Place New Table", web_app={"url": f"{BASE_URL}/mini-app"})]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎮 *Create New Table*\n\nClick below to open table creation form:",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def tables_command(self, update: Update, context: CallbackContext):
        """Show active tables"""
        tables = Table.get_active_tables()
            
        if not tables:
            await update.message.reply_text("📭 No active tables available. Create one with /newtable")
            return
        
        for table in tables:
            creator = User.get_user_stats(table['created_by'])
            creator_name = f"@{creator['username']}" if creator and creator['username'] else creator['first_name']
            
            table_msg = f"""
🎯 *Table Available!*

🆔 *Table ID:* `{table['table_id']}`
👤 *Creator:* {creator_name}
🎮 *Game:* {table['game_type'].replace('_', ' ').title()}
💰 *Amount:* ₹{table['amount']}
⚡ *Options:* {table['options'].replace('_', ' ').title()}
            """
            
            keyboard = [[InlineKeyboardButton("✅ Accept Table", callback_data=f"accept_{table['table_id']}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(table_msg, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    async def button_click(self, update: Update, context: CallbackContext):
        """Button click handler"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user = query.from_user
        
        if data.startswith("accept_"):
            table_id = data.replace("accept_", "")
            await self.accept_table(query, table_id)
    
    async def accept_table(self, query, table_id):
        """Table accept karein"""
        user = query.from_user
        
        db_user = User.get_user_stats(str(user.id))
        if not db_user:
            await query.answer("❌ Please use /start first!", show_alert=True)
            return
        
        table = Table.get_table_by_id(table_id)
        if not table:
            await query.answer("❌ Table not found!", show_alert=True)
            return
        
        if table['status'] != 'created':
            await query.answer("❌ Table already accepted!", show_alert=True)
            return
        
        if table['created_by'] == str(user.id):
            await query.answer("❌ You cannot accept your own table!", show_alert=True)
            return
        
        # Check balance
        if db_user['balance'] < table['amount']:
            await query.answer("❌ Insufficient balance!", show_alert=True)
            return
        
        # Table accept karein
        success, message = Table.accept_table(table_id, str(user.id))
        
        if success:
            # Group mein battle message bhejein
            creator = User.get_user_stats(table['created_by'])
            acceptor = db_user
            
            battle_message = f"""
⚔️ *BATTLE STARTED!* ⚔️

🆔 *Table ID:* `{table_id}`
👥 *Players:* 
   🛡️ {creator['first_name']} (@{creator['username'] or 'N/A'})
   ⚔️ {acceptor['first_name']} (@{acceptor['username'] or 'N/A'})
💰 *Stakes:* ₹{table['amount']} each
🎯 *Game:* {table['game_type'].replace('_', ' ').title()}
⚡ *Options:* {table['options'].replace('_', ' ').title()}

⏳ *Game in progress...*
            """
            
            await self.application.bot.send_message(
                chat_id=GROUP_ID,
                text=battle_message,
                parse_mode=ParseMode.MARKDOWN
            )
            
            await query.answer("✅ Table accepted successfully!", show_alert=True)
            await query.message.delete()
        else:
            await query.answer(f"❌ {message}", show_alert=True)
    
    async def balance_command(self, update: Update, context: CallbackContext):
        """Balance check"""
        user = update.effective_user
        db_user = User.get_user_stats(str(user.id))
        
        if db_user:
            await update.message.reply_text(
                f"💰 *Balance:* ₹{db_user['balance']}\n"
                f"👤 *User:* {db_user['first_name']}",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def stats_command(self, update: Update, context: CallbackContext):
        """Stats command"""
        user = update.effective_user
        db_user = User.get_user_stats(str(user.id))
        
        if db_user:
            total_games = db_user['total_wins'] + db_user['total_losses']
            win_rate = (db_user['total_wins'] / total_games * 100) if total_games > 0 else 0
            
            stats_msg = f"""
📊 *Your Stats:*

💰 *Balance:* ₹{db_user['balance']}
🏆 *Wins:* {db_user['total_wins']}
💔 *Losses:* {db_user['total_losses']}
📈 *Win Rate:* {win_rate:.1f}%
            """
            await update.message.reply_text(stats_msg, parse_mode=ParseMode.MARKDOWN)
    
    async def admin_command(self, update: Update, context: CallbackContext):
        """Admin command"""
        user = update.effective_user
        
        if str(user.id) not in ADMIN_IDS:
            await update.message.reply_text("❌ Access denied.")
            return
        
        await update.message.reply_text(
            f"🔧 *Admin Panel*\n\n"
            f"🌐 *Admin URL:* {BASE_URL}/admin\n"
            f"📊 *Live Dashboard*",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_message(self, update: Update, context: CallbackContext):
        """Auto user creation"""
        user = update.effective_user
        User.find_or_create(
            telegram_id=str(user.id),
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
    
    async def handle_new_members(self, update: Update, context: CallbackContext):
        """New member welcome"""
        for member in update.message.new_chat_members:
            if member.is_bot:
                continue
                
            db_user = User.find_or_create(
                telegram_id=str(member.id),
                username=member.username,
                first_name=member.first_name,
                last_name=member.last_name
            )
            
            if db_user:
                welcome_msg = f"""
👋 Welcome {member.first_name}!

💰 Starting balance: ₹{db_user['balance']}

Click below to create your first table! ⬇️
                """
                
                keyboard = [
                    [InlineKeyboardButton("📍 Place New Table", web_app={"url": f"{BASE_URL}/mini-app"})]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(welcome_msg, reply_markup=reply_markup)
    
    def run(self):
        """Bot run karein"""
        print("🤖 Starting Telegram Bot...")
        print(f"✅ Bot Token: {BOT_TOKEN[:10]}...")
        print(f"✅ Group ID: {GROUP_ID}")
        print(f"✅ Web URL: {BASE_URL}")
        
        # Group welcome message
        import asyncio
        asyncio.get_event_loop().run_until_complete(self.send_group_welcome())
        
        self.application.run_polling()

if __name__ == '__main__':
    bot = LudoBot()
    bot.run()
