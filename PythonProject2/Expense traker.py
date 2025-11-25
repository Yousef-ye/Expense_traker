import csv
import os
from datetime import date
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# ------------------------------
# Expense Tracker (Tkinter + CSV)
# ------------------------------

class ExpenseTracker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Expense Tracker")
        self.geometry("840x560")
        self.minsize(780, 520)

        # Data storage: list of dicts: {"date": str, "category": str, "description": str, "amount": float}
        self.expenses = []

        self._build_ui()
        self._configure_tree_sorting()
        self.update_total()

    # ---------- UI ----------
    def _build_ui(self):
        # Top frame: form inputs
        form = ttk.LabelFrame(self, text="Add Expense")
        form.pack(fill="x", padx=10, pady=10)

        # Date
        ttk.Label(form, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        self.date_var = tk.StringVar(value=str(date.today()))
        date_entry = ttk.Entry(form, textvariable=self.date_var, width=16)
        date_entry.grid(row=0, column=1, sticky="w", padx=8, pady=6)

        # Category
        ttk.Label(form, text="Category:").grid(row=0, column=2, sticky="w", padx=8, pady=6)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(form, textvariable=self.category_var, width=18, state="readonly")
        self.category_combo["values"] = ("Food", "Transport", "Bills", "Rent", "Health", "Education", "Shopping", "Entertainment", "Other")
        self.category_combo.grid(row=0, column=3, sticky="w", padx=8, pady=6)
        self.category_combo.set("Food")

        # Description
        ttk.Label(form, text="Description:").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        self.desc_var = tk.StringVar()
        desc_entry = ttk.Entry(form, textvariable=self.desc_var, width=40)
        desc_entry.grid(row=1, column=1, columnspan=3, sticky="we", padx=8, pady=6)

        # Amount
        ttk.Label(form, text="Amount:").grid(row=2, column=0, sticky="w", padx=8, pady=6)
        self.amount_var = tk.StringVar()
        amount_entry = ttk.Entry(form, textvariable=self.amount_var, width=16)
        amount_entry.grid(row=2, column=1, sticky="w", padx=8, pady=6)

        # Buttons
        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=2, column=2, columnspan=2, sticky="e", padx=8, pady=6)
        add_btn = ttk.Button(btn_frame, text="Add", command=self.add_expense)
        add_btn.pack(side="left", padx=4)
        clear_btn = ttk.Button(btn_frame, text="Clear", command=self.clear_form)
        clear_btn.pack(side="left", padx=4)

        # Middle frame: table + actions
        table_frame = ttk.LabelFrame(self, text="Expenses")
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0,10))

        # Treeview
        columns = ("date", "category", "description", "amount")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.heading("date", text="Date")
        self.tree.heading("category", text="Category")
        self.tree.heading("description", text="Description")
        self.tree.heading("amount", text="Amount")
        self.tree.column("date", width=110, anchor="center")
        self.tree.column("category", width=130, anchor="w")
        self.tree.column("description", width=380, anchor="w")
        self.tree.column("amount", width=100, anchor="e")
        self.tree.pack(fill="both", expand=True, side="left")

        # Scrollbar
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scroll.set)
        scroll.pack(fill="y", side="right")

        # Bottom bar: total + actions
        bottom = ttk.Frame(self)
        bottom.pack(fill="x", padx=10, pady=(0,10))

        self.total_var = tk.StringVar(value="Total: 0.00")
        total_label = ttk.Label(bottom, textvariable=self.total_var, font=("Segoe UI", 10, "bold"))
        total_label.pack(side="left")

        actions = ttk.Frame(bottom)
        actions.pack(side="right")

        save_btn = ttk.Button(actions, text="Save CSV", command=self.save_csv)
        save_btn.pack(side="left", padx=4)
        load_btn = ttk.Button(actions, text="Load CSV", command=self.load_csv)
        load_btn.pack(side="left", padx=4)
        delete_btn = ttk.Button(actions, text="Delete selected", command=self.delete_selected)
        delete_btn.pack(side="left", padx=4)

    def _configure_tree_sorting(self):
        # Attach sort per column
        for col in ("date", "category", "description", "amount"):
            self.tree.heading(col, command=lambda c=col: self._sort_by_column(c, False))

    # ---------- Actions ----------
    def add_expense(self):
        d = self.date_var.get().strip()
        cat = self.category_var.get().strip()
        desc = self.desc_var.get().strip()
        amt_str = self.amount_var.get().strip()

        # Validate
        if not d or not cat or not desc or not amt_str:
            messagebox.showwarning("Missing data", "Please fill all fields.")
            return
        try:
            amt = float(amt_str)
            if amt <= 0:
                raise ValueError("Amount must be positive.")
        except Exception:
            messagebox.showerror("Invalid amount", "Please enter a valid positive number for amount.")
            return

        # Optional: validate date format YYYY-MM-DD
        if not self._validate_date(d):
            messagebox.showerror("Invalid date", "Date must be in format YYYY-MM-DD.")
            return

        # Store and display
        record = {"date": d, "category": cat, "description": desc, "amount": amt}
        self.expenses.append(record)
        self.tree.insert("", "end", values=(d, cat, desc, f"{amt:.2f}"))
        self.update_total()
        self.clear_form(focus=False)

    def clear_form(self, focus=True):
        self.desc_var.set("")
        self.amount_var.set("")
        if focus:
            # Focus description for faster entry
            self.focus_set()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("No selection", "Please select a row to delete.")
            return
        # Delete from data and UI
        for item_id in selected:
            vals = self.tree.item(item_id, "values")
            # Find matching record (first occurrence)
            for i, r in enumerate(self.expenses):
                if (r["date"] == vals[0] and r["category"] == vals[1] and
                    r["description"] == vals[2] and f"{r['amount']:.2f}" == vals[3]):
                    self.expenses.pop(i)
                    break
            self.tree.delete(item_id)
        self.update_total()

    def update_total(self):
        total = sum(r["amount"] for r in self.expenses)
        self.total_var.set(f"Total: {total:.2f}")

    def save_csv(self):
        if not self.expenses:
            messagebox.showinfo("Nothing to save", "No expenses to save.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save expenses to CSV"
        )
        if not file_path:
            return
        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["date", "category", "description", "amount"])
                for r in self.expenses:
                    writer.writerow([r["date"], r["category"], r["description"], f"{r['amount']:.2f}"])
            messagebox.showinfo("Saved", f"Saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error saving", str(e))

    def load_csv(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")],
            title="Load expenses from CSV"
        )
        if not file_path:
            return
        try:
            with open(file_path, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                loaded = []
                for row in reader:
                    # normalize
                    d = (row.get("date") or "").strip()
                    cat = (row.get("category") or "").strip()
                    desc = (row.get("description") or "").strip()
                    amt_str = (row.get("amount") or "").strip()
                    if not d or not cat or not desc or not amt_str:
                        continue
                    if not self._validate_date(d):
                        continue
                    try:
                        amt = float(amt_str)
                    except:
                        continue
                    loaded.append({"date": d, "category": cat, "description": desc, "amount": amt})

            # Replace current data
            self.expenses = loaded
            # Refresh tree
            for item in self.tree.get_children():
                self.tree.delete(item)
            for r in self.expenses:
                self.tree.insert("", "end", values=(r["date"], r["category"], r["description"], f"{r['amount']:.2f}"))
            self.update_total()
            messagebox.showinfo("Loaded", f"Loaded {len(self.expenses)} records.")
        except Exception as e:
            messagebox.showerror("Error loading", str(e))

    def _sort_by_column(self, col, descending):
        # Get data to sort
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        # Convert amount to float for correct sorting
        if col == "amount":
            data.sort(key=lambda t: float(t[0]), reverse=descending)
        elif col == "date":
            data.sort(key=lambda t: t[0], reverse=descending)
        else:
            data.sort(key=lambda t: t[0].lower(), reverse=descending)
        # Rearrange items
        for index, (val, k) in enumerate(data):
            self.tree.move(k, "", index)
        # Toggle sort order on next click
        self.tree.heading(col, command=lambda: self._sort_by_column(col, not descending))

    @staticmethod
    def _validate_date(d):
        # Very light validation: YYYY-MM-DD
        parts = d.split("-")
        if len(parts) != 3:
            return False
        y, m, dd = parts
        if not (y.isdigit() and m.isdigit() and dd.isdigit()):
            return False
        try:
            _ = date(int(y), int(m), int(dd))
            return True
        except:
            return False


if __name__ == "__main__":
    app = ExpenseTracker()
    # Use native styling if available
    try:
        from ctypes import windll
        app.tk.call("tk", "scaling", 1.2)  # nicer scaling on high-DPI
    except:
        pass
    app.mainloop()