import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# WooCommerce API configuration
WOO_URL = os.getenv("WOO_URL", "https://yourstore.com")
WOO_CONSUMER_KEY = os.getenv("WOO_CONSUMER_KEY")
WOO_CONSUMER_SECRET = os.getenv("WOO_CONSUMER_SECRET")

# Authentication configuration
API_KEY = os.getenv("MCP_API_KEY")
if not API_KEY:
    logger.warning("MCP_API_KEY not set - server will run without authentication (NOT RECOMMENDED FOR PRODUCTION)")

# Validate required environment variables
if not WOO_CONSUMER_KEY or not WOO_CONSUMER_SECRET:
    logger.error("WOO_CONSUMER_KEY and WOO_CONSUMER_SECRET must be set in environment variables")
    exit(1)

if WOO_URL == "https://yourstore.com":
    logger.error("WOO_URL must be configured with your actual WooCommerce store URL")
    exit(1)

logger.info(f"Initializing WooCommerce MCP Server for {WOO_URL}")
if API_KEY:
    logger.info("Authentication enabled with API key")
else:
    logger.warning("Running without authentication - use MCP_API_KEY for security")
