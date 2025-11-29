import csv
from datetime import date
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class ExpenseTracker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Expense Tracker")
        self.geometry("500x350")
        self.expenses = []
        
        # --- إدخالات ---
        form = ttk.Frame(self); form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Date:").grid(row=0, column=0)
        self.date_var = tk.StringVar(value=str(date.today()))
        ttk.Entry(form, textvariable=self.date_var, width=12).grid(row=0, column=1)

        ttk.Label(form, text="Category:").grid(row=0, column=2)
        self.cat_var = tk.StringVar()
        self.cat_box = ttk.Combobox(form, textvariable=self.cat_var, state="readonly",
                                    values=["Food","Transport","Bills","Rent","Health","Other"])
        self.cat_box.grid(row=0, column=3); self.cat_box.set("Food")

        ttk.Label(form, text="Desc:").grid(row=1, column=0)
        self.desc_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.desc_var, width=30).grid(row=1, column=1, columnspan=3)

        ttk.Label(form, text="Amount:").grid(row=2, column=0)
        self.amount_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.amount_var, width=12).grid(row=2, column=1)

        ttk.Button(form, text="Add", command=self.add_expense).grid(row=2, column=2)
        ttk.Button(form, text="Clear", command=self.clear_form).grid(row=2, column=3)

        # --- جدول ---
        cols = ("date","category","description","amount")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols: self.tree.heading(c, text=c.capitalize())
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # --- أسفل ---
        bottom = ttk.Frame(self); bottom.pack(fill="x", padx=10, pady=5)
        self.total_var = tk.StringVar(value="Total: 0.00")
        ttk.Label(bottom, textvariable=self.total_var).pack(side="left")
        ttk.Button(bottom, text="Save", command=self.save_csv).pack(side="right")
        ttk.Button(bottom, text="Load", command=self.load_csv).pack(side="right")
        ttk.Button(bottom, text="Delete", command=self.delete_selected).pack(side="right")

    # --- دوال ---
    def add_expense(self):
        try:
            amt = float(self.amount_var.get())
            if amt <= 0: raise ValueError
        except:
            messagebox.showerror("Error","Amount must be positive"); return
        rec = {"date":self.date_var.get(),"category":self.cat_var.get(),
               "description":self.desc_var.get(),"amount":amt}
        self.expenses.append(rec)
        self.tree.insert("", "end", values=(rec["date"],rec["category"],rec["description"],f"{amt:.2f}"))
        self.update_total(); self.clear_form()

    def clear_form(self):
        self.desc_var.set(""); self.amount_var.set("")

    def delete_selected(self):
        for item in self.tree.selection():
            vals = self.tree.item(item,"values")
            for i,r in enumerate(self.expenses):
                if (r["date"],r["category"],r["description"],f"{r['amount']:.2f}")==tuple(vals):
                    self.expenses.pop(i); break
            self.tree.delete(item)
        self.update_total()

    def update_total(self):
        self.total_var.set(f"Total: {sum(r['amount'] for r in self.expenses):.2f}")

    def save_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if not path: return
        with open(path,"w",newline="",encoding="utf-8") as f:
            w=csv.writer(f); w.writerow(["date","category","description","amount"])
            for r in self.expenses: w.writerow([r["date"],r["category"],r["description"],f"{r['amount']:.2f}"])

    def load_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files","*.csv")])
        if not path: return
        with open(path,"r",newline="",encoding="utf-8") as f:
            reader=csv.DictReader(f); self.expenses=[]
            for row in reader:
                try: amt=float(row["amount"])
                except: continue
                self.expenses.append({"date":row["date"],"category":row["category"],
                                      "description":row["description"],"amount":amt})
        for i in self.tree.get_children(): self.tree.delete(i)
        for r in self.expenses:
            self.tree.insert("", "end", values=(r["date"],r["category"],r["description"],f"{r['amount']:.2f}"))
        self.update_total()

if __name__=="__main__": ExpenseTracker().mainloop()