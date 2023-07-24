import mysql.connector
import smtplib
from email.mime.text import MIMEText

# Function to create a connection to the database
def create_database_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="amit",
        database="food_management"  # Add the database name here
    )

# Function to create the database if it doesn't exist
def create_database():
    connection = create_database_connection()
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS food_management")
    cursor.close()
    connection.close()

# Function to create the table for storing user details and food donations
def create_user_and_donation_tables():
    connection = create_database_connection()
    cursor = connection.cursor()
    cursor.execute("USE food_management")
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, "
        "name VARCHAR(255), username VARCHAR(255) UNIQUE, phone_number VARCHAR(15), "
        "email VARCHAR(255), address TEXT, password VARCHAR(255), about TEXT)"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS food_donations (id INT AUTO_INCREMENT PRIMARY KEY, "
        "user_id INT, food_name VARCHAR(255), quantity INT, when_made DATETIME, "
        "fresh_till DATE, image_path VARCHAR(255), description TEXT, status VARCHAR(20))"
    )
    cursor.close()
    connection.close()

# Function to welcome users and display the main menu
def welcome_screen():
    print("Welcome to the Food Management System!")
    print("1. Create Account")
    print("2. Login")
    print("3. Admin Login")
    print("4. Exit")

# Function to create a new user account
def create_account():
    name = input("Enter your name: ")
    username = input("Enter a username: ")
    phone_number = input("Enter your phone number: ")
    email = input("Enter your email: ")
    address = input("Enter your address: ")
    password = input("Enter a password: ")
    about = input("Tell us something about yourself: ")

    connection = create_database_connection()
    cursor = connection.cursor()
    cursor.execute("USE food_management")
    cursor.execute(
        "INSERT INTO users (name, username, phone_number, email, address, password, about) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (name, username, phone_number, email, address, password, about)
    )
    connection.commit()
    cursor.close()
    connection.close()

    print("Account created successfully!")

# Function to handle user login
def login():
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    connection = create_database_connection()
    cursor = connection.cursor()
    cursor.execute("USE food_management")
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if user:
        print("Login successful!")
        display_user_details(user)
        return user  # Return the user information to be used for donation
    else:
        print("Invalid username or password. Please try again.")
        return None

# Function to display user details
def display_user_details(user):
    print("\nUser Details:")
    print("Name:", user[1])
    print("Username:", user[2])
    print("Phone Number:", user[3])
    print("Email:", user[4])
    print("Address:", user[5])
    print("About:", user[7])

# Function to handle food donation
def donate_food(user):
    print("You chose to donate food.")
    food_name = input("Enter Food Name: ")
    quantity = int(input("Enter Quantity: "))
    when_made = input("Enter When Made (e.g., YYYY-MM-DD HH:mm:ss): ")
    fresh_till = input("Enter Fresh Till (e.g., YYYY-MM-DD): ")
    image_path = input("Enter Image Path: ")
    description = input("Enter Description: ")

    # Show the user the entered information for confirmation
    print("\nPlease confirm the following details:")
    print("Food Name:", food_name)
    print("Quantity:", quantity)
    print("When Made:", when_made)
    print("Fresh Till:", fresh_till)
    print("Image Path:", image_path)
    print("Description:", description)

    confirmation = input("Are you sure to submit? (Y/N): ").upper()
    if confirmation == "Y":
        connection = create_database_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO food_donations (user_id, food_name, quantity, when_made, fresh_till, image_path, description, status) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (user[0], food_name, quantity, when_made, fresh_till, image_path, description, "pending")
        )
        connection.commit()
        cursor.close()
        connection.close()
        print("Donation request submitted successfully!")
    else:
        print("Donation request canceled.")

# Function to handle food collection
def get_food(user):
    print("You chose to get food.")

    # Show accepted food donations for the user
    accept_food(user)

    # Request food from available donations
    request_food(user)

# Function to handle accepting food donations
def accept_food(user):
    connection = create_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM food_donations WHERE user_id=%s AND status='approved'", (user[0],))
    accepted_donations = cursor.fetchall()
    cursor.close()
    connection.close()

    if not accepted_donations:
        print("You have not accepted any food donations.")
    else:
        print("Accepted Food Donations:")
        for donation in accepted_donations:
            print("Request ID:", donation[0])
            print("Food Name:", donation[2])
            print("Quantity:", donation[3])
            print("When Made:", donation[4])
            print("Fresh Till:", donation[5])
            print("Description:", donation[7])
            print("----------------------")

# Function to handle user request for food
def request_food(user):
    connection = create_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM food_donations WHERE status='approved'")
    approved_donations = cursor.fetchall()
    cursor.close()
    connection.close()

    if not approved_donations:
        print("No approved food donations available at the moment.")
        return

    print("Approved Food Donations:")
    for donation in approved_donations:
        print("Request ID:", donation[0])
        print("Food Name:", donation[2])
        print("Quantity:", donation[3])
        print("When Made:", donation[4])
        print("Fresh Till:", donation[5])
        print("Description:", donation[7])
        print("----------------------")

    request_id = int(input("Enter the ID of the request you want to accept (0 to cancel): "))

    if request_id == 0:
        print("Food request canceled.")
        return

    connection = create_database_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE food_donations SET status='accepted' WHERE id=%s", (request_id,))
    connection.commit()
    cursor.close()
    connection.close()
    print("Food request accepted!")

# Function to handle admin login
def admin_login():
    print("Admin login:")
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    if username == "!@#$" and password == "%^&*":
        admin_menu()
    else:
        print("Invalid username or password.")

# Function to display the admin menu
def admin_menu():
    while True:
        print("\nAdmin Menu:")
        print("1. View all user details")
        print("2. View all food donation details")
        print("3. View pending donation requests")
        print("4. Logout")
        admin_choice = int(input("Enter your choice: "))

        if admin_choice == 1:
            view_all_users()
        elif admin_choice == 2:
            view_all_food_donations()
        elif admin_choice == 3:
            admin_approve_reject_food()
        elif admin_choice == 4:
            print("Admin logged out.")
            break
        else:
            print("Invalid choice. Please try again.")

# Function to view all user details
def view_all_users():
    connection = create_database_connection()
    cursor = connection.cursor()
    cursor.execute("USE food_management")
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    connection.close()

    if not users:
        print("No users found.")
    else:
        print("All User Details:")
        for user in users:
            display_user_details(user)
            print("----------------------")

# Function to view all food donation details
def view_all_food_donations():
    connection = create_database_connection()
    cursor = connection.cursor()
    cursor.execute("USE food_management")
    cursor.execute("SELECT * FROM food_donations")
    donations = cursor.fetchall()
    cursor.close()
    connection.close()

    if not donations:
        print("No food donations found.")
    else:
        print("All Food Donation Details:")
        for donation in donations:
            display_food_donation(donation)
            print("----------------------")

# Function to display food donation details
def display_food_donation(donation):
    print("Request ID:", donation[0])
    print("User ID:", donation[1])
    print("Food Name:", donation[2])
    print("Quantity:", donation[3])
    print("When Made:", donation[4])
    print("Fresh Till:", donation[5])
    print("Image Path:", donation[6])
    print("Description:", donation[7])
    print("Status:", donation[8])

# Function to view all food donation details
def view_all_food_donations():
    connection = create_database_connection()
    cursor = connection.cursor()
    cursor.execute("USE food_management")
    cursor.execute("SELECT * FROM food_donations")
    donations = cursor.fetchall()
    cursor.close()
    connection.close()

    if not donations:
        print("No food donations found.")
    else:
        print("All Food Donation Details:")
        for donation in donations:
            display_food_donation(donation)
            print("----------------------")

# Function to display food donation details
def display_food_donation(donation):
    print("Request ID:", donation[0])
    print("User ID:", donation[1])
    print("Food Name:", donation[2])
    print("Quantity:", donation[3])
    print("When Made:", donation[4])
    print("Fresh Till:", donation[5])
    print("Image Path:", donation[6])
    print("Description:", donation[7])
    print("Status:", donation[8])

# Function to view all food donation details
def view_all_food_donations():
    connection = create_database_connection()
    cursor = connection.cursor()
    cursor.execute("USE food_management")
    cursor.execute("SELECT * FROM food_donations")
    donations = cursor.fetchall()
    cursor.close()
    connection.close()

    if not donations:
        print("No food donations found.")
    else:
        print("All Food Donation Details:")
        for donation in donations:
            display_food_donation(donation)
            print("----------------------")

# Function to handle approving or rejecting food donation requests
def admin_approve_reject_food():
    connection = create_database_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM food_donations WHERE status='pending'")
    pending_donations = cursor.fetchall()
    cursor.close()
    connection.close()

    if not pending_donations:
        print("No pending food donation requests.")
        return

    print("Pending Food Donation Requests:")
    for donation in pending_donations:
        print("Request ID:", donation[0])
        print("User ID:", donation[1])
        print("Food Name:", donation[2])
        print("Quantity:", donation[3])
        print("When Made:", donation[4])
        print("Fresh Till:", donation[5])
        print("Description:", donation[7])
        print("----------------------")

        request_id = donation[0]
        user_id = donation[1]
        user = get_user_by_id(user_id)

        approval_status = input("Do you want to approve or reject the request? (approve/reject): ").lower()
        if approval_status == "approve":
            approve_food_donation(request_id)
            if user:
                send_email_to_user(user, "Food Donation Approval", "Your food donation request has been approved. Thank you for your contribution!")
        elif approval_status == "reject":
            reject_food_donation(request_id)
            if user:
                send_email_to_user(user, "Food Donation Rejection", "Your food donation request has been rejected. We appreciate your efforts.")
        else:
            print("Invalid choice. Please enter 'approve' or 'reject'.")

def get_user_by_id(user_id):
    connection = create_database_connection()
    cursor = connection.cursor()
    cursor.execute("USE food_management")
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    return user

def approve_food_donation(request_id):
    connection = create_database_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE food_donations SET status='approved' WHERE id=%s", (request_id,))
    connection.commit()
    cursor.close()
    connection.close()
    print("Food donation request approved!")

def reject_food_donation(request_id):
    connection = create_database_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE food_donations SET status='rejected' WHERE id=%s", (request_id,))
    connection.commit()
    cursor.close()
    connection.close()
    print("Food donation request rejected!")

def send_email_to_user(user, subject, message):
    # Replace these values with your actual email credentials and settings
    sender_email = "your_email@example.com"
    sender_password = "your_email_password"
    smtp_server = "your_smtp_server"
    smtp_port = 587

    recipient_email = user[4]

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print("Failed to send email:", e)


# The main block of the code
if __name__ == "__main__":
    create_database()
    create_user_and_donation_tables()

    while True:
        welcome_screen()
        choice = int(input("Enter your choice: "))

        if choice == 1:
            create_account()
        elif choice == 2:
            user = login()
            if user:
                while True:
                    print("\nUser Menu:")
                    print("1. Donate Food")
                    print("2. Get Food")
                    print("3. Logout")
                    user_choice = int(input("Enter your choice: "))
                    if user_choice == 1:
                        donate_food(user)
                    elif user_choice == 2:
                        get_food(user)
                    elif user_choice == 3:
                        print("Logged out.")
                        break
                    else:
                        print("Invalid choice. Please try again.")
        elif choice == 3:
            admin_login()
        elif choice == 4:
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

