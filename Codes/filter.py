import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

cleaned_df = None
filtered_df = None
unlabeled_df = None  # To store data with missing target_classification
file_path = None
data_type = None

# Observational Parameters
important_features_type1 = [
    "target_name", "target_classification", "s_ra", "s_dec", "calib_level", 
    "t_min", "t_exptime"
]

def upload_file():
    global file_path, data_type
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    
    if file_path:
        messagebox.showinfo("Success", "File uploaded successfully! Now click 'Clear CSV'.")
        detect_data_type()
    else:
        messagebox.showerror("Error", "No file selected!")

def detect_data_type():
    global file_path, data_type
    try:
        df = pd.read_csv(file_path, comment="#")
        columns = set(df.columns)

        if "target_classification" in columns:
            data_type = "Type 1"
            messagebox.showinfo("Data Type Detected", "Detected Type 1 dataset.")
        else:
            messagebox.showwarning("Unknown Format", "This CSV does not match known data types.")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to detect data type:\n{e}")

def clear_csv():
    global cleaned_df, file_path
    if not file_path:
        messagebox.showerror("Error", "Please upload a CSV file first!")
        return
    
    try:
        cleaned_df = pd.read_csv(file_path, comment="#")
        messagebox.showinfo("Success", "Comments removed! Click 'Filter CSV' to process data.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to process file:\n{e}")

def filter_csv():
    global cleaned_df, filtered_df, unlabeled_df
    if cleaned_df is None:
        messagebox.showerror("Error", "No cleaned data available! Click 'Clear CSV' first.")
        return

    try:
        # Ensure required columns are present
        columns_in_file = set(cleaned_df.columns)
        required_columns = set(important_features_type1)
        missing_columns = required_columns - columns_in_file

        if missing_columns:
            messagebox.showerror("Error", f"Missing columns: {', '.join(missing_columns)}")
            return

        df = cleaned_df.copy()
        
        # If target_classification doesn't exist, create it and mark as unlabeled
        if "target_classification" not in df.columns:
            df["target_classification"] = [f"un{i+1}" for i in range(len(df))]
            unlabeled_df = df[important_features_type1].copy()
            filtered_df = None
            messagebox.showinfo("Success", "Data labeled as 'un1', 'un2', ... since no classification was found.")
            return
        
        # If target_classification exists, handle both labeled and unlabeled
        df["target_classification"] = df["target_classification"].astype(str).str.replace(r"[; ]+", "-", regex=True)
        df.loc[df["target_classification"].str.lower() == "nan", "target_classification"] = ""
        
        labeled_data = df[df["target_classification"].str.strip() != ""].copy()
        unlabeled_data = df[df["target_classification"].str.strip() == ""].copy()

        # Assign unique labels to the unlabeled data
        unlabeled_data["target_classification"] = [f"un{i+1}" for i in range(len(unlabeled_data))]

        filtered_df = labeled_data[important_features_type1]
        unlabeled_df = unlabeled_data[important_features_type1]

        messagebox.showinfo("Success", "Data filtered and pseudo-labeled! Ready to save files.")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to filter data:\n{e}")
        
def save_file():
    global filtered_df, unlabeled_df
    if filtered_df is None or unlabeled_df is None:
        messagebox.showerror("Error", "No filtered data available! Click 'Filter CSV' first.")
        return
    
    save_path_filtered = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")], title="Save Labeled Data")
    if save_path_filtered:
        filtered_df.to_csv(save_path_filtered, index=False)
        
    save_path_unlabeled = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")], title="Save Unlabeled Data")
    if save_path_unlabeled:
        unlabeled_df.to_csv(save_path_unlabeled, index=False)
    
    messagebox.showinfo("Success", "Files saved successfully!")

# Tkinter GUI Setup
root = tk.Tk()
root.title("CSV Cleaner & Auto-Filter")
root.geometry("500x450")

button_style = {"font": ("Arial", 12, "bold"), "width": 18, "height": 2}

title_label = tk.Label(root, text="CSV Cleaner & Auto-Filter", font=("Arial", 18, "bold"))
title_label.pack(pady=15)

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Button(frame, text="📂 Upload CSV", command=upload_file, **button_style).grid(row=0, column=0, pady=5)
tk.Button(frame, text="🗑️ Clear CSV", command=clear_csv, **button_style).grid(row=1, column=0, pady=5)
tk.Button(frame, text="🔍 Filter CSV", command=filter_csv, **button_style).grid(row=2, column=0, pady=5)
tk.Button(frame, text="💾 Save CSV", command=save_file, **button_style).grid(row=3, column=0, pady=5)

root.mainloop()
