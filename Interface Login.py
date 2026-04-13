import random
import os
import tkinter as tk
from tkinter import messagebox

#Phase 1: login (and registration *extra*) system + 1 easy minigame
#Phase 2: ???? 

# 1.Persistent Storage Setup / Data Handling
SCRIPT_FOLDER = os.path.dirname(os.path.abspath(__file__)) #Get the folder where the script is located
DATA_FILE = os.path.join(SCRIPT_FOLDER, 'user-data.txt')#Create a file path for the data file in the same folder as the script

#Load user data from the file, return a data of users with their passwords and scores
def load_data(): 
    data = {}
    if not os.path.exists(DATA_FILE): #If the data file doesn't exist, create it and return an empty data to store user data
        with open(DATA_FILE, 'w') as file:
            pass 
        return data

    #Split each line into username, password, and score, and store it in the data
    with open(DATA_FILE, 'r') as file: 
        for line in file:
            parts = line.strip().split(',')
            if len(parts) == 3:
                username = parts[0]
                password = parts[1]
                score = int(parts[2])
                data[username] = {'password': password, 'score': score}
    return data

def save_data(data): #Save the user data back to the file, user's username, password, and score in a new line
    with open(DATA_FILE, 'w') as file:
        for username, info in data.items():
            file.write(f"{username},{info['password']},{info['score']}\n")

# 2.GUI Application with Tkinter
#class
class EnglishLearningApp: #Main application class that handles the GUI and game logic
    def __init__(self, root): #open a application, set up the main window, load user data, and prepare the different screens
        #Set the title, size, and background color of the main window
        self.root = root 
        self.root.title("Interactive English Learning") #(title)
        self.root.geometry("400x450") #(window size)
        self.root.configure(bg="#f0f4f8") #(background color)
        
        #Load user data from the file when the application starts, and store it in a variable for later use
        self.data = load_data() #A variable to keep track of the currently logged in user, and the current word being played in the game
        self.active_user = None #(store the username of the currently logged in user as value)
        self.current_word = "" #(store and use current word as value)
        self.scrambled_word = "" #(store and use scrambled word as value)
        # Font styling
        self.title_font = ("Helvetica", 16, "bold")
        self.normal_font = ("Helvetica", 12)
        
        # Setup all screens
        #call the function for all
        self.setup_login_screen()
        self.setup_menu_screen()
        self.setup_game_screen() 
        self.setup_leaderboard_screen()
        
        # Start by showing the login screen
        self.show_screen(self.frame_login)






    # A function to switch between different screens by hiding all screens and showing the requested one
    def show_screen(self, frame_to_show):
        # Loop through all frames and hide them, then show the frame that was requested
        for frame in (self.frame_login, self.frame_menu, self.frame_game, self.frame_leaderboard):
            # Hide all frames
            frame.pack_forget()
        # Show the requested frame/screen
        frame_to_show.pack(fill="both", expand=True, padx=20, pady=20)

    # --- SCREEN SETUPS ---
    #1st screen: login screen, where users can enter their username and password to log in or register a new account
    def setup_login_screen(self):
        
        #self.frame_login is a variable that holds the login screen frame
        self.frame_login = tk.Frame(self.root, bg="#f0f4f8") 

        #Add a title label 
        tk.Label(self.frame_login, text="Welcome to English Learner", font=self.title_font, bg="#f0f4f8", pady=20).pack()
        
        #Add labels and entry fields(input box) for username and buttons
        tk.Label(self.frame_login, text="Username:", font=self.normal_font, bg="#f0f4f8").pack() #(create a label for username)
        self.entry_username = tk.Entry(self.frame_login, font=self.normal_font) #(create input box for username)
        self.entry_username.pack(pady=5) #(display it)
        
        #Add labels and entry fields(input box) for password, and buttons
        tk.Label(self.frame_login, text="Password:", font=self.normal_font, bg="#f0f4f8").pack() #(create a label for password)
        self.entry_password = tk.Entry(self.frame_login, font=self.normal_font, show="*") #(create input box for password) , show="*" makes the password input hidden with asterisks for security
        self.entry_password.pack(pady=5) #(display it)
        
        #Add buttons for login and registration, and link them to their functions
        tk.Button(self.frame_login, text="Login", font=self.normal_font, width=15, bg="#4CAF50", fg="white", command=self.login).pack(pady=10) #Login button
        tk.Button(self.frame_login, text="Register", font=self.normal_font, width=15, bg="#2196F3", fg="white", command=self.register).pack() #Register button

    #2nd screen: menu screen, where users can choose to play the word scramble game, view the leaderboard, or log out
    def setup_menu_screen(self):
        
        #self.frame_menu is a variable that holds the menu screen frame
        self.frame_menu = tk.Frame(self.root, bg="#f0f4f8")
        
        #A label to show the welcome message with the user's name and score, which will be updated when the user logs in
        self.lbl_welcome = tk.Label(self.frame_menu, text="", font=self.title_font, bg="#f0f4f8", pady=20) #(create a label for welcome message, initially empty) 
        self.lbl_welcome.pack() #(display it)
        
        #Add buttons for playing the game, viewing the leaderboard, and logging out, and link them to their functions
        tk.Button(self.frame_menu, text="Play Word Scramble", font=self.normal_font, width=20, pady=10, bg="#ff9800", fg="white", command=self.start_game).pack(pady=10) #Start game button
        tk.Button(self.frame_menu, text="View Leaderboard", font=self.normal_font, width=20, pady=10, bg="#9c27b0", fg="white", command=self.show_leaderboard).pack(pady=10) #Leaderboard button
        tk.Button(self.frame_menu, text="Logout", font=self.normal_font, width=20, bg="#f44336", fg="white", command=self.logout).pack(pady=30) #Logout button
    
    #3rd screen: game screen, where users can see a scrambled word and enter their guess to unscramble it, with buttons to submit the guess or go back to the menu
    def setup_game_screen(self):
        #self.frame_game is a variable that holds the game screen frame
        self.frame_game = tk.Frame(self.root, bg="#f0f4f8")
        
        #Add a title label and instructions for the game, and create labels and entry fields for the scrambled word and the user's guess, as well as buttons to submit the guess and go back to the menu
        tk.Label(self.frame_game, text="Word Scramble", font=self.title_font, bg="#f0f4f8", pady=10).pack() #Title label for the game screen
        tk.Label(self.frame_game, text="Unscramble the letters below:", font=self.normal_font, bg="#f0f4f8").pack() #Instruction label for the game screen
        
        #A label to display the scrambled word, which will be updated with a new scrambled word each time the game starts
        self.lbl_scrambled = tk.Label(self.frame_game, text="", font=("Helvetica", 20, "bold"), fg="#e91e63", bg="#f0f4f8", pady=15) #(create a label for the scrambled word, initially empty)
        self.lbl_scrambled.pack() #(display it)

        #An entry field for the user to input their guess, which will be checked against the current word when they submit their guess        
        self.entry_guess = tk.Entry(self.frame_game, font=self.normal_font) #(create an input box for the user's guess)
        self.entry_guess.pack(pady=10) #(display it)
        
        #Add buttons for submitting the guess and going back to the menu, and link them to their functions
        tk.Button(self.frame_game, text="Submit Guess", font=self.normal_font, bg="#4CAF50", fg="white", command=self.check_guess).pack(pady=5) #Submit guess button
        tk.Button(self.frame_game, text="Back to Menu", font=self.normal_font, command=lambda: self.show_screen(self.frame_menu)).pack(pady=20) #Back to menu button, lambda is an anonymous function that allows us to call the show_screen function with the frame_menu argument when the button is clicked 
    
    #4th screen: leaderboard screen, where users can see the top players and their scores, with a button to go back to the menu
    def setup_leaderboard_screen(self):
        #self.frame_leaderboard is a variable that holds the leaderboard screen frame
        self.frame_leaderboard = tk.Frame(self.root, bg="#f0f4f8")
        
        #Add a title label for the leaderboard screen, and create a text box to display the scores, as well as a button to go back to the menu
        tk.Label(self.frame_leaderboard, text="Top Players", font=self.title_font, bg="#f0f4f8", pady=10).pack() #Title label for the leaderboard screen
        
        # A text box to display scores
        self.txt_scores = tk.Text(self.frame_leaderboard, height=12, width=30, font=self.normal_font, bg="white", state="disabled") #Create a text box for displaying the scores, initially disabled so users can't type in it
        self.txt_scores.pack(pady=10) #(display it)
        
        tk.Button(self.frame_leaderboard, text="Back to Menu", font=self.normal_font, command=lambda: self.show_screen(self.frame_menu)).pack(pady=10) #Back to menu button

    # --- BUTTON LOGIC ---

    def login(self):
        #Get the username and password from the entry fields, and check if they match an existing user in the data. If they do, log the user in and show the menu screen, otherwise show an error message
        username = self.entry_username.get().strip() #Get the username from the input box  
        password = self.entry_password.get().strip() #Get the password from the input box
        
        #check
        if username in self.data and self.data[username]['password'] == password:
            self.active_user = username #Set the active user to the logged in username
            self.lbl_welcome.config(text=f"Welcome back, {username}!\nScore: {self.data[username]['score']}") #Update the welcome label with the user's name and score
            self.show_screen(self.frame_menu) #Show the menu screen after successful login
            self.entry_password.delete(0, tk.END) # Clear password field for security
        else:
            messagebox.showerror("Error", "Invalid username or password.") #Show an error message if the username or password is incorrect

    def register(self):
        username = self.entry_username.get().strip() #Get the username from the input box
        password = self.entry_password.get().strip() #Get the password from the input box

        #check if both are filled and don't contain commas        
        if not username or not password:
            messagebox.showwarning("Warning", "Please fill in both fields.") #Show a warning message
            return
        if ',' in username or ',' in password: #Check if the username or password contains commas
            messagebox.showwarning("Warning", "Commas are not allowed.") #Show a warning message
            return
        
        #Check if the username already exists in the data
        if username in self.data:
            messagebox.showerror("Error", "Username already exists!") #Show an error message if the username is already taken
        else:
            self.data[username] = {'password': password, 'score': 0} #Add the new user to the data with their password and an initial score of 0
            save_data(self.data) #Save the updated data to the file
            messagebox.showinfo("Success", "Registration successful! You can now log in.") #Show a success message

    def logout(self):
        #Log the user out by clearing the active user variable
        self.active_user = None #Clear the active user variable to log out
        self.entry_username.delete(0, tk.END) #clear the username field
        self.entry_password.delete(0, tk.END) #clear the password field
        self.show_screen(self.frame_login) #Show the login screen after logging out

    def start_game(self):
        #Select a random word from the list (add to infinite words later)
        words = ['algorithm', 'variable', 'function', 'database', 'syntax', 'network']
        self.current_word = random.choice(words) #Select a random word from the list
        
        #Scramble the selected word by shuffling its letters
        scrambled = list(self.current_word) #Convert the word into a list of characters to shuffle
        random.shuffle(scrambled) #Shuffle the list of characters to create a scrambled version of the word
        self.scrambled_word = "".join(scrambled) #Join the shuffled characters back into a string to display as the scrambled word
        
        #Update the scrambled word label with the new scrambled word
        self.lbl_scrambled.config(text=self.scrambled_word) #Update the label to show the scrambled word for the user to guess
        self.entry_guess.delete(0, tk.END) #Clear the guess entry field for the new word
        self.show_screen(self.frame_game) #Show the game screen to start the game

    def check_guess(self):
        guess = self.entry_guess.get().strip().lower() #Get the user's guess from the input box
        
        #Check if the guess is correct by comparing it to the current word
        if guess == self.current_word:
            self.data[self.active_user]['score'] += 10 #add 10 points to the user's score in the data
            save_data(self.data) #Save the updated data to the file to persist the new score
            self.lbl_welcome.config(text=f"Welcome back, {self.active_user}!\nScore: {self.data[self.active_user]['score']}") #Update the welcome label with the user's name and new score
            messagebox.showinfo("Correct!", "You earned 10 points!") #Show a message box to inform the user is correct
            self.start_game() # Load next word
        else:
            messagebox.showerror("Incorrect", f"Wrong! The word was '{self.current_word}'.") #Show a message box to inform the user is wrong
            self.start_game() # Load next word

    def show_leaderboard(self):
        #Display the leaderboard by sorting the users in the data by their scores and showing them in the text box
        self.txt_scores.config(state="normal") #Enable the text box so we can update it with the latest scores
        self.txt_scores.delete(1.0, tk.END) #Clear the text box before displaying the updated leaderboard
        
        #Check if there are any users in the data
        if not self.data:
            self.txt_scores.insert(tk.END, "No players yet.") #show a message indicating that there are no players
        else:
            sorted_users = sorted(self.data.items(), key=lambda x: x[1]['score'], reverse=True) #Sort the users in the data by their scores in descending order
            rank = 1 #Initialize a rank variable

            #Loop through the sorted users and insert their names and scores into the text box, along with their rank
            for user, info in sorted_users:
                self.txt_scores.insert(tk.END, f"{rank}. {user} - {info['score']} pts\n") #Insert the user's rank, username, and score into the text box
                rank += 1 #Increment the rank for the next user
        
        #After updating the leaderboard, lock the text box again so users can't type in it
        self.txt_scores.config(state="disabled") #Disable the text box again to prevent user input
        self.show_screen(self.frame_leaderboard) #Show the leaderboard screen to display the updated leaderboard

# --- Start Program ---
if __name__ == "__main__": #Check if the script is being run directly
    root = tk.Tk() #Create the main application window
    app = EnglishLearningApp(root) #run the EnglishLearningApp class
    root.mainloop() #Start the Tkinter event loop to run the application