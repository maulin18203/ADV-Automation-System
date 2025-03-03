import pymysql
from flask import flash

def get_db_config():
    return {
        'MYSQL_HOST': 'localhost',
        'MYSQL_USER': 'root',
        'MYSQL_PASSWORD': '',
        'MYSQL_DB': 'iot',
        'MYSQL_CHARSET': 'utf8mb4'
    }

def get_db_connection():
    config = get_db_config()
    try:
        connection = pymysql.connect(
            host=config['MYSQL_HOST'],
            user=config['MYSQL_USER'],
            password=config['MYSQL_PASSWORD'],
            database=config['MYSQL_DB'],
            charset=config['MYSQL_CHARSET'],
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.Error as e:
        print(f"Database connection error: {str(e)}")  # Use print instead of flash
        return None


def execute_query(query, params=None, fetch=True):
    connection = get_db_connection()
    result = None
    
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                if fetch:
                    result = cursor.fetchall()
                else:
                    connection.commit()
        except pymysql.Error as e:
            flash(f"Database query error: {str(e)}", "danger")
        finally:
            connection.close()
    
    return result

def init_db():
    """Initialize database tables if they don't exist"""
    connection = get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                # Admin table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `admin` (
                        `id` int(11) NOT NULL AUTO_INCREMENT,
                        `username` varchar(50) NOT NULL,
                        `password` varchar(255) NOT NULL,
                        `role` varchar(20) NOT NULL DEFAULT 'admin',
                        `full_name` varchar(100) NOT NULL,
                        `email` varchar(100) NOT NULL,
                        `phone` varchar(15) DEFAULT NULL,
                        `alternative_number` varchar(15) DEFAULT NULL,
                        `address` varchar(255) DEFAULT NULL,
                        `gender` enum('Male','Female','Other') DEFAULT NULL,
                        `birthday` date DEFAULT NULL,
                        `created_at` timestamp NULL DEFAULT current_timestamp(),
                        PRIMARY KEY (`id`),
                        UNIQUE KEY `username` (`username`),
                        UNIQUE KEY `email` (`email`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci
                """)

                # Users table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `users` (
                        `id` int(11) NOT NULL AUTO_INCREMENT,
                        `username` varchar(255) NOT NULL,
                        `password` varchar(255) NOT NULL,
                        `full_name` varchar(255) DEFAULT 'Unknown',
                        `email` varchar(255) NOT NULL,
                        `phone` varchar(20) DEFAULT NULL,
                        `created_at` timestamp NULL DEFAULT current_timestamp(),
                        `role` enum('admin','user') NOT NULL DEFAULT 'user',
                        PRIMARY KEY (`id`),
                        UNIQUE KEY `username` (`username`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
                """)

                # Contacts table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `contacts` (
                        `id` int(11) NOT NULL AUTO_INCREMENT,
                        `username` varchar(255) NOT NULL,
                        `email` varchar(255) NOT NULL,
                        `message` text NOT NULL,
                        `timestamp` timestamp NULL DEFAULT current_timestamp(),
                        PRIMARY KEY (`id`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci
                """)

                # Login logs table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `login_logs` (
                        `id` int(11) NOT NULL AUTO_INCREMENT,
                        `username` varchar(80) NOT NULL,
                        `role` varchar(20) NOT NULL,
                        `action` varchar(255) NOT NULL,
                        `timestamp` datetime DEFAULT current_timestamp(),
                        `ip_address` varchar(45) NOT NULL,
                        PRIMARY KEY (`id`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci
                """)

                # Products table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS `products` (
                        `id` int(11) NOT NULL AUTO_INCREMENT,
                        `user_id` int(11) NOT NULL,
                        `product_name` varchar(255) DEFAULT NULL,
                        `product_serial` varchar(255) DEFAULT NULL,
                        `purchase_date` date DEFAULT NULL,
                        `product_warranty` varchar(255) DEFAULT NULL,
                        PRIMARY KEY (`id`),
                        KEY `user_id` (`user_id`),
                        CONSTRAINT `products_ibfk_1` FOREIGN KEY (`user_id`) 
                        REFERENCES `users` (`id`) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci
                """)

                connection.commit()
        finally:
            connection.close() 