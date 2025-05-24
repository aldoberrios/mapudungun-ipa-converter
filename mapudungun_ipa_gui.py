#!/usr/bin/env python3

import tkinter as tk
from tkinter import messagebox  # For the About popup

# Ordered IPA mapping (longest matches first)
orthography_to_ipa = [
    ("ch", "t͡ʃ"), ("tr", "ʈ͡ʂ"), ("sh", "ʃ"), ("ng", "ŋ"), ("ll", "ʎ"),
    ("hu", "w"), ("qu", "k"), ("c", "k"),
    ("ñ", "ɲ"), ("g", "ɣ"), ("r", "ʐ"), ("d", "θ"),
    ("l'", "l̪"), ("n'", "n̪"), ("t'", "t̪"),
    ("ü", "ɨ"), ("ù", "ɨ"), ("ú", "ɨ"),
    ("a", "a"), ("e", "e"), ("i", "i"), ("o", "o"), ("u", "u"),
    ("p", "p"), ("t", "t"), ("k", "k"), ("f", "f"), ("s", "s"),
    ("m", "m"), ("n", "n"), ("l", "l"), ("w", "w"), ("y", "j")
]

def normalize_apostrophes(word):
    return word.replace("’", "'")

def convert_to_ipa(word):
    result = ""
    i = 0
    while i < len(word):
        matched = False
        for src, ipa in orthography_to_ipa:
            if word[i:i+len(src)] == src:
                result += ipa
                i += len(src)
                matched = True
                break
        if not matched:
            result += word[i]
            i += 1
    return result

def on_typing(event=None):
    input_text.edit_modified(False)  # Reset the modified flag
    word = normalize_apostrophes(input_text.get("1.0", tk.END).strip().lower())
    ipa = convert_to_ipa(word)
    output_text.config(state='normal')
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, ipa)
    output_text.config(state='disabled')

def copy_to_clipboard():
    root.clipboard_clear()
    root.clipboard_append(output_text.get("1.0", tk.END).strip())
    root.update()

def select_all_input(event):
    input_text.tag_add("sel", "1.0", "end-1c")
    return "break"  # prevent default behavior

def handle_input_modified(event=None):
    update_status()
    on_typing()
    return "break"

def show_about():
    messagebox.showinfo("About", "Mapudungun → IPA Converter\n\nCreated by Aldo Berríos\nVersion 1.0")

def show_mapping_table():
    popup = tk.Toplevel(root)
    popup.title("IPA Mapping Table")
    popup.geometry("450x250")
    tk.Label(popup, text="Orthography → IPA", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=4, pady=5)

    total = len(orthography_to_ipa)
    chunk = (total + 2) // 3
    col1 = orthography_to_ipa[:chunk]
    col2 = orthography_to_ipa[chunk:2*chunk]
    col3 = orthography_to_ipa[2*chunk:]

    text1 = tk.Text(popup, width=20, font=("Courier", 10))
    text2 = tk.Text(popup, width=20, font=("Courier", 10))
    text3 = tk.Text(popup, width=20, font=("Courier", 10))

    text1.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=(0, 10))
    text2.grid(row=1, column=1, sticky="nsew", padx=5, pady=(0, 10))
    text3.grid(row=1, column=2, sticky="nsew", padx=5, pady=(0, 10))

    scrollbar = tk.Scrollbar(popup)
    scrollbar.grid(row=1, column=3, sticky="ns", padx=(0, 10), pady=(0, 10))

    def yview(*args):
        text1.yview(*args)
        text2.yview(*args)
        text3.yview(*args)
    text1.config(yscrollcommand=scrollbar.set)
    text2.config(yscrollcommand=scrollbar.set)
    text3.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=yview)

    for src, ipa in col1:
        text1.insert(tk.END, f"{src:>6} → {ipa}\n")
    for src, ipa in col2:
        text2.insert(tk.END, f"{src:>6} → {ipa}\n")
    for src, ipa in col3:
        text3.insert(tk.END, f"{src:>6} → {ipa}\n")

    text1.config(state='disabled')
    text2.config(state='disabled')
    text3.config(state='disabled')

    popup.grid_rowconfigure(1, weight=1)
    popup.grid_columnconfigure(0, weight=1)
    popup.grid_columnconfigure(1, weight=1)
    popup.grid_columnconfigure(2, weight=1)

# Counts
def update_status(event=None):
    text = input_text.get("1.0", tk.END).strip()
    lines = text.count('\n') + 1 if text else 0
    words = len(text.split())
    chars = len(text)
    status_var.set(f"Lines: {lines} | Words: {words} | Characters: {chars}")
    input_text.edit_modified(False)


# GUI Setup
root = tk.Tk()
root.title("Mapudungun → IPA Converter")

# Menu bar
menu_bar = tk.Menu(root)

# File menu
file_menu = tk.Menu(menu_bar, tearoff=0)
def clear_fields():
    input_text.delete("1.0", tk.END)
    output_text.config(state='normal')
    output_text.delete("1.0", tk.END)
    output_text.config(state='disabled')
file_menu.add_command(label="Clear Input/Output", command=clear_fields)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu)

# View menu
view_menu = tk.Menu(menu_bar, tearoff=0)
view_menu.add_command(label="Show IPA Mapping Table", command=show_mapping_table)
menu_bar.add_cascade(label="View", menu=view_menu)

# Help menu
help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="About", command=show_about)
menu_bar.add_cascade(label="Help", menu=help_menu)

root.config(menu=menu_bar)

# Label
tk.Label(root, text="Enter Mapudungun word(s):").pack(pady=5)

# Multiline Input with scrollbar
input_frame = tk.Frame(root)
input_frame.pack(padx=10, pady=5, fill="both", expand=False)

input_scrollbar = tk.Scrollbar(input_frame)
input_scrollbar.pack(side="right", fill="y")

input_text = tk.Text(input_frame, height=4, width=40, font=("Arial", 14),
                     wrap="word", yscrollcommand=input_scrollbar.set)
input_text.pack(side="left", fill="both", expand=True)
input_scrollbar.config(command=input_text.yview)

input_text.bind("<<Modified>>", on_typing)
input_text.bind("<Control-a>", select_all_input)
input_text.bind("<Control-A>", select_all_input)  # handles uppercase A too

input_text.bind("<<Modified>>", handle_input_modified)

# Output with scrollbar
output_frame = tk.Frame(root)
output_frame.pack(padx=10, pady=5, fill="both", expand=False)

output_scrollbar = tk.Scrollbar(output_frame)
output_scrollbar.pack(side="right", fill="y")

output_text = tk.Text(output_frame, height=4, width=40, font=("Arial", 14),
                      wrap="word", yscrollcommand=output_scrollbar.set)
output_text.pack(side="left", fill="both", expand=True)
output_scrollbar.config(command=output_text.yview)

output_text.config(state='disabled')

# Button
tk.Button(root, text="Copy to Clipboard", command=copy_to_clipboard).pack(pady=5)

# Live status bar
status_var = tk.StringVar()
status_label = tk.Label(root, textvariable=status_var, font=("Arial", 10), fg="gray")
status_label.pack(pady=(0, 5))


root.mainloop()
