# Import required libraries
import random
import datetime

# Define a dictionary for user data
user_data = {
    "name": "",
    "phone_number": "",
    "balance": 0,
    "recharge_history": []
}

# Define a dictionary for automated messages
messages = {
    "welcome": "Welcome! Please enter your name:",
    "menu": "Choose an option:\n1. Balance inquiry\n2. Recharge\n3. Customer support\n4. Recharge history\n5. Exit",
    "balance": "Your balance is {}",
    "recharge": "Recharge successful! Amount: {}",
    "support": "Our customer support team will contact you soon.",
    "recharge_history": "Your recharge history: {}",
    "exit": "Thank you for using our service!",
    "invalid_choice": "Invalid choice. Please try again.",
    "enter_phone_number": "Please enter your phone number:",
    "enter_recharge_amount": "Enter recharge amount: "
}
# Define a function to display menu
def display_menu():
    print(messages["menu"])

# Define a function to handle user input
def handle_input(user_input):
    if user_input == "1":
        print(messages["balance"].format(user_data["balance"]))
    elif user_input == "2":
        amount = int(input(messages["enter_recharge_amount"]))
        user_data["balance"] += amount
        user_data["recharge_history"].append({"amount": amount, "date": datetime.datetime.now()})
        print(messages["recharge"].format(amount))
    elif user_input == "3":
        print(messages["support"])
    elif user_input == "4":
        if len(user_data["recharge_history"]) == 0:
            print("No recharge history found.")
        else:
            print(messages["recharge_history"].format(", ".join([str(item["amount"]) + " on " + str(item["date"]) for item in user_data["recharge_history"]])))
    elif user_input == "5":
        print(messages["exit"])
        return False
    else:
        print(messages["invalid_choice"])
    return True

# Define a function for the chatbot
def chatbot():
    print(messages["welcome"])
    user_data["name"] = input()
    print(messages["enter_phone_number"])
    user_data["phone_number"] = input()
    display_menu()
    while True:
        user_input = input("Enter your choice (1/2/3/4/5): ")
        if not handle_input(user_input):
            break

# Run the chatbot
chatbot()
##basic testing of git
##nothing
