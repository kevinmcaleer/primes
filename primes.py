import sqlite3
import math
import time
import numpy as np

PRIMES_TO_PRINT = 100_000  # Print every 1000th prime found

def sieve_of_eratosthenes(limit, print_primes=False, start_time=None, print_interval=1000):
    """
    Generate all prime numbers up to the given limit using the Sieve of Eratosthenes algorithm with NumPy.
    """
    if limit < 2:
        return []

    # Use NumPy boolean array for better performance
    is_prime = np.ones(limit + 1, dtype=bool)
    is_prime[0] = is_prime[1] = False

    prime_count = 0
    sqrt_limit = int(math.sqrt(limit))

    for i in range(2, limit + 1):
        if is_prime[i]:
            prime_count += 1

            if print_primes and start_time is not None and prime_count % print_interval == 0:
                elapsed = time.time() - start_time
                print(f"Prime {prime_count}: {i} (found at {elapsed:.4f}s)")

            # Mark multiples as composite using NumPy slicing (much faster)
            if i <= sqrt_limit:
                is_prime[i*i::i] = False

    # Extract all primes at once using NumPy's where function
    primes = np.where(is_prime)[0].tolist()

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
    limit = 1_000_000_000  # Change this to generate primes up to a different limit

    # Check the last prime in the database to resume from there
    conn = sqlite3.connect('primes.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS primes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number INTEGER UNIQUE NOT NULL
        )
    ''')
    cursor.execute("SELECT MAX(number) FROM primes")
    result = cursor.fetchone()
    last_prime = result[0] if result[0] is not None else 0
    conn.close()

    if last_prime > 0:
        print(f"Resuming from last prime: {last_prime}")
        # Start from the next number after the last prime
        start_limit = last_prime + 1
    else:
        print("Starting fresh")
        start_limit = 2

    # Only run if we haven't reached the limit yet
    if start_limit < limit:
        start_time = time.time()
        primes = sieve_of_eratosthenes(limit, print_primes=True, start_time=start_time, print_interval=PRIMES_TO_PRINT)
        end_time = time.time()

        elapsed_time = end_time - start_time
        print(f"\nFound {len(primes)} primes in {elapsed_time:.2f} seconds")

        # Filter out primes we already have
        new_primes = [p for p in primes if p > last_prime]
        print(f"Storing {len(new_primes)} new primes")
        store_primes_in_db(new_primes)
    else:
        print(f"Already computed all primes up to {limit}")
    
    # Optional: Query and print the first few primes to verify
    conn = sqlite3.connect('primes.db')
    cursor = conn.cursor()
    cursor.execute("SELECT number FROM primes ORDER BY id ")
    first_ten = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    print("First 10 primes stored:", first_ten)