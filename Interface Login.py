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
        self.root.title("Interactive English Learning")
        self.root.geometry("400x450")
        self.root.configure(bg="#f0f4f8")
        
        #Load user data from the file when the application starts, and store it in a variable for later use
        self.data = load_data() 
        self.active_user = None
        self.current_word = ""
        self.scrambled_word = ""
        
        # Font styling
        self.title_font = ("Helvetica", 16, "bold")
        self.normal_font = ("Helvetica", 12)
        
        # Setup all screens
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
        # Show the requested frame
        frame_to_show.pack(fill="both", expand=True, padx=20, pady=20)

    # --- SCREEN SETUPS ---
    #1st screen: login screen, where users can enter their username and password to log in or register a new account
    def setup_login_screen(self):
        
        #Create the login screen with labels, entry fields for username and password, and buttons for login and registration
        self.frame_login = tk.Frame(self.root, bg="#f0f4f8")

        #Add a title label 
        tk.Label(self.frame_login, text="Welcome to English Learner", font=self.title_font, bg="#f0f4f8", pady=20).pack()
        
        #Add labels and entry fields(input box) for username and buttons
        tk.Label(self.frame_login, text="Username:", font=self.normal_font, bg="#f0f4f8").pack()
        self.entry_username = tk.Entry(self.frame_login, font=self.normal_font)
        self.entry_username.pack(pady=5)
        
        #Add labels and entry fields(input box) for password, and buttons
        tk.Label(self.frame_login, text="Password:", font=self.normal_font, bg="#f0f4f8").pack()
        self.entry_password = tk.Entry(self.frame_login, font=self.normal_font, show="*")
        self.entry_password.pack(pady=5)
        
        #Add buttons for login and registration, and link them to their functions
        tk.Button(self.frame_login, text="Login", font=self.normal_font, width=15, bg="#4CAF50", fg="white", command=self.login).pack(pady=10)
        tk.Button(self.frame_login, text="Register", font=self.normal_font, width=15, bg="#2196F3", fg="white", command=self.register).pack()

    #2nd screen: menu screen, where users can choose to play the word scramble game, view the leaderboard, or log out
    def setup_menu_screen(self):
        
        #Create the menu screen with a welcome message that shows the user's name and score, and buttons to game, leaderboard, logout
        self.frame_menu = tk.Frame(self.root, bg="#f0f4f8")
        
        #
        self.lbl_welcome = tk.Label(self.frame_menu, text="", font=self.title_font, bg="#f0f4f8", pady=20)
        self.lbl_welcome.pack()
        

        tk.Button(self.frame_menu, text="Play Word Scramble", font=self.normal_font, width=20, pady=10, bg="#ff9800", fg="white", command=self.start_game).pack(pady=10)
        tk.Button(self.frame_menu, text="View Leaderboard", font=self.normal_font, width=20, pady=10, bg="#9c27b0", fg="white", command=self.show_leaderboard).pack(pady=10)
        tk.Button(self.frame_menu, text="Logout", font=self.normal_font, width=20, bg="#f44336", fg="white", command=self.logout).pack(pady=30)
    
    #3rd screen: game screen, where users can see a scrambled word and enter their guess to unscramble it, with buttons to submit the guess or go back to the menu
    def setup_game_screen(self):
        self.frame_game = tk.Frame(self.root, bg="#f0f4f8")
        
        tk.Label(self.frame_game, text="Word Scramble", font=self.title_font, bg="#f0f4f8", pady=10).pack()
        tk.Label(self.frame_game, text="Unscramble the letters below:", font=self.normal_font, bg="#f0f4f8").pack()
        
        self.lbl_scrambled = tk.Label(self.frame_game, text="", font=("Helvetica", 20, "bold"), fg="#e91e63", bg="#f0f4f8", pady=15)
        self.lbl_scrambled.pack()
        
        self.entry_guess = tk.Entry(self.frame_game, font=self.normal_font)
        self.entry_guess.pack(pady=10)
        
        tk.Button(self.frame_game, text="Submit Guess", font=self.normal_font, bg="#4CAF50", fg="white", command=self.check_guess).pack(pady=5)
        tk.Button(self.frame_game, text="Back to Menu", font=self.normal_font, command=lambda: self.show_screen(self.frame_menu)).pack(pady=20)
    
    #4th screen: leaderboard screen, where users can see the top players and their scores, with a button to go back to the menu
    def setup_leaderboard_screen(self):
        self.frame_leaderboard = tk.Frame(self.root, bg="#f0f4f8")
        
        tk.Label(self.frame_leaderboard, text="Top Players", font=self.title_font, bg="#f0f4f8", pady=10).pack()
        
        # A text box to display scores
        self.txt_scores = tk.Text(self.frame_leaderboard, height=12, width=30, font=self.normal_font, bg="white", state="disabled")
        self.txt_scores.pack(pady=10)
        
        tk.Button(self.frame_leaderboard, text="Back to Menu", font=self.normal_font, command=lambda: self.show_screen(self.frame_menu)).pack(pady=10)

    # --- BUTTON LOGIC ---

    def login(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        
        if username in self.data and self.data[username]['password'] == password:
            self.active_user = username
            self.lbl_welcome.config(text=f"Welcome back, {username}!\nScore: {self.data[username]['score']}")
            self.show_screen(self.frame_menu)
            self.entry_password.delete(0, tk.END) # Clear password field for security
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    def register(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Warning", "Please fill in both fields.")
            return
        if ',' in username or ',' in password:
            messagebox.showwarning("Warning", "Commas are not allowed.")
            return
            
        if username in self.data:
            messagebox.showerror("Error", "Username already exists!")
        else:
            self.data[username] = {'password': password, 'score': 0}
            save_data(self.data)
            messagebox.showinfo("Success", "Registration successful! You can now log in.")

    def logout(self):
        self.active_user = None
        self.entry_username.delete(0, tk.END)
        self.show_screen(self.frame_login)

    def start_game(self):
        words = ['algorithm', 'variable', 'function', 'database', 'syntax', 'network']
        self.current_word = random.choice(words)
        
        scrambled = list(self.current_word)
        random.shuffle(scrambled)
        self.scrambled_word = "".join(scrambled)
        
        self.lbl_scrambled.config(text=self.scrambled_word)
        self.entry_guess.delete(0, tk.END)
        self.show_screen(self.frame_game)

    def check_guess(self):
        guess = self.entry_guess.get().strip().lower()
        
        if guess == self.current_word:
            self.data[self.active_user]['score'] += 10
            save_data(self.data)
            self.lbl_welcome.config(text=f"Welcome back, {self.active_user}!\nScore: {self.data[self.active_user]['score']}")
            messagebox.showinfo("Correct!", "You earned 10 points!")
            self.start_game() # Load next word
        else:
            messagebox.showerror("Incorrect", f"Wrong! The word was '{self.current_word}'.")
            self.start_game() # Load next word

    def show_leaderboard(self):
        self.txt_scores.config(state="normal") # Enable text box to write into it
        self.txt_scores.delete(1.0, tk.END)    # Clear old text
        
        if not self.data:
            self.txt_scores.insert(tk.END, "No players yet.")
        else:
            sorted_users = sorted(self.data.items(), key=lambda x: x[1]['score'], reverse=True)
            rank = 1
            for user, info in sorted_users:
                self.txt_scores.insert(tk.END, f"{rank}. {user} - {info['score']} pts\n")
                rank += 1
                
        self.txt_scores.config(state="disabled") # Lock it so user can't type in it
        self.show_screen(self.frame_leaderboard)

# --- Start Program ---
if __name__ == "__main__":
    root = tk.Tk()
    app = EnglishLearningApp(root)
    root.mainloop()