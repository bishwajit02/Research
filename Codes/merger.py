import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

merged_df = None

def merge_csv_files():
    global merged_df
    file_paths = filedialog.askopenfilenames(filetypes=[("CSV Files", "*.csv")])

    if not file_paths:
        messagebox.showerror("Error", "No files selected!")
        return

    try:
        # Read all CSVs and merge them
        dataframes = [pd.read_csv(file) for file in file_paths]
        merged_df = pd.concat(dataframes, ignore_index=True)  # Combine & reset index

        # Ensure 'target_classification' column exists
        if "target_classification" in merged_df.columns:
            # Fill missing target_classification values with "un1", "un2", etc.
            missing_classes = merged_df["target_classification"].isna()
            merged_df.loc[missing_classes, "target_classification"] = [
                f"un{i+1}" for i in range(missing_classes.sum())
            ]

            # Create a consistent classification mapping
            unique_classes = sorted(merged_df["target_classification"].unique())
            class_mapping = {cls: idx for idx, cls in enumerate(unique_classes)}

            # Assign classification_id based on the mapping
            merged_df["classification_id"] = merged_df["target_classification"].map(class_mapping)

        messagebox.showinfo("Success", f"{len(file_paths)} files merged successfully! Click 'Save CSV'.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to merge files:\n{e}")

def save_merged_file():
    global merged_df
    if merged_df is None:
        messagebox.showerror("Error", "No merged data available! Click 'Merge CSVs' first.")
        return

    save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if save_path:
        merged_df.to_csv(save_path, index=False)
        messagebox.showinfo("Success", f"Merged file saved to:\n{save_path}")
    else:
        messagebox.showerror("Error", "No file name specified!")

# Tkinter GUI Setup
root = tk.Tk()
root.title("CSV Merger with Classification ID")
root.geometry("500x350")
root.config(bg="#2C3E50")

# Button Styling
button_style = {
    "font": ("Arial", 12, "bold"),
    "bg": "#3498DB", 
    "fg": "white",
    "activebackground": "#2980B9",
    "activeforeground": "white",
    "relief": "raised",
    "width": 18,
    "height": 2
}

# Title Label
title_label = tk.Label(root, text="CSV Merger & Classifier", font=("Arial", 18, "bold"), fg="white", bg="#2C3E50")
title_label.pack(pady=15)

# Button Frame
frame = tk.Frame(root, bg="#2C3E50")
frame.pack(pady=10)

# Merge Button
btn_merge = tk.Button(frame, text="📂 Merge CSVs", command=merge_csv_files, **button_style)
btn_merge.grid(row=0, column=0, pady=5)

# Save Button
btn_save = tk.Button(frame, text="💾 Save Merged CSV", command=save_merged_file, **button_style)
btn_save.grid(row=1, column=0, pady=5)

root.mainloop()
