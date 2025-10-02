import sqlite3
import math

def sieve_of_eratosthenes(limit):
    """
    Generate all prime numbers up to the given limit using the Sieve of Eratosthenes algorithm.
    """
    if limit < 2:
        return []
    
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    
    for i in range(2, int(math.sqrt(limit)) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    
    primes = [i for i in range(2, limit + 1) if is_prime[i]]
    return primes

def store_primes_in_db(primes, db_name='primes.db'):
    """
    Store the list of primes in an SQLite database.
    Creates a table 'primes' with columns 'id' (auto-increment) and 'number' if it doesn't exist.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS primes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number INTEGER UNIQUE NOT NULL
        )
    ''')
    
    # Insert primes (ignore duplicates)
    for prime in primes:
        cursor.execute("INSERT OR IGNORE INTO primes (number) VALUES (?)", (prime,))
    
    conn.commit()
    conn.close()
    print(f"Stored {len(primes)} primes in {db_name}")

# Main execution
if __name__ == "__main__":
    limit = 10000  # Change this to generate primes up to a different limit
    primes = sieve_of_eratosthenes(limit)
    store_primes_in_db(primes)
    
    # Optional: Query and print the first few primes to verify
    conn = sqlite3.connect('primes.db')
    cursor = conn.cursor()
    cursor.execute("SELECT number FROM primes ORDER BY id LIMIT 10")
    first_ten = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    print("First 10 primes stored:", first_ten)