from flask import Flask, request, jsonify, redirect
from models.database import init_database, get_db_connection
from models.user_model import User
from models.table_model import Table
import json
import requests

app = Flask(__name__)
app.secret_key = 'ludo-tournament-secret-key-2024'

# Configuration
BOT_TOKEN = "8265367568:AAF39Ckal4XiGbF_vIHlG_WgTSiJT5jOD70"
ADMIN_IDS = ["7002989319"]
GROUP_ID = "-1003126963687"  # Negative sign added for group

def send_telegram_message(chat_id, text, reply_markup=None):
    """Telegram message send karne ka function - FIXED VERSION"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"📤 Telegram API Response: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ Message sent successfully to group!")
                return result
            else:
                print(f"❌ Telegram API Error: {result}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
        return None
    except Exception as e:
        print(f"❌ Telegram message error: {e}")
        return None

@app.route('/')
def index():
    return "🎮 Ludo Tournament Server is Running! Use /mini-app for table creation."

@app.route('/mini-app')
def mini_app():
    """Telegram Mini Web App - Create Table Form"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Create Ludo Table</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                max-width: 400px;
                margin: 0 auto;
                background: white;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            .header {
                background: linear-gradient(135deg, #4CAF50, #45a049);
                color: white;
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 25px;
                text-align: center;
            }
            .form-group {
                margin: 20px 0;
            }
            label {
                display: block;
                margin-bottom: 8px;
                font-weight: bold;
                color: #333;
            }
            select, input {
                width: 100%;
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 16px;
            }
            .amount-buttons {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 10px;
                margin: 15px 0;
            }
            .amount-btn {
                padding: 12px;
                border: 2px solid #4CAF50;
                background: white;
                color: #4CAF50;
                border-radius: 8px;
                cursor: pointer;
                text-align: center;
                font-weight: bold;
            }
            .amount-btn.active {
                background: #4CAF50;
                color: white;
            }
            .option-group label {
                display: flex;
                align-items: center;
                font-weight: normal;
                margin: 10px 0;
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                cursor: pointer;
            }
            .submit-btn {
                background: linear-gradient(135deg, #4CAF50, #45a049);
                color: white;
                padding: 16px;
                border: none;
                border-radius: 8px;
                width: 100%;
                font-size: 18px;
                font-weight: bold;
                cursor: pointer;
                margin-top: 25px;
            }
            .submit-btn:disabled {
                background: #cccccc;
                cursor: not-allowed;
            }
            .balance-display {
                font-size: 18px;
                font-weight: bold;
                text-align: center;
                margin: 10px 0;
                color: #fff;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>🎮 Create Ludo Table</h2>
                <div class="balance-display">
                    Balance: ₹<span id="balance">0</span>
                </div>
            </div>

            <form id="tableForm">
                <div class="form-group">
                    <label for="gameType">🎯 Game Type:</label>
                    <select id="gameType" required>
                        <option value="">Select Game Type</option>
                        <option value="full">Full Game</option>
                        <option value="1goti">1 Goti</option>
                        <option value="2goti">2 Goti</option>
                        <option value="1goti_quick">1 Goti Quick</option>
                        <option value="snake_ladder">Snake & Ladder</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="amount">💰 Amount:</label>
                    <input type="number" id="amount" placeholder="Enter amount" required min="100">
                    <div class="amount-buttons">
                        <button type="button" class="amount-btn" onclick="setAmount(100)">100</button>
                        <button type="button" class="amount-btn" onclick="setAmount(200)">200</button>
                        <button type="button" class="amount-btn" onclick="setAmount(300)">300</button>
                        <button type="button" class="amount-btn" onclick="setAmount(500)">500</button>
                        <button type="button" class="amount-btn" onclick="setAmount(1000)">1000</button>
                        <button type="button" class="amount-btn" onclick="setAmount(2000)">2000</button>
                    </div>
                </div>

                <div class="form-group">
                    <label>⚡ Options:</label>
                    <div class="option-group">
                        <label>
                            <input type="radio" name="option" value="code_aap_doge" required>
                            🔐 Code aap doge
                        </label>
                    </div>
                    <div class="option-group">
                        <label>
                            <input type="radio" name="option" value="code_main_dunga">
                            🔑 Code main dunga
                        </label>
                    </div>
                    <div class="option-group">
                        <label>
                            <input type="radio" name="option" value="no_iphone">
                            📱 No iPhone
                        </label>
                    </div>
                </div>

                <button type="submit" class="submit-btn" id="submitBtn">
                    🎯 Create Table
                </button>
            </form>
        </div>

        <script>
            let tg = window.Telegram.WebApp;
            tg.expand();
            
            // User data fetch karein
            const user = tg.initDataUnsafe.user;
            
            if (user) {
                // Balance ke liye API call karein
                fetch('/api/user/' + user.id)
                    .then(response => response.json())
                    .then(userData => {
                        document.getElementById('balance').textContent = userData.balance || 0;
                    });
            }

            function setAmount(amount) {
                document.getElementById('amount').value = amount;
                document.querySelectorAll('.amount-btn').forEach(btn => {
                    btn.classList.remove('active');
                });
                event.target.classList.add('active');
                validateForm();
            }

            function validateForm() {
                const amount = parseFloat(document.getElementById('amount').value) || 0;
                const gameType = document.getElementById('gameType').value;
                const option = document.querySelector('input[name="option"]:checked');
                const balance = parseFloat(document.getElementById('balance').textContent) || 0;
                
                const submitBtn = document.getElementById('submitBtn');
                submitBtn.disabled = !(amount > 0 && gameType && option && amount <= balance);
            }

            document.getElementById('gameType').addEventListener('change', validateForm);
            document.getElementById('amount').addEventListener('input', validateForm);
            document.querySelectorAll('input[name="option"]').forEach(radio => {
                radio.addEventListener('change', validateForm);
            });

            document.getElementById('tableForm').addEventListener('submit', function(e) {
                e.preventDefault();
                
                const user = tg.initDataUnsafe.user;
                if (!user) {
                    alert('User not found!');
                    return;
                }

                const formData = {
                    userId: user.id,
                    gameType: document.getElementById('gameType').value,
                    amount: document.getElementById('amount').value,
                    option: document.querySelector('input[name="option"]:checked').value
                };

                const submitBtn = document.getElementById('submitBtn');
                submitBtn.disabled = true;
                submitBtn.textContent = 'Creating Table...';

                fetch('/api/create-table', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        submitBtn.textContent = '✅ Table Created!';
                        setTimeout(() => tg.close(), 2000);
                    } else {
                        alert('Error: ' + data.message);
                        submitBtn.disabled = false;
                        submitBtn.textContent = '🎯 Create Table';
                    }
                })
                .catch(error => {
                    alert('Error creating table!');
                    submitBtn.disabled = false;
                    submitBtn.textContent = '🎯 Create Table';
                });
            });

            validateForm();
        </script>
    </body>
    </html>
    '''

@app.route('/api/user/<user_id>')
def api_get_user(user_id):
    """User data API"""
    user = User.get_user_stats(user_id)
    if user:
        return jsonify(user)
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/api/create-table', methods=['POST'])
def api_create_table():
    """Table creation API"""
    try:
        data = request.json
        user_id = data.get('userId')
        game_type = data.get('gameType')
        amount = float(data.get('amount'))
        option = data.get('option')
        
        user = User.get_user_stats(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'})
        
        if user['balance'] < amount:
            return jsonify({'success': False, 'message': f'Insufficient balance. Your balance: ₹{user["balance"]}'})
        
        # Table create karein
        table_id = Table.create_table(user_id, game_type, amount, option)
        if table_id:
            # Amount deduct karein
            success, message = User.deduct_table_amount(user_id, amount, table_id)
            if success:
                # Group mein message bhejein
                creator = User.get_user_stats(user_id)
                message_text = f"""
🎮 <b>NEW TABLE CREATED!</b>

👤 <b>Created By:</b> @{creator['username'] or creator['first_name']}
💰 <b>Amount:</b> ₹{amount}
🎯 <b>Game Type:</b> {game_type.replace('_', ' ').title()}
⚡ <b>Options:</b> {option.replace('_', ' ').title()}
🆔 <b>Table ID:</b> <code>{table_id}</code>

Click below to accept the challenge! ⬇️
                """
                
                keyboard = {
                    'inline_keyboard': [[
                        {'text': '✅ Accept Table', 'callback_data': f'accept_{table_id}'}
                    ]]
                }
                
                send_telegram_message(GROUP_ID, message_text, keyboard)
                
                return jsonify({'success': True, 'table_id': table_id, 'message': 'Table created successfully'})
            else:
                return jsonify({'success': False, 'message': message})
        else:
            return jsonify({'success': False, 'message': 'Error creating table'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})

@app.route('/admin/credit', methods=['POST'])
def admin_credit():
    """User ko credit karein"""
    try:
        user_id = request.form.get('user_id')
        amount = float(request.form.get('amount'))
        description = request.form.get('description', 'Admin Credit')
        
        user = User.get_user_stats(user_id)
        if not user:
            return redirect('/admin/dashboard?error=User not found')
        
        # Balance update karein
        success = User.update_balance(user_id, amount, description)
        
        if success:
            return redirect('/admin/dashboard?message=Credit successful')
        else:
            return redirect('/admin/dashboard?error=Credit failed')
            
    except Exception as e:
        return redirect(f'/admin/dashboard?error={str(e)}')

@app.route('/admin/debit', methods=['POST'])
def admin_debit():
    """User ko debit karein"""
    try:
        user_id = request.form.get('user_id')
        amount = float(request.form.get('amount'))
        description = request.form.get('description', 'Admin Debit')
        
        user = User.get_user_stats(user_id)
        if not user:
            return redirect('/admin/dashboard?error=User not found')
        
        if user['balance'] < amount:
            return redirect('/admin/dashboard?error=Insufficient balance')
        
        # Balance update karein (negative amount for debit)
        success = User.update_balance(user_id, -amount, description)
        
        if success:
            return redirect('/admin/dashboard?message=Debit successful')
        else:
            return redirect('/admin/dashboard?error=Debit failed')
            
    except Exception as e:
        return redirect(f'/admin/dashboard?error={str(e)}')

@app.route('/admin/declare_winner', methods=['POST'])
def admin_declare_winner():
    """Winner declare karein"""
    try:
        table_id = request.form.get('table_id')
        winner_id = request.form.get('winner_id')
        
        conn = get_db_connection()
        
        # Table details get karein
        table = conn.execute(
            'SELECT * FROM tables WHERE table_id = ?', 
            (table_id,)
        ).fetchone()
        
        if not table:
            return redirect('/admin/dashboard?error=Table not found')
        
        if table['status'] != 'active':
            return redirect('/admin/dashboard?error=Table is not active')
        
        # Winner aur loser determine karein
        if winner_id == table['created_by']:
            loser_id = table['accepted_by']
        else:
            loser_id = table['created_by']
        
        # Commission calculate karein (5%)
        total_amount = table['amount'] * 2
        commission = total_amount * 0.05
        winner_amount = total_amount - commission
        
        # Winner ko amount transfer karein
        User.update_balance(winner_id, winner_amount, f"Won battle {table_id}")
        
        # Commission admin ko (system balance)
        # Yahan aap commission ko kisi admin account mein store kar sakte hain
        
        # Wins/Losses update karein
        conn.execute(
            'UPDATE users SET total_wins = total_wins + 1 WHERE telegram_id = ?',
            (winner_id,)
        )
        conn.execute(
            'UPDATE users SET total_losses = total_losses + 1 WHERE telegram_id = ?',
            (loser_id,)
        )
        
        # Table status update karein
        conn.execute(
            'UPDATE tables SET status = "completed", winner = ? WHERE table_id = ?',
            (winner_id, table_id)
        )
        
        conn.commit()
        conn.close()
        
        # Winner aur loser ko notification bhejein
        winner = User.get_user_stats(winner_id)
        loser = User.get_user_stats(loser_id)
        
        # Group mein result announce karein
        result_message = f"""
🏆 <b>BATTLE RESULT!</b> 🏆

🆔 <b>Table ID:</b> <code>{table_id}</code>
🎮 <b>Game:</b> {table['game_type'].replace('_', ' ').title()}
💰 <b>Amount:</b> ₹{table['amount']} each

🥇 <b>WINNER:</b> {winner['first_name']} (@{winner['username'] or 'N/A'})
💔 <b>LOSER:</b> {loser['first_name']} (@{loser['username'] or 'N/A'})
🏅 <b>Prize:</b> ₹{winner_amount}

Congratulations to the winner! 🎉
        """
        
        send_telegram_message(GROUP_ID, result_message)
        
        return redirect('/admin/dashboard?message=Winner declared successfully')
        
    except Exception as e:
        return redirect(f'/admin/dashboard?error={str(e)}')

@app.route('/admin')
def admin():
    """Admin dashboard"""
    return redirect('/admin/dashboard')

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard - UPDATED VERSION"""
    conn = get_db_connection()
    
    try:
        # Statistics fetch karein
        total_users = conn.execute('SELECT COUNT(*) as count FROM users').fetchone()[0]
        total_tables = conn.execute('SELECT COUNT(*) as count FROM tables').fetchone()[0]
        active_tables = conn.execute("SELECT COUNT(*) as count FROM tables WHERE status = 'active'").fetchone()[0]
        
        total_balance_result = conn.execute('SELECT SUM(balance) as total FROM users').fetchone()[0]
        total_balance = total_balance_result if total_balance_result else 0
        
        # Recent users
        recent_users = conn.execute(
            'SELECT * FROM users ORDER BY created_at DESC LIMIT 10'
        ).fetchall()
        
        # Active battles
        active_battles = conn.execute('''
            SELECT t.*, u1.username as creator_name, u2.username as accepter_name 
            FROM tables t 
            LEFT JOIN users u1 ON t.created_by = u1.telegram_id 
            LEFT JOIN users u2 ON t.accepted_by = u2.telegram_id 
            WHERE t.status = "active"
        ''').fetchall()
        
        # Get message/error from query parameters
        message = request.args.get('message')
        error = request.args.get('error')
        
        return f"""
        <html>
        <head>
            <title>Ludo Tournament Admin</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .dashboard {{ max-width: 1400px; margin: 0 auto; }}
                .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 30px 0; }}
                .stat-card {{ background: white; padding: 25px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .stat-number {{ font-size: 2.5em; font-weight: bold; color: #007bff; margin: 10px 0; }}
                .users-table, .battles-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .users-table th, .users-table td, .battles-table th, .battles-table td {{ padding: 15px; text-align: left; border-bottom: 1px solid #ddd; }}
                .users-table th, .battles-table th {{ background: #007bff; color: white; }}
                .section {{ background: white; padding: 25px; border-radius: 10px; margin: 25px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                button {{ padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; background: #28a745; color: white; }}
                .winner-btn {{ background: #ffc107; color: black; }}
                .danger-btn {{ background: #dc3545; }}
                .form-group {{ margin: 15px 0; }}
                .form-group label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
                .form-group input, .form-group select {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
                .alert {{ padding: 15px; margin: 15px 0; border-radius: 5px; }}
                .alert-success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
                .alert-danger {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
                .action-buttons {{ display: flex; gap: 10px; }}
            </style>
        </head>
        <body>
            <div class="dashboard">
                <h1>🎮 Ludo Tournament Admin Dashboard</h1>
                
                {"<div class='alert alert-success'>" + message + "</div>" if message else ""}
                {"<div class='alert alert-danger'>" + error + "</div>" if error else ""}
                
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-number">{total_users}</div>
                        <div>Total Users</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{total_tables}</div>
                        <div>Total Tables</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{active_tables}</div>
                        <div>Active Tables</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">₹{total_balance}</div>
                        <div>Total Balance</div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>💰 Credit/Debit User</h2>
                    <form action="/admin/credit" method="post" style="display: inline-block; width: 48%; margin-right: 2%; vertical-align: top;">
                        <h3>💹 Credit User</h3>
                        <div class="form-group">
                            <label for="credit_user_id">User ID:</label>
                            <input type="text" id="credit_user_id" name="user_id" required>
                        </div>
                        <div class="form-group">
                            <label for="credit_amount">Amount:</label>
                            <input type="number" id="credit_amount" name="amount" required min="1">
                        </div>
                        <div class="form-group">
                            <label for="credit_description">Description:</label>
                            <input type="text" id="credit_description" name="description" value="Admin Credit">
                        </div>
                        <button type="submit">💳 Credit User</button>
                    </form>
                    
                    <form action="/admin/debit" method="post" style="display: inline-block; width: 48%; vertical-align: top;">
                        <h3>💸 Debit User</h3>
                        <div class="form-group">
                            <label for="debit_user_id">User ID:</label>
                            <input type="text" id="debit_user_id" name="user_id" required>
                        </div>
                        <div class="form-group">
                            <label for="debit_amount">Amount:</label>
                            <input type="number" id="debit_amount" name="amount" required min="1">
                        </div>
                        <div class="form-group">
                            <label for="debit_description">Description:</label>
                            <input type="text" id="debit_description" name="description" value="Admin Debit">
                        </div>
                        <button type="submit" class="danger-btn">💸 Debit User</button>
                    </form>
                </div>
                
                <div class="section">
                    <h2>⚔️ Active Battles</h2>
                    {"<table class='battles-table'><tr><th>Table ID</th><th>Player 1</th><th>Player 2</th><th>Amount</th><th>Game Type</th><th>Actions</th></tr>" + 
                    "".join([f"""
                    <tr>
                        <td>{battle['table_id']}</td>
                        <td>@{battle['creator_name'] or battle['created_by']}</td>
                        <td>@{battle['accepter_name'] or battle['accepted_by']}</td>
                        <td>₹{battle['amount']}</td>
                        <td>{battle['game_type']}</td>
                        <td>
                            <form action="/admin/declare_winner" method="post" style="display: inline;">
                                <input type="hidden" name="table_id" value="{battle['table_id']}">
                                <input type="hidden" name="winner_id" value="{battle['created_by']}">
                                <button type="submit" class="winner-btn">🎯 Player 1 Winner</button>
                            </form>
                            <form action="/admin/declare_winner" method="post" style="display: inline;">
                                <input type="hidden" name="table_id" value="{battle['table_id']}">
                                <input type="hidden" name="winner_id" value="{battle['accepted_by']}">
                                <button type="submit" class="winner-btn">🎯 Player 2 Winner</button>
                            </form>
                        </td>
                    </tr>
                    """ for battle in active_battles]) + "</table>" if active_battles else "<p>No active battles</p>"}
                </div>
                
                <div class="section">
                    <h2>👥 Recent Users</h2>
                    <table class="users-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Username</th>
                                <th>Name</th>
                                <th>Balance</th>
                                <th>Wins/Losses</th>
                                <th>Joined</th>
                            </tr>
                        </thead>
                        <tbody>
                            {"".join([f"""
                            <tr>
                                <td>{user['telegram_id']}</td>
                                <td>@{user['username'] or 'N/A'}</td>
                                <td>{user['first_name']}</td>
                                <td>₹{user['balance']}</td>
                                <td>{user['total_wins']}/{user['total_losses']}</td>
                                <td>{user['created_at'][:16]}</td>
                            </tr>
                            """ for user in recent_users])}
                        </tbody>
                    </table>
                </div>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"Error: {e}"
    finally:
        conn.close()

if __name__ == '__main__':
    # Database initialize karein
    init_database()
    
    # Flask app run karein with PORT 5000
    print("🌐 Starting Server on http://localhost:5000")
    print("📱 Mini App: http://localhost:5000/mini-app")
    print("🔧 Admin Panel: http://localhost:5000/admin")
    app.run(host='0.0.0.0', port=5000, debug=True)
