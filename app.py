import pymysql
import os
from dotenv import load_dotenv
import logging
import urllib.parse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('test_db.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get DATABASE_URL from environment
database_url = os.getenv('DATABASE_URL')
if not database_url:
    logger.error("DATABASE_URL not set in environment variables")
    exit(1)

# Parse DATABASE_URL
try:
    # Expected format: mysql+pymysql://username:password@host:port/dbname?params
    parsed = urllib.parse.urlparse(database_url)
    username = parsed.username
    password = urllib.parse.unquote(parsed.password)
    host = parsed.hostname
    port = parsed.port or 3306
    dbname = parsed.path.lstrip('/')
    query_params = urllib.parse.parse_qs(parsed.query)
    ssl_ca = query_params.get('ssl_ca', [None])[0]
except Exception as e:
    logger.error(f"Failed to parse DATABASE_URL: {str(e)}")
    exit(1)

# SSL configuration
ssl_config = {}
if ssl_ca:
    ssl_config['ca'] = ssl_ca

# Connect to MySQL
try:
    connection = pymysql.connect(
        host=host,
        user=username,
        password=password,
        database=dbname,
        port=port,
        charset='utf8mb4',
        ssl=ssl_config if ssl_ca else None
    )
    logger.info("Successfully connected to MySQL database")
except pymysql.MySQLError as e:
    logger.error(f"Failed to connect to MySQL: {str(e)}")
    exit(1)

# Test database operations
try:
    with connection.cursor() as cursor:
        # Create user table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                email VARCHAR(120) UNIQUE NOT NULL,
                name VARCHAR(120) NOT NULL
            )
        """)
        logger.info("User table created or already exists")

        # Create submission table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS submission (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                user_id INTEGER,
                submission_date DATE NOT NULL,
                audio_file VARCHAR(255),
                FOREIGN KEY (user_id) REFERENCES user(id)
            )
        """)
        logger.info("Submission table created or already exists")

        # Insert a test user
        cursor.execute(
            "INSERT INTO user (email, name) VALUES (%s, %s) ON DUPLICATE KEY UPDATE name=%s",
            ('test@example.com', 'Test User', 'Test User')
        )
        logger.info("Inserted test user")

        # Get user ID
        cursor.execute("SELECT id FROM user WHERE email = %s", ('test@example.com',))
        user_id = cursor.fetchone()[0]

        # Insert a test submission
        cursor.execute(
            "INSERT INTO submission (user_id, submission_date, audio_file) VALUES (%s, CURDATE(), %s)",
            (user_id, 'test_audio.wav')
        )
        logger.info("Inserted test submission")

        # Query submissions
        cursor.execute("SELECT * FROM submission WHERE user_id = %s", (user_id,))
        submissions = cursor.fetchall()
        logger.info(f"Retrieved submissions: {submissions}")

    # Commit changes
    connection.commit()
    logger.info("Database operations completed successfully")

except pymysql.MySQLError as e:
    logger.error(f"Database error: {str(e)}")
finally:
    connection.close()
    logger.info("Database connection closed")