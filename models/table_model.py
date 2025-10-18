import random
import string
from models.database import get_db_connection
from models.user_model import User

class Table:
    @staticmethod
    def generate_table_id():
        """Unique table ID generate karein"""
        return 'T' + ''.join(random.choices(string.digits, k=6))
    
    @staticmethod
    def create_table(created_by, game_type, amount, options):
        """Naya table create karein"""
        conn = get_db_connection()
        try:
            table_id = Table.generate_table_id()
            
            conn.execute(
                'INSERT INTO tables (table_id, created_by, game_type, amount, options, status) VALUES (?, ?, ?, ?, ?, ?)',
                (table_id, created_by, game_type, amount, options, 'created')
            )
            conn.commit()
            
            return table_id
        except Exception as e:
            print(f"❌ Error creating table: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def accept_table(table_id, accepted_by):
        """Table accept karein"""
        conn = get_db_connection()
        try:
            # Table details get karein
            table = conn.execute(
                'SELECT * FROM tables WHERE table_id = ?', 
                (table_id,)
            ).fetchone()
            
            if not table:
                return False, "Table not found"
            
            if table['status'] != 'created':
                return False, "Table already accepted"
            
            if table['created_by'] == accepted_by:
                return False, "You cannot accept your own table"
            
            # Table update karein
            conn.execute(
                'UPDATE tables SET status = "active", accepted_by = ? WHERE table_id = ?',
                (accepted_by, table_id)
            )
            
            conn.commit()
            return True, "Table accepted successfully"
            
        except Exception as e:
            print(f"❌ Error accepting table: {e}")
            return False, str(e)
        finally:
            conn.close()
    
    @staticmethod
    def get_active_tables():
        """Active tables fetch karein"""
        conn = get_db_connection()
        try:
            tables = conn.execute(
                "SELECT * FROM tables WHERE status = 'created' ORDER BY created_at DESC"
            ).fetchall()
            return [dict(table) for table in tables]
        except Exception as e:
            print(f"❌ Error getting active tables: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_table_by_id(table_id):
        """Table ID se table fetch karein"""
        conn = get_db_connection()
        try:
            table = conn.execute(
                'SELECT * FROM tables WHERE table_id = ?', 
                (table_id,)
            ).fetchone()
            return dict(table) if table else None
        except Exception as e:
            print(f"❌ Error getting table by ID: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_all_tables():
        """Saare tables fetch karein"""
        conn = get_db_connection()
        try:
            tables = conn.execute(
                "SELECT t.*, u1.username as creator_username, u2.username as accepter_username FROM tables t LEFT JOIN users u1 ON t.created_by = u1.telegram_id LEFT JOIN users u2 ON t.accepted_by = u2.telegram_id ORDER BY t.created_at DESC"
            ).fetchall()
            return [dict(table) for table in tables]
        except Exception as e:
            print(f"❌ Error getting all tables: {e}")
            return []
        finally:
            conn.close()
