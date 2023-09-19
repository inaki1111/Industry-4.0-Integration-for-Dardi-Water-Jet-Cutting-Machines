import login
import forms


def main():
    # The on_success parameter is set to forms.create_next_page
    # This means that when the login is successful, it will call forms.create_next_page
    login.create_login_window(forms.start_forms)

if __name__ == "__main__":
    main()
