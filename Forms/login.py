import customtkinter
import tkinter as tk
from tkinter.simpledialog import askstring



def check_login(entered_username, entered_password):
    try:
        with open("enterLog.txt", "r") as file:
            # Read the lines and remove leading/trailing whitespace and square brackets.
            lines = [line.strip('[]').strip() for line in file]

            # Split each line into a list of usernames and passwords.
            stored_usernames = lines[0].split(', ')
            stored_passwords = lines[1].split(', ')

        # Check if entered credentials match any of the stored ones.
        return entered_username in stored_usernames and entered_password in stored_passwords
    except FileNotFoundError:
        # Handle the case where the file doesn't exist.
        return False

def add_user(username, password):
    try:
        with open("enterLog.txt", "r") as file:
            lines = [line.strip() for line in file]

        # Extract existing usernames and passwords.
        stored_usernames = lines[0].strip('[]').split(', ')
        stored_passwords = lines[1].strip('[]').split(', ')

        # Add the new username and password.
        stored_usernames.append(username)
        stored_passwords.append(password)

        # Write the updated content back to the file.
        with open("enterLog.txt", "w") as file:
            file.write(f"[{', '.join(stored_usernames)}]\n")
            file.write(f"[{', '.join(stored_passwords)}]\n")

        return True
    except Exception as e:
        print(f"Error adding user: {e}")
        return False
   

def create_login_window(on_success):
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("dark-blue")

    root = customtkinter.CTk()
    root.geometry("1000x600")
    # Set the title of the application window
    root.title("Login Page")

    frame = customtkinter.CTkFrame(master=root)
    frame.pack(pady=20, padx=60, fill="both", expand=True)

    label = customtkinter.CTkLabel(master=frame, text="Inicio de sesion", font=('Roboto', 24))
    label.pack(pady=20, padx=10)

    entry1 = customtkinter.CTkEntry(master=frame, placeholder_text="Usuario")
    entry1.pack(pady=10, padx=10)   

    entry2 = customtkinter.CTkEntry(master=frame, placeholder_text="Contrasena", show="*")
    entry2.pack(pady=10, padx=10)

    def add_new_user():
        new_username = askstring("Add New User", "Enter new username:")
        if new_username:
            new_password = askstring("Add New User", "Enter new password:")
            if new_password:
                if add_user(new_username, new_password):
                    print("New user added successfully.")
                else:
                    print("Failed to add a new user.")


    def login():
        if check_login(entry1.get(), entry2.get()):
            root.destroy()
            on_success()
        else:
            print("EL usuario o contrasena no son validos.")



    button = customtkinter.CTkButton(master=frame, text="Entrar", command=login)
    button.pack(pady=10, padx=10)


    add_user_button = customtkinter.CTkButton(master=frame, text="Add User", command=add_new_user)
    add_user_button.pack(pady=10, padx=10)


    root.mainloop()




# to run it alone

'''

if __name__ == "__main__":
    def on_success():
        print("Logged in successfully!")

    create_login_window(on_success)
'''