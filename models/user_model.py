from models.database import get_db_connection

class User:
    @staticmethod
    def find_or_create(telegram_id, username=None, first_name=None, last_name=None):
        """User ko create karein ya existing user fetch karein"""
        conn = get_db_connection()
        
        try:
            # Check if user exists
            user = conn.execute(
                'SELECT * FROM users WHERE telegram_id = ?', 
                (telegram_id,)
            ).fetchone()
            
            if user:
                # Update last active
                conn.execute(
                    'UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE telegram_id = ?',
                    (telegram_id,)
                )
                conn.commit()
                return dict(user)
            else:
                # New user create karein
                conn.execute(
                    'INSERT INTO users (telegram_id, username, first_name, last_name, balance) VALUES (?, ?, ?, ?, ?)',
                    (telegram_id, username, first_name, last_name, 1000.0)
                )
                conn.commit()
                
                # New user fetch karein
                new_user = conn.execute(
                    'SELECT * FROM users WHERE telegram_id = ?', 
                    (telegram_id,)
                ).fetchone()
                return dict(new_user)
                
        except Exception as e:
            print(f"❌ Error in find_or_create: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_user_stats(telegram_id):
        """User ka complete stats fetch karein"""
        conn = get_db_connection()
        try:
            user = conn.execute(
                'SELECT * FROM users WHERE telegram_id = ?', 
                (telegram_id,)
            ).fetchone()
            
            if user:
                return dict(user)
            return None
        except Exception as e:
            print(f"❌ Error getting user stats: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_all_users():
        """Saare users fetch karein"""
        conn = get_db_connection()
        try:
            users = conn.execute(
                'SELECT * FROM users ORDER BY created_at DESC'
            ).fetchall()
            return [dict(user) for user in users]
        except Exception as e:
            print(f"❌ Error getting all users: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def update_balance(telegram_id, amount, description="", table_id=None, admin_id=None):
        """User ka balance update karein"""
        conn = get_db_connection()
        try:
            # Balance update karein
            conn.execute(
                'UPDATE users SET balance = balance + ? WHERE telegram_id = ?',
                (amount, telegram_id)
            )
            
            # Transaction record create karein
            transaction_type = "credit" if amount > 0 else "debit"
            conn.execute(
                'INSERT INTO transactions (user_id, type, amount, description, table_id, admin_id) VALUES (?, ?, ?, ?, ?, ?)',
                (telegram_id, transaction_type, abs(amount), description, table_id, admin_id)
            )
            
            conn.commit()
            return True
        except Exception as e:
            print(f"❌ Error updating balance: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def deduct_table_amount(telegram_id, amount, table_id):
        """Table creation ke liye amount deduct karein"""
        conn = get_db_connection()
        try:
            user = conn.execute(
                'SELECT balance FROM users WHERE telegram_id = ?', 
                (telegram_id,)
            ).fetchone()
            
            if not user:
                return False, "User not found"
            
            if user['balance'] < amount:
                return False, "Insufficient balance"
            
            # Amount deduct karein
            conn.execute(
                'UPDATE users SET balance = balance - ? WHERE telegram_id = ?',
                (amount, telegram_id)
            )
            
            # Transaction record
            conn.execute(
                'INSERT INTO transactions (user_id, type, amount, description, table_id) VALUES (?, "table_creation", ?, "Table creation", ?)',
                (telegram_id, amount, table_id)
            )
            
            conn.commit()
            return True, "Amount deducted successfully"
            
        except Exception as e:
            print(f"❌ Error deducting table amount: {e}")
            return False, str(e)
        finally:
            conn.close()
