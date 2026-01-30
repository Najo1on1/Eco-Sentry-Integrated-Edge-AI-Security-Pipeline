import random
import time
from datetime import datetime

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
LOG_FILE = "server_logs.txt"
NUM_NORMAL = 1000   # Clean data for "training"
NUM_MIXED = 200     # Mixed data for "testing" (contains attacks)

# ---------------------------------------------------------
# TEMPLATES (Apache Access Log Format)
# ---------------------------------------------------------
# Format: IP - - [Date] "METHOD URI HTTP/1.1" Status Bytes
NORMAL_URIS = [
    "/index.html", "/contact", "/about", "/products/item1", 
    "/products/item2", "/login", "/css/style.css", "/js/app.js"
]

ATTACK_URIS = [
    "/login?user=' OR '1'='1",          # SQL Injection
    "/admin/config.php",                # Admin Probing
    "/......./etc/passwd",              # Directory Traversal
    "/api/v1/user?id=<script>alert(1)"  # XSS
]

IPS = ["192.168.1.10", "10.0.0.5", "172.16.0.23", "192.168.1.55"]

def get_timestamp():
    return datetime.now().strftime("%d/%b/%Y:%H:%M:%S +0000")

def generate_log_line(is_attack=False):
    ip = random.choice(IPS) if not is_attack else "192.168.66.6" # Attacker IP
    uri = random.choice(NORMAL_URIS) if not is_attack else random.choice(ATTACK_URIS)
    status = "200" if not is_attack else "403"
    size = random.randint(200, 5000)

    return f'{ip} - - [{get_timestamp()}] "GET {uri} HTTP/1.1" {status} {size}'

# ---------------------------------------------------------
# EXECUTION
# ---------------------------------------------------------
def main():
    print(f"📝 Generating {NUM_NORMAL} normal logs for training...")
    with open("normal_train.txt", "w") as f:
        for _ in range(NUM_NORMAL):
            f.write(generate_log_line(is_attack=False) + "\n")

    print(f"📝 Generating {NUM_MIXED} mixed logs for simulation...")
    with open("live_fire_log.txt", "w") as f:
        # 95% Normal, 5% Attack
        for _ in range(NUM_MIXED):
            is_attack = random.random() > 0.95
            f.write(generate_log_line(is_attack) + "\n")

    print("✅ Data Generation Complete.")
    print("   - data/normal_train.txt (For Sentry learning)")
    print("   - data/live_fire_log.txt (For Watchtower demo)")

if __name__ == "__main__":
    main()