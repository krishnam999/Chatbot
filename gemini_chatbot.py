import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from dotenv import load_dotenv
import google.generativeai as genai
import requests
import threading


class GeminiChatbot:
    def __init__(self, root):
        self.root = root
        self.root.title("Gemini Chatbot")
        self.root.geometry("700x800")
        self.root.configure(bg="#1a1a1b")
        
        self.setup_gemini()
        self.create_widgets()
        self._configure_styles()
    
    def setup_gemini(self):
        """Initialize Gemini API"""
        try:
            load_dotenv()
            API_KEY = os.getenv("GEMINI_API_KEY")
            
            if not API_KEY:
                messagebox.showwarning(
                    "API Key Required",
                    "Please set your GEMINI_API_KEY in a .env file."
                )
                self.root.destroy()
                return
            
            genai.configure(api_key=API_KEY)
            # Use the 'gemini-1.5-flash' model for faster responses
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.chat = self.model.start_chat(history=[])
            
        except Exception as e:
            messagebox.showerror("API Error", f"Failed to initialize Gemini API: {str(e)}")
            self.root.destroy()
    
    def create_widgets(self):
        """Create and layout all the widgets for the UI."""
        main_container = ttk.Frame(self.root, padding="15")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(2, weight=1) # Chat area row
        
        self._create_header(main_container)
        self._create_chat_area(main_container)
        self._create_input_area(main_container)
        self._create_status_bar(main_container)
        
        self.user_input.focus()

    def _create_header(self, parent):
        """Creates the header with title and clear button."""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(0, weight=1)
        
        title_label = ttk.Label(header_frame, text="🤖 Gemini AI Assistant", 
                               font=('Arial', 18, 'bold'))
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        clear_button = ttk.Button(header_frame, text="Clear Chat", command=self.clear_chat)
        clear_button.grid(row=0, column=1, sticky=tk.E)

    def _create_chat_area(self, parent):
        """Creates the scrolled text widget for displaying the chat."""
        chat_frame = ttk.LabelFrame(parent, text="Chat", padding="10")
        chat_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=('Arial', 11),
            bg='#fafafa',
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.chat_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.chat_display.config(state=tk.DISABLED)

    def _create_input_area(self, parent):
        """Creates the user input entry and send button."""
        input_frame = ttk.Frame(parent)
        input_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        input_frame.columnconfigure(0, weight=1)
        
        self.user_input = ttk.Entry(input_frame, font=('Arial', 12))
        self.user_input.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.user_input.bind('<Return>', lambda event: self.send_message())
        
        self.send_button = ttk.Button(input_frame, text="Send", command=self.send_message)
        self.send_button.grid(row=0, column=1)

    def _create_status_bar(self, parent):
        """Creates the status bar at the bottom."""
        self.status_var = tk.StringVar()
        self.status_var.set("✅ Ready - Type your message and press Enter")
        status_bar = ttk.Label(
            parent,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2)
        )
        status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

    def _configure_styles(self):
        """Configures the text tags for styling the chat display."""
        self.chat_display.tag_configure("user_label", foreground="#1a5276", font=('Arial', 11, 'bold'))
        self.chat_display.tag_configure("user_msg", foreground="#2c3e50", font=('Arial', 11))
        self.chat_display.tag_configure("ai_label", foreground="#27ae60", font=('Arial', 11, 'bold'))
        self.chat_display.tag_configure("ai_msg", foreground="#34495e", font=('Arial', 11))
        self.chat_display.tag_configure("system", foreground="#e74c3c", font=('Arial', 11, 'italic'))
    
    def send_message(self):
        """Handle message sending"""
        user_text = self.user_input.get().strip()
        if not user_text:
            return
        
        self.user_input.delete(0, tk.END)
        self.display_message("You", user_text, "user")
        
        self.send_button.config(state=tk.DISABLED)
        self.status_var.set("🔍 Gemini is thinking...")
        
        thread = threading.Thread(target=self.process_enhanced_message, args=(user_text,))
        thread.daemon = True
        thread.start()
    
    def process_enhanced_message(self, user_text):
        """Process message with enhanced capabilities"""
        try:
            # Sending the user text directly is faster and usually sufficient
            response = self.chat.send_message(user_text)
            self.root.after(0, self.display_ai_response, response.text)

        except Exception as e:
            self.root.after(0, self.display_error, f"Error: {str(e)}")
    
    def display_message(self, sender, message, msg_type="ai"):
        """Display formatted message"""
        self.chat_display.config(state=tk.NORMAL)
        
        timestamp = tk.StringVar()
        
        if msg_type == "user":
            self.chat_display.insert(tk.END, f"👤 {sender}: ", "user_label")
            self.chat_display.insert(tk.END, f"{message}\n\n", "user_msg")
        else:
            self.chat_display.insert(tk.END, f"🤖 {sender}: ", "ai_label")
            self.chat_display.insert(tk.END, f"{message}\n\n", "ai_msg")
        
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def display_ai_response(self, response_text):
        """Display AI response"""
        self.display_message("Gemini AI", response_text, "ai")
        self.status_var.set("✅ Ready - Type your message and press Enter")
        self.send_button.config(state=tk.NORMAL)
    
    def display_error(self, error_msg):
        """Display error"""
        self.display_message("System", error_msg, "ai")
        self.display_message("System", error_msg, "system")
        self.status_var.set("❌ Error occurred")
        self.send_button.config(state=tk.NORMAL)
        
    def clear_chat(self):
        """Clears the chat display and resets the conversation history."""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # Reset the backend chat session
        self.chat = self.model.start_chat(history=[])
        self.status_var.set("✅ Chat cleared. Ready for a new conversation.")

def main(): # pragma: no cover
    """Run the enhanced chatbot"""
    root = tk.Tk()
    app = GeminiChatbot(root)
    
    # Configure text styles
    app.chat_display.tag_configure("user_label", foreground="#1a5276", font=('Arial', 11, 'bold'))
    app.chat_display.tag_configure("user_msg", foreground="#2c3e50", font=('Arial', 11))
    app.chat_display.tag_configure("ai_label", foreground="#27ae60", font=('Arial', 11, 'bold'))
    app.chat_display.tag_configure("ai_msg", foreground="#34495e", font=('Arial', 11))
    
    root.mainloop()


if __name__ == "__main__":
    main()