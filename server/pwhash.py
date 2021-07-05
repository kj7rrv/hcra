import argon2
import getpass

password = getpass.getpass('Password: ')

print(f'password_argon2 {argon2.hash_password(password.encode("utf-8")).decode("utf-8")}')
