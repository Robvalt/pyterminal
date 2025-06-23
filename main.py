import os
import json
import hashlib
import subprocess
from datetime import datetime

USER_FILE = "users.json"
PACKAGES_DIR = "Packages"
INSTALLED_DIR = "InstalledPackages"

def hash_password(password):
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

def setup_directories():
    """Ensure required directories exist."""
    os.makedirs(PACKAGES_DIR, exist_ok=True)
    os.makedirs(INSTALLED_DIR, exist_ok=True)

def register():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n=== User Registration ===")
    users = load_users()
    username = input("Choose a username: ").strip()

    if username in users:
        print("Username already exists.")
        return False

    password = input("Choose a password: ")
    confirm = input("Confirm password: ")

    if password != confirm:
        print("Passwords do not match.")
        return False

    role = input("Assign role (admin/user): ").strip().lower()
    if role not in ["admin", "user"]:
        role = "user"

    users[username] = {
        "password": hash_password(password),
        "role": role,
        "last_login": None,
        "name": username  # Fixed missing comma
    }

    save_users(users)
    print("Registration successful!")
    return True

def login():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n=== CoalenPY Login ===")
    users = load_users()
    username = input("Username: ").strip()
    password = input("Password: ")

    user = users.get(username)
    if user and user["password"] == hash_password(password):
        user["last_login"] = datetime.now().isoformat()
        save_users(users)
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\nWelcome, {username}!")
        print(f"Role: {user.get('role', 'user')}")
        print(f"Last login updated to: {user['last_login']}\n")
        shell(user)
        return True
    else:
        print("\nLogin failed. Invalid credentials.\n")
        return False

def install_package(user, package):
    """Install a package from 'Packages' to 'InstalledPackages'."""
    if user["role"] != "admin":
        print("You don't have permissions to run this command.")
        return

    package_path = os.path.join(PACKAGES_DIR, package)
    installed_path = os.path.join(INSTALLED_DIR, package)

    if not os.path.exists(package_path):
        print(f"Package '{package}' not found in Packages.")
        return

    os.rename(package_path, installed_path)
    print(f"Package '{package}' installed successfully.")

def create_package(package_name):
    """Create a new package folder in the 'Packages' directory."""
    package_path = os.path.join(PACKAGES_DIR, package_name)

    if os.path.exists(package_path):
        print(f"Package '{package_name}' already exists.")
        return

    os.makedirs(package_path)
    print(f"Package '{package_name}' created successfully in '{PACKAGES_DIR}'.")

def execute_package(user, package_name):
    """Execute an installed package."""
    package_path = os.path.join(INSTALLED_DIR, package_name, "main.py")

    if not os.path.exists(package_path):
        print(f"Package '{package_name}' not found in InstalledPackages.")
        return

    print(f"Executing '{package_name}' as {user['role']}...")
    subprocess.run(["python", package_path])

def list_installed_packages():
    """List installed packages."""
    installed = os.listdir(INSTALLED_DIR)
    if installed:
        print("Installed Packages:")
        print("\n".join(installed))
    else:
        print("No packages installed.")

def uninstall_package(user, package):
    """Uninstall a package from 'InstalledPackages'."""
    if user["role"] != "admin":
        print("You don't have permissions to run this command.")
        return

    package_path = os.path.join(INSTALLED_DIR, package)

    if not os.path.exists(package_path):
        print(f"Package '{package}' is not installed.")
        return

    os.rmdir(package_path)  # Removes the package directory
    print(f"Package '{package}' has been successfully uninstalled.")

def shell(user):
    print("Type 'exit' to quit.")
    while True:
        if user["role"] == "admin":
            command = input("CoalenPY> ").strip()
        elif user["role"] == "user":
            command = input("CoalenPY/Users/" + user["name"] + "> ").strip()  # Fixed reference to user["name"]

        if command == "exit":
            print("Exiting CoalenPY...")
            break
        elif command.startswith("packager -new "):
            package_name = command[len("packager -new "):].strip()
            create_package(package_name)
        elif command.startswith("packager -run "):
            package_name = command[len("packager -run "):].strip()
            execute_package(user, package_name)
        elif command.startswith("sudo apt install "):
            package = command[len("sudo apt install "):].strip()
            install_package(user, package)
        elif command.startswith("sudo apt uninstall "):
            package = command[len("sudo apt uninstall "):].strip()
            uninstall_package(user, package)
        elif command == "apt list --installed":
            list_installed_packages()
        else:
            print(f"Unknown command: {command}")


def main_menu():
    while True:
        setup_directories()
        print("\nWelcome to CoalenPY")
        print("1. Login")
        print("2. Register")
        print("3. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            login()
        elif choice == "2":
            register()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please select 1, 2, or 3.")

if __name__ == "__main__":  # Fixed missing colon
    main_menu()
