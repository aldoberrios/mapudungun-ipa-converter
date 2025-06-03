#!/usr/bin/env python3

import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter.filedialog import askopenfilename
from version import __version__

# ─────────────────────────────────────────────────────────────
# 🧩 IPA MAPPING DEFINITIONS
# ─────────────────────────────────────────────────────────────

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

ipa_map_ɨ = [("ü", "ɨ"), ("ù", "ɨ"), ("ú", "ɨ")]
ipa_map_ə = [("ü", "ə"), ("ù", "ə"), ("ú", "ə")]
ipa_map_ɯ = [("ü", "ɯ"), ("ù", "ɯ"), ("ú", "ɯ")]
ipa_map_sadowsky = [
    ("ü", "ɘ"), ("ù", "ɘ"), ("ú", "ɘ"), 
    ("i", "ɪ"), ("e", "ë"), ("a", "a̝"), 
    ("o", "ö"), ("u", "ʊ")
]

ipa_map_simple = [
    ("t͡ʃ", "ʧ"),  # U+02A7
    ("ʈ͡ʂ", "ŧ"),  # U+0167
    ("t̪", "ţ"),   # U+0163
    ("n̪", "ņ"),   # U+0146
    ("l̪", "ļ"),   # U+013C
]

def build_base_ipa_dict():
    return dict(orthography_to_ipa)

# ─────────────────────────────────────────────────────────────
# 🔁 TEXT CONVERSION FUNCTIONS
# ─────────────────────────────────────────────────────────────

def normalize_apostrophes(word):
    return word.replace("’", "'")

def convert_to_ipa(word):
    display = ipa_display_var.get()

    if display == "ɨ":
        suffix_map = dict(ipa_map_ɨ)
    elif display == "ə":
        suffix_map = dict(ipa_map_ə)
    elif display == "ɯ":
        suffix_map = dict(ipa_map_ɯ)
    elif display == "sadowsky":
        suffix_map = dict(ipa_map_sadowsky)
    else:
        suffix_map = {}

    ipa_dict = build_base_ipa_dict()
    ipa_dict.update({
        "r": r_display_var.get(),
        "g": g_display_var.get(),
        **suffix_map
    })

    # If simple IPA is active, apply substitutions at the end
    simple_mode = simple_ipa_var.get()

    # Conversion core
    max_len = max(len(k) for k in ipa_dict)
    result = ""
    i = 0
    while i < len(word):
        for j in range(max_len, 0, -1):
            chunk = word[i:i+j]
            if chunk in ipa_dict:
                result += ipa_dict[chunk]
                i += j
                break
        else:
            result += word[i]
            i += 1

    # Post-process for simple IPA
    if simple_mode:
        for k, v in ipa_map_simple:
            result = result.replace(k, v)

    return result

# ─────────────────────────────────────────────────────────────
# ✍️ INPUT/OUTPUT HANDLERS
# ─────────────────────────────────────────────────────────────

def on_typing(event=None):
    input_text.edit_modified(False)
    word = normalize_apostrophes(input_text.get("1.0", tk.END).strip().lower())
    ipa = convert_to_ipa(word)
    output_text.config(state='normal')
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, ipa)
    output_text.config(state='disabled')

def handle_input_modified(event=None):
    update_status()
    on_typing()
    return "break"

def update_status(event=None):
    text = input_text.get("1.0", tk.END).strip()
    status_var.set(f"Lines: {text.count(chr(10)) + 1} | Words: {len(text.split())} | Characters: {len(text)}")
    input_text.edit_modified(False)

def select_all(event=None):
    input_text.tag_add("sel", "1.0", "end-1c")
    return "break"

# ─────────────────────────────────────────────────────────────
# 📁 FILE OPERATIONS
# ─────────────────────────────────────────────────────────────

def copy_to_clipboard():
    root.clipboard_clear()
    root.clipboard_append(output_text.get("1.0", tk.END).strip())
    root.update()

def export_to_txt():
    output_value = output_text.get("1.0", tk.END).strip()
    if not output_value:
        messagebox.showwarning("No Output", "There is no IPA result to export.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(output_value)
        messagebox.showinfo("Saved", f"IPA output saved to:\n{file_path}")

def import_txt_file():
    filepath = askopenfilename(filetypes=[("Text files", "*.txt")])
    if not filepath:
        return
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read().strip()
            input_text.delete("1.0", tk.END)
            input_text.insert(tk.END, content)
            on_typing()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load file:\n{e}")

# ─────────────────────────────────────────────────────────────
# ⚙️ PREFERENCES & OPTIONS
# ─────────────────────────────────────────────────────────────

def reset_letter_options():
    ipa_display_var.set("ɨ")
    r_display_var.set("ʐ")
    g_display_var.set("ɣ")
    handle_input_modified()

def show_preferences():
    win = tk.Toplevel(root)
    win.title("Preferences")
    win.geometry("320x355")

    # ü Display
    tk.Label(win, text="ü Display", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky='w', padx=10, pady=(10, 0))
    for i, val in enumerate(["ɨ", "ə", "ɯ"]):
        tk.Radiobutton(win, text=val, variable=ipa_display_var, value=val, command=handle_input_modified)\
            .grid(row=1, column=i, sticky='w', padx=(10 if i == 0 else 5, 5))

    # r Display
    tk.Label(win, text="r Display", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky='w', padx=10, pady=(10, 0))
    for i, val in enumerate(["ʐ", "ɻ"]):
        tk.Radiobutton(win, text=val, variable=r_display_var, value=val, command=handle_input_modified)\
            .grid(row=3, column=i, sticky='w', padx=(10 if i == 0 else 5, 5))

    # g Display
    tk.Label(win, text="g Display", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky='w', padx=10, pady=(10, 0))
    for i, val in enumerate(["ɣ", "ɰ"]):
        tk.Radiobutton(win, text=val, variable=g_display_var, value=val, command=handle_input_modified)\
            .grid(row=5, column=i, sticky='w', padx=(10 if i == 0 else 5, 5))

    # Sadowsky Option
    tk.Label(win, text="Sadowsky et al, 2013", font=("Arial", 10, "bold"))\
        .grid(row=6, column=0, columnspan=2, sticky='w', padx=10, pady=(10, 0))
    tk.Radiobutton(win, text="ɘ ɪ ë a̝ ö ʊ", variable=ipa_display_var, value="sadowsky", command=handle_input_modified)\
        .grid(row=7, column=0, columnspan=2, sticky='w', padx=10)

    # Simple IPA Checkbox
    tk.Label(win, text="Additional Options", font=("Arial", 10, "bold"))\
        .grid(row=8, column=0, columnspan=2, sticky='w', padx=10, pady=(10, 0))
    tk.Checkbutton(win, text="Use Simple IPA substitutions", variable=simple_ipa_var,
                   command=handle_input_modified)\
        .grid(row=9, column=0, columnspan=3, sticky='w', padx=10)

    # Reset Button
    tk.Button(win, text="Reset to Defaults", command=reset_letter_options)\
        .grid(row=10, column=0, columnspan=3, pady=15, padx=10, sticky='w')

# ─────────────────────────────────────────────────────────────
# 🖼️ UI: SUPPORT / ABOUT / CHARTS
# ─────────────────────────────────────────────────────────────

def show_about():
    messagebox.showinfo("About", f"Mapudungun → IPA Converter\nCreated by Aldo Berríos\nVersion {__version__}")

def show_support_popup():
    help_win = tk.Toplevel(root)
    help_win.title("Support")
    help_win.geometry("350x450")

    text = (
        "📘 How to Use the Mapudungun → IPA Converter\n\n"
        "1. ✍️ Type Mapudungun word(s) in the upper text box.\n"
        "   → The corresponding IPA transcription appears below automatically.\n\n"
        "2. ⚙️ Use 'Options → Preferences' to:\n"
        "   • Choose the phonetic value of 'ü' (ɨ, ə, ɯ).\n"
        "   • Choose the IPA form for 'r' and 'g'.\n"
        "   • Apply the Sadowsky et al. (2013) vowel mapping.\n"
        "   • Choos 'Reset All Letter Options' to restore defaults.\n\n"
        "3. 📁 Use 'File' menu to:\n"
        "   • Import a .txt file with Mapudungun text.\n"
        "   • Export the IPA output to a .txt file.\n\n"
        "4. 📋 Use 'Copy to Clipboard' to copy the IPA output.\n"
        "   • Shortcut: Ctrl+A to select all input.\n\n"
        "5. 🧠 Use 'Help → IPA Chart' to view symbol mappings.\n"
        "   • Includes consonant and vowel tables.\n\n"
    )

    tk.Message(help_win, text=text, width=400, font=("Arial", 10), justify="left").pack(padx=10, pady=10)
    tk.Button(help_win, text="Close", command=help_win.destroy).pack(pady=(0, 10))

def show_ipa_chart():
    chart_win = tk.Toplevel(root)
    chart_win.title("IPA Chart (Simplified)")
    chart_win.geometry("540x500")

    tk.Label(chart_win, text="Simplified IPA Chart", font=("Arial", 12, "bold")).pack(pady=(10, 0))

    intro = "The following tables show the IPA symbols used in the conversion of Mapudungun orthography.\n"
    tk.Message(chart_win, text=intro, width=520, font=("Arial", 10)).pack(padx=10, pady=(10, 0))

    consonant_frame = tk.Frame(chart_win)
    consonant_frame.pack(pady=(10, 5))

    headers = ["", "Bilabial", "Dental", "Alveolar", "Palatal", "Retroflex", "Velar"]
    consonant_rows = [
        ("Stops",       ["p", "t̪", "t", "t͡ʃ", "ʈ͡ʂ", "k"]),
        ("Nasal",       ["m", "n̪", "n", "ɲ", "", "ŋ"]),
        ("Fricative",   ["f", "θ", "s", "ʃ", "ʐ", "ɣ"]),
        ("Approximant", ["w", "l̪", "", "j", "", ""])
    ]

    for col, text in enumerate(headers):
        tk.Label(consonant_frame, text=text, font=("Arial", 10, "bold"), borderwidth=1, relief="solid", padx=5, pady=3)\
            .grid(row=0, column=col, sticky="nsew")

    for row_idx, (label, symbols) in enumerate(consonant_rows, start=1):
        tk.Label(consonant_frame, text=label, font=("Arial", 10, "bold"), borderwidth=1, relief="solid", padx=5, pady=3)\
            .grid(row=row_idx, column=0, sticky="nsew")
        for col_idx, symbol in enumerate(symbols, start=1):
            tk.Label(consonant_frame, text=symbol, font=("Arial", 10), borderwidth=1, relief="solid", padx=5, pady=3)\
                .grid(row=row_idx, column=col_idx, sticky="nsew")

    outro = "\nNote that some orthographic symbols correspond to different IPA forms depending on user settings."
    tk.Message(chart_win, text=outro, width=520, font=("Arial", 10)).pack(padx=10, pady=(10, 0))

    vowel_frame = tk.Frame(chart_win)
    vowel_frame.pack(pady=(6, 5))

    vowel_headers = ["", "Front", "Central", "Back"]
    vowel_rows = [("High", ["i", "ɨ", "u"]), ("Mid", ["e", "", "o"]), ("Low", ["", "a", ""])]

    for col, text in enumerate(vowel_headers):
        tk.Label(vowel_frame, text=text, font=("Arial", 10, "bold"), borderwidth=1, relief="solid", padx=5, pady=3)\
            .grid(row=0, column=col, sticky="nsew")

    for row_idx, (label, symbols) in enumerate(vowel_rows, start=1):
        tk.Label(vowel_frame, text=label, font=("Arial", 10, "bold"), borderwidth=1, relief="solid", padx=5, pady=3)\
            .grid(row=row_idx, column=0, sticky="nsew")
        for col_idx, symbol in enumerate(symbols, start=1):
            tk.Label(vowel_frame, text=symbol, font=("Arial", 10), borderwidth=1, relief="solid", padx=5, pady=3)\
                .grid(row=row_idx, column=col_idx, sticky="nsew")

import os

def show_changelog():
    # Get the path where the script is located
    base_dir = os.path.dirname(os.path.abspath(__file__))
    changelog_path = os.path.join(base_dir, "CHANGELOG.md")

    if not os.path.exists(changelog_path):
        messagebox.showerror("Error", "CHANGELOG.md file not found.")
        return

    with open(changelog_path, encoding="utf-8") as f:
        content = f.read()

    popup = tk.Toplevel(root)
    popup.title("Changelog")
    popup.geometry("600x500")

    frame = tk.Frame(popup)
    frame.pack(fill="both", expand=True)

    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side="right", fill="y")

    text_widget = tk.Text(frame, wrap="word", yscrollcommand=scrollbar.set, font=("Courier", 10))
    text_widget.insert("1.0", content)
    text_widget.config(state="disabled")
    text_widget.pack(side="left", fill="both", expand=True)

    scrollbar.config(command=text_widget.yview)

    tk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)

# ─────────────────────────────────────────────────────────────
# 🖼️ GUI SETUP
# ─────────────────────────────────────────────────────────────

root = tk.Tk()
root.title("Mapudungun → IPA Converter")
root.geometry("500x400")  # Width x Height in pixels

ipa_display_var = tk.StringVar(value="ɨ")
r_display_var = tk.StringVar(value="ʐ")
g_display_var = tk.StringVar(value="ɣ")
simple_ipa_var = tk.BooleanVar(value=False)

root.columnconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.rowconfigure(3, weight=1)

# Menu
menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Import from .txt", command=import_txt_file)
file_menu.add_command(label="Export to .txt", command=export_to_txt)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu)

options_menu = tk.Menu(menu_bar, tearoff=0)
options_menu.add_command(label="Preferences", command=show_preferences)
options_menu.add_command(label="Reset All Letter Options", command=reset_letter_options)
menu_bar.add_cascade(label="Options", menu=options_menu)

help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="About", command=show_about)
help_menu.add_command(label="Support", command=show_support_popup)
help_menu.add_command(label="IPA Chart", command=show_ipa_chart)
help_menu.add_command(label="Display Changelog", command=show_changelog)
menu_bar.add_cascade(label="Help", menu=help_menu)
root.config(menu=menu_bar)

# Widgets
tk.Label(root, text="Enter Mapudungun word(s):").grid(row=0, column=0, sticky="w", padx=10, pady=5)

input_text = tk.Text(root, height=4, font=("Arial", 14), wrap='word')
input_text.grid(row=1, column=0, sticky="nsew", padx=10)
input_text.bind("<<Modified>>", handle_input_modified)
input_text.bind("<Control-a>", select_all)

tk.Button(root, text="Select All", command=lambda: input_text.tag_add("sel", "1.0", "end-1c"))\
    .grid(row=2, column=0, sticky="e", padx=10, pady=(2, 5))

output_text = tk.Text(root, height=4, font=("Arial", 14), state='disabled', wrap='word')
output_text.grid(row=3, column=0, sticky="nsew", padx=10)

tk.Button(root, text="Copy to Clipboard", command=copy_to_clipboard)\
    .grid(row=4, column=0, sticky="e", padx=10, pady=(2, 5))

status_var = tk.StringVar()
status_label = tk.Label(root, textvariable=status_var, font=("Arial", 10), fg="gray")
status_label.grid(row=5, column=0, sticky="we", padx=10, pady=(0, 5))

# ─────────────────────────────────────────────────────────────
# 🚀 LAUNCH
# ─────────────────────────────────────────────────────────────

root.mainloop()
