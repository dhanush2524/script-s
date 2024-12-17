import subprocess
import sys
import platform

MIN_PYTHON_VERSION = (3, 6)

def run_command(command, shell=True):
    """Run a shell command and handle errors."""
    try:
        subprocess.run(command, shell=shell, check=True, universal_newlines=True)
        print("[INFO] Command succeeded: {}".format(command))
    except subprocess.CalledProcessError as e:
        print("[ERROR] Command failed: {}\nError: {}".format(command, e))
        exit(1)

def check_python_version():
    """Check if the current Python version is suitable."""
    current_version = sys.version_info[:2]
    if current_version < MIN_PYTHON_VERSION:
        print("[WARNING] Your Python version {} is outdated.".format(sys.version.split()[0]))
        print("[INFO] This script requires Python {}.{} or later.".format(MIN_PYTHON_VERSION[0], MIN_PYTHON_VERSION[1]))
        return False
    print("[INFO] Python version {} is sufficient.".format(sys.version.split()[0]))
    return True

def check_sudo_privileges():
    """Check for sudo privileges with user options."""
    while True:
        print("\n[INFO] Checking for sudo privileges...")
        print("1. Continue with the current password.")
        print("2. Set a new password for the current Linux user.")
        try:
            choice = int(input("Enter your choice (1 or 2): "))
            if choice == 1:
                print("[INFO] Please enter your current password to verify access...")
                try:
                    run_command("sudo -v")
                    return True
                except:
                    print("[ERROR] Incorrect password. Please use option 2 to reset the password.")
            elif choice == 2:
                print("[INFO] Setting a new password for your Linux user account...")
                run_command("sudo passwd $USER")
                print("[INFO] Password updated successfully. Rechecking sudo access...")
            else:
                print("[ERROR] Invalid choice. Please enter 1 or 2.")
        except ValueError:
            print("[ERROR] Please enter a valid number (1 or 2).")

def uninstall_docker():
    """Uninstall Docker and remove related files."""
    print("[INFO] Starting Docker uninstallation process...")
    
    # Remove Docker packages
    print("[INFO] Removing Docker packages...")
    run_command("sudo apt-get purge -y docker-ce docker-ce-cli containerd.io")
    
    # Remove all Docker files
    print("[INFO] Removing Docker related files and directories...")
    run_command("sudo rm -rf /var/lib/docker")
    run_command("sudo rm -rf /etc/docker")
    run_command("sudo rm -rf /var/run/docker.sock")
    run_command("sudo rm -rf /usr/local/bin/docker-compose")
    
    # Clean up leftover dependencies
    print("[INFO] Cleaning up unused packages...")
    run_command("sudo apt-get autoremove -y")
    run_command("sudo apt-get autoclean")
    
    print("[INFO] Docker has been successfully uninstalled and all related files have been removed.")

def install_docker():
    """Install Docker on the system."""
    print("[INFO] Starting Docker installation process...")

    # Check for Linux system
    if platform.system() != "Linux":
        print("[ERROR] This script is only supported on Linux systems.")
        exit(1)

    # Step 1: Verify sudo privileges
    check_sudo_privileges()

    # Step 2: Update the package list
    print("[INFO] Updating package list...")
    run_command("sudo apt-get update")

    # Step 3: Install prerequisite packages
    print("[INFO] Installing prerequisite packages...")
    run_command("sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common")

    # Step 4: Add Docker's GPG key
    print("[INFO] Adding Docker's GPG key...")
    run_command(
        "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg"
    )

    # Step 5: Set up the stable repository
    print("[INFO] Adding Docker repository...")
    run_command(
        "echo \"deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] "
        "https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable\" | "
        "sudo tee /etc/apt/sources.list.d/docker.list > /dev/null"
    )

    # Step 6: Update the package list again
    print("[INFO] Updating package list after adding Docker repository...")
    run_command("sudo apt-get update")

    # Step 7: Install Docker Engine
    print("[INFO] Installing Docker Engine...")
    run_command("sudo apt-get install -y docker-ce docker-ce-cli containerd.io")

    # Step 8: Verify Docker installation
    print("[INFO] Verifying Docker installation...")
    run_command("docker --version")
    print("[INFO] Docker installed successfully!")

    # Step 9: Add the current user to the Docker group
    print("[INFO] Adding the current user to the Docker group...")
    run_command('sudo usermod -aG docker "$USER"')

    # Step 10: Manual instructions for user permissions
    print("[INFO] To apply group changes, you must log out and log back in or reboot the system.")
    print("[INFO] Alternatively, reboot your system using: sudo reboot")
    print("[INFO] After rebooting, test Docker using the following command:")
    print("    docker run hello-world")

    # Step 11: Update Docker socket permissions (manual)
    print("[INFO] Fixing permission issue for Docker socket...")
    print("[INFO] Please enter your password when prompted.")
    run_command("sudo chown $USER /var/run/docker.sock")

    # Step 12: Final test for Docker
    print("[INFO] Running Docker test (hello-world container)...")
    try:
        run_command("docker run hello-world")
    except:
        print("[ERROR] You may still need to log out and back in, or reboot your system to resolve permissions.")
        print("[INFO] Reboot now using: sudo reboot")
    print("[INFO] Docker test completed successfully!")

if __name__ == "__main__":
    if not check_python_version():
        print("\n[ERROR] Your Python version is outdated. This script requires Python 3.6 or later.")
        exit(1)
    
    print("\nWhat would you like to do?")
    print("1. Install Docker")
    print("2. Uninstall Docker")
    try:
        option = int(input("Enter your choice (1 or 2): "))
        if option == 1:
            install_docker()
        elif option == 2:
            uninstall_docker()
        else:
            print("[ERROR] Invalid choice. Exiting...")
    except ValueError:
        print("[ERROR] Invalid input. Please enter 1 or 2.")
