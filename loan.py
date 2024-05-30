import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

client_counter = 1
clients = []
total_bank_profit = 0
monthly_profits_all_clients = []
bank_capital = 1_000_000_000  

def add_client():
    global client_counter, total_bank_profit
    if client_counter > 10:
        messagebox.showerror("Error", "Maximum number of clients reached (10)")
        return

    try:
        name = name_entry.get()
        loan_amount = float(loan_amount_entry.get())
        interest_rate = float(interest_rate_entry.get())
        loan_term = int(loan_term_entry.get())

        if new_interest_option_var.get() == 1:
            new_interest_level = float(new_interest_level_entry.get()) if new_interest_level_entry.get() else None
            start_month = int(start_month_entry.get()) if start_month_entry.get() else None
        else:
            new_interest_level = None
            start_month = None

        monthly_interest_rate = (interest_rate / 100) / 12
        monthly_payment = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** loan_term) / ((1 + monthly_interest_rate) ** loan_term - 1)

        result_text = f"Monthly payment is: {monthly_payment:.2f} MAD"
        result_label.config(text=result_text)

        total_cost, new_monthly_payment, total_interest, monthly_profits = generate_amortization_schedule(
            loan_amount, monthly_interest_rate, monthly_payment, loan_term, new_interest_level, start_month
        )

        total_cost_text = f"Total loan cost is: {total_cost:.2f} MAD"
        total_cost_label.config(text=total_cost_text)
        if new_interest_level is not None and start_month is not None:
            new_monthly_payment_text = f"Monthly payment after {start_month} months is: {new_monthly_payment:.2f} MAD"
            new_monthly_payment_label.config(text=new_monthly_payment_text)
        else:
            new_monthly_payment_label.config(text="")

        bank_profit_text = f"Bank profit is: {total_interest:.2f} MAD"
        bank_profit_label.config(text=bank_profit_text)

        total_bank_profit += total_interest
        total_bank_profit_text.set(f"Total bank profit is: {total_bank_profit:.2f} MAD")

        aggregate_monthly_profits(monthly_profits)
        
        client_info = (
            f"Client {client_counter}: Name: {name}, Loan Amount: {loan_amount}, Interest Rate: {interest_rate}, "
            f"Loan Term: {loan_term}, Monthly Payment: {monthly_payment:.2f}, Total Cost: {total_cost:.2f}, "
            f"Bank Profit: {total_interest:.2f}"
        )
        clients.append(client_info)
        client_counter += 1

        with open("clients.txt", "a") as file:
            file.write(client_info + "\n")

        results_frame.grid()

    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers")

def generate_amortization_schedule(loan_amount, monthly_interest_rate, monthly_payment, loan_term, new_interest_level, start_month):
    total_interest_before = 0
    total_interest_after = 0
    balance = loan_amount
    amortization_data = []
    monthly_profits = []
    new_monthly_payment = None

    for month in range(1, loan_term + 1):
        if new_interest_level is not None and start_month is not None and month >= start_month:
            if new_monthly_payment is None:
                new_balance = balance
                new_loan_term = loan_term - month + 1
                new_monthly_interest_rate = (new_interest_level / 100) / 12
                new_monthly_payment = new_balance * (new_monthly_interest_rate * (1 + new_monthly_interest_rate) ** new_loan_term) / ((1 + new_monthly_interest_rate) ** new_loan_term - 1)
            monthly_interest_rate = (new_interest_level / 100) / 12
            interest_payment = balance * monthly_interest_rate
            total_interest_after += interest_payment
            monthly_payment = new_monthly_payment
        else:
            interest_payment = balance * monthly_interest_rate
            total_interest_before += interest_payment
        
        principal_payment = monthly_payment - interest_payment
        balance -= principal_payment
        amortization_data.append((month, monthly_payment, principal_payment, interest_payment, balance))
        monthly_profits.append(interest_payment)

    display_amortization_table(amortization_data)

    total_cost = total_interest_before + total_interest_after + loan_amount
    total_interest = total_interest_before + total_interest_after

    return total_cost, new_monthly_payment, total_interest, monthly_profits

def display_amortization_table(amortization_data):
    for row in amortization_table.get_children():
        amortization_table.delete(row)

    for data in amortization_data:
        amortization_table.insert("", "end", values=data)

def aggregate_monthly_profits(monthly_profits):
    global monthly_profits_all_clients
    if not monthly_profits_all_clients:
        monthly_profits_all_clients = [0] * len(monthly_profits)
    for i, profit in enumerate(monthly_profits):
        if i < len(monthly_profits_all_clients):
            monthly_profits_all_clients[i] += profit
        else:
            monthly_profits_all_clients.append(profit)
    update_monthly_profits_listbox()

def update_monthly_profits_listbox():
    monthly_profits_listbox.delete(0, tk.END)
    for i, profit in enumerate(monthly_profits_all_clients):
        monthly_profits_listbox.insert(tk.END, f"Month {i + 1}: {profit:.2f} MAD")

def show_alltime_yearly_profits_window():
    try:
        years = int(simpledialog.askstring("Input", "Enter number of years:"))
    except (TypeError, ValueError):
        messagebox.showerror("Error", "Please enter a valid number of years")
        return

    clients_data = load_clients_data()

    profit_window = tk.Toplevel(root)
    profit_window.title("All-Time and Yearly Profits")
    profit_window.geometry("800x600")
    profit_window.configure(bg="#f0f0f0")

    yearly_profit_text = "Annual profits of all clients:\n"
    all_time_profit = 0
    current_bank_capital = bank_capital

    yearly_profit = 0
    yearly_profits = []
    capital_over_time = [bank_capital]

    for year in range(years):
        for client in clients_data:
            monthly_profits = client['monthly_profits']
            for i, profit in enumerate(monthly_profits[year * 12:(year + 1) * 12]):
                yearly_profit += profit
                all_time_profit += profit
                current_bank_capital += profit
                capital_over_time.append(current_bank_capital)
        yearly_profits.append(yearly_profit)
        yearly_profit_text += f"Year {year + 1}: {yearly_profit:.2f} MAD\n"
        yearly_profit = 0

    yearly_profit_label = tk.Label(profit_window, text=yearly_profit_text, font=("Helvetica", 8), bg="#f0f0f0", justify=tk.LEFT)
    all_time_profit_label = tk.Label(profit_window, text=f"Total all-time profit is: {all_time_profit:.2f} MAD", font=("Helvetica", 10, "bold"), bg="#f0f0f0", justify=tk.LEFT)

    yearly_profit_label.pack(pady=10)
    all_time_profit_label.pack(pady=10)

    years_list = list(range(1, years + 1))
    months = list(range(1, len(capital_over_time) + 1))
    fig, ax1 = plt.subplots()

    ax1.set_xlabel('Month')
    ax1.set_ylabel('Capital (MAD)', color='tab:blue')
    ax1.plot(months, capital_over_time, label='Bank Capital', color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    ax2 = ax1.twinx()
    ax2.set_ylabel('Yearly Profit (MAD)', color='tab:orange')
    ax2.plot(years_list, yearly_profits, label='Yearly Profits', color='tab:orange')
    ax2.tick_params(axis='y', labelcolor='tab:orange')

    fig.tight_layout()
    plt.title('Bank Capital and Yearly Profits Over Time')

    canvas = FigureCanvasTkAgg(fig, master=profit_window)
    canvas.draw()
    canvas.get_tk_widget().pack()

def show_bank_profit():
    try:
        years = int(simpledialog.askstring("Input", "Enter number of years:"))
    except (TypeError, ValueError):
        messagebox.showerror("Error", "Please enter a valid number of years")
        return

    clients_data = load_clients_data()

    profit_window = tk.Toplevel(root)
    profit_window.title("Bank Profit")
    profit_window.geometry("800x600")
    profit_window.configure(bg="#f0f0f0")

    all_time_profit = 0
    yearly_profits = 0
    monthly_profits_all_clients = [0] * (years * 12)
    for client in clients_data:
        monthly_profits = client['monthly_profits']
        for i in range(years * 12):
            if i < len(monthly_profits):
                monthly_profits_all_clients[i] += monthly_profits[i]
                all_time_profit += monthly_profits[i]
                if i < years * 12:
                    yearly_profits += monthly_profits[i]

    bank_profit_text = f"Total bank profit is: {all_time_profit:.2f} MAD"
    yearly_profit_text = f"Bank profit over {years} years is: {yearly_profits:.2f} MAD"
    monthly_profit_text = f"Average monthly bank profit is: {yearly_profits / (years * 12):.2f} MAD"

    bank_profit_label = tk.Label(profit_window, text=bank_profit_text, font=("Helvetica", 10, "bold"), bg="#f0f0f0", justify=tk.LEFT)
    yearly_profit_label = tk.Label(profit_window, text=yearly_profit_text, font=("Helvetica", 10, "bold"), bg="#f0f0f0", justify=tk.LEFT)
    monthly_profit_label = tk.Label(profit_window, text=monthly_profit_text, font=("Helvetica", 10, "bold"), bg="#f0f0f0", justify=tk.LEFT)

    bank_profit_label.pack(pady=10)
    yearly_profit_label.pack(pady=10)
    monthly_profit_label.pack(pady=10)

def toggle_amortization_schedule():
    if amortization_frame.winfo_ismapped():
        amortization_frame.grid_remove()
        show_amortization_button.config(text="Show Amortization Schedule")
    else:
        amortization_frame.grid()
        show_amortization_button.config(text="Hide Amortization Schedule")

def toggle_monthly_profits():
    try:
        years = int(simpledialog.askstring("Input", "Enter number of years:"))
    except (TypeError, ValueError):
        messagebox.showerror("Error", "Please enter a valid number of years")
        return

    clients_data = load_clients_data()
    monthly_profits_all_clients = [0] * (years * 12)
    for client in clients_data:
        monthly_profits = client['monthly_profits']
        for i in range(years * 12):
            if i < len(monthly_profits):
                monthly_profits_all_clients[i] += monthly_profits[i]

    monthly_profits_listbox.delete(0, tk.END)
    for i, profit in enumerate(monthly_profits_all_clients):
        monthly_profits_listbox.insert(tk.END, f"Month {i + 1}: {profit:.2f} MAD")

    if monthly_profits_listbox_frame.winfo_ismapped():
        monthly_profits_listbox_frame.grid_remove()
        show_monthly_profits_button.config(text="Show Monthly Profits")
    else:
        monthly_profits_listbox_frame.grid()
        show_monthly_profits_button.config(text="Hide Monthly Profits")

def show_all_clients():
    try:
        with open("clients.txt", "r") as file:
            clients_data = file.readlines()

        clients_window = tk.Toplevel(root)
        clients_window.title("All Clients")
        clients_window.geometry("600x400")
        clients_window.configure(bg="#f0f0f0")

        clients_text = tk.Text(clients_window, font=("Helvetica", 10), wrap=tk.WORD)
        clients_text.pack(expand=True, fill=tk.BOTH)
        clients_text.insert(tk.END, ''.join(clients_data))

    except FileNotFoundError:
        messagebox.showerror("Error", "The file clients.txt was not found")

def load_clients_data():
    clients_data = []
    try:
        with open("clients.txt", "r") as file:
            for line in file:
                parts = line.split(", ")
                loan_amount = float(parts[1].split(": ")[1])
                interest_rate = float(parts[2].split(": ")[1])
                loan_term = int(parts[3].split(": ")[1])
                monthly_payment = float(parts[4].split(": ")[1])
                monthly_interest_rate = (interest_rate / 100) / 12
                total_cost, new_monthly_payment, total_interest, monthly_profits = generate_amortization_schedule(
                    loan_amount, monthly_interest_rate, monthly_payment, loan_term, None, None
                )
                clients_data.append({'monthly_profits': monthly_profits})
    except FileNotFoundError:
        messagebox.showerror("Error", "The file clients.txt was not found")
    return clients_data

root = tk.Tk()
root.title("Bank Application By Younes BENELHOMS")
root.geometry("1200x600")
root.configure(bg="#f0f0f0")

header_label = tk.Label(root, text="Bank Application By YOUNES BENELHOMS", font=("Helvetica", 16, "bold"), bg="#d00013", fg="white")
header_label.grid(row=0, column=0, columnspan=4, pady=10)

client_frame = tk.LabelFrame(root, text="Client Information", font=("Helvetica", 12, "bold"), bg="#f0f0f0", padx=10, pady=10)
client_frame.grid(row=1, column=0, padx=10, pady=10, sticky="n")

def create_label_entry(frame, label_text, row):
    label = tk.Label(frame, text=label_text, font=("Helvetica", 10), bg="#f0f0f0")
    entry = tk.Entry(frame, font=("Helvetica", 10))
    label.grid(row=row, column=0, padx=5, pady=5, sticky=tk.E)
    entry.grid(row=row, column=1, padx=5, pady=5)
    return entry

name_entry = create_label_entry(client_frame, "Name:", 0)
loan_amount_entry = create_label_entry(client_frame, "Loan Amount (MAD):", 1)
interest_rate_entry = create_label_entry(client_frame, "Annual Interest Rate (%):", 2)
loan_term_entry = create_label_entry(client_frame, "Loan Term (months):", 3)

new_interest_option_var = tk.IntVar()
new_interest_option_checkbutton = tk.Checkbutton(client_frame, text="Enable New Interest Option", variable=new_interest_option_var, font=("Helvetica", 10), bg="#f0f0f0", command=lambda: toggle_new_interest_option(new_interest_option_var.get()))
new_interest_option_checkbutton.grid(row=4, column=0, columnspan=2, pady=5)

new_interest_level_entry = create_label_entry(client_frame, "New Interest Level (%):", 5)
start_month_entry = create_label_entry(client_frame, "Start Month of New Interest:", 6)

def toggle_new_interest_option(enabled):
    state = tk.NORMAL if enabled else tk.DISABLED
    new_interest_level_entry.config(state=state)
    start_month_entry.config(state=state)

toggle_new_interest_option(0)

add_client_button = tk.Button(client_frame, text="Add Client", font=("Helvetica", 10, "bold"), bg="#d00013", fg="white", command=add_client)
add_client_button.grid(row=7, column=0, columnspan=2, pady=10)

nav_frame = tk.Frame(root, bg="#f0f0f0")
nav_frame.grid(row=1, column=1, padx=10, pady=10, sticky="n")

show_alltime_yearly_profits_button = tk.Button(nav_frame, text="Show All-Time & Yearly Profits", font=("Helvetica", 10, "bold"), bg="#2196F3", fg="white", command=show_alltime_yearly_profits_window)
show_bank_profit_button = tk.Button(nav_frame, text="View Bank Profit", font=("Helvetica", 10, "bold"), bg="#FFC107", fg="black", command=show_bank_profit)
show_amortization_button = tk.Button(nav_frame, text="Show Amortization Schedule", font=("Helvetica", 10, "bold"), bg="#9C27B0", fg="white", command=toggle_amortization_schedule)
show_monthly_profits_button = tk.Button(nav_frame, text="Show Monthly Profits", font=("Helvetica", 10, "bold"), bg="#FF5722", fg="white", command=toggle_monthly_profits)
show_clients_button = tk.Button(nav_frame, text="Show All Clients", font=("Helvetica", 10, "bold"), bg="#3F51B5", fg="white", command=show_all_clients)

show_alltime_yearly_profits_button.pack(pady=5)
show_bank_profit_button.pack(pady=5)
show_amortization_button.pack(pady=5)
show_monthly_profits_button.pack(pady=5)
show_clients_button.pack(pady=5)

results_frame = tk.LabelFrame(root, text="Results", font=("Helvetica", 12, "bold"), bg="#f0f0f0", padx=10, pady=10)
results_frame.grid(row=1, column=2, padx=10, pady=10, sticky="n")
results_frame.grid_remove()

result_label = tk.Label(results_frame, text="", font=("Helvetica", 10, "bold"), bg="#f0f0f0")
total_cost_label = tk.Label(results_frame, text="", font=("Helvetica", 10, "bold"), bg="#f0f0f0")
new_monthly_payment_label = tk.Label(results_frame, text="", font=("Helvetica", 10, "bold"), bg="#f0f0f0")
bank_profit_label = tk.Label(results_frame, text="", font=("Helvetica", 10, "bold"), bg="#f0f0f0")
total_bank_profit_text = tk.StringVar()
total_bank_profit_label = tk.Label(results_frame, textvariable=total_bank_profit_text, font=("Helvetica", 10, "bold"), bg="#f0f0f0")

result_label.grid(row=0, column=0, pady=5)
total_cost_label.grid(row=1, column=0, pady=5)
new_monthly_payment_label.grid(row=2, column=0, pady=5)
total_bank_profit_label.grid(row=3, column=0, pady=5)

amortization_frame = tk.LabelFrame(root, text="Amortization Schedule", font=("Helvetica", 12, "bold"), bg="#f0f0f0", padx=10, pady=10)
amortization_frame.grid(row=2, column=2, padx=10, pady=10, sticky="n")
amortization_frame.grid_remove()

columns = ("Month", "Payment", "Principal", "Interest", "Balance")
amortization_table = ttk.Treeview(amortization_frame, columns=columns, show="headings")
for col in columns:
    amortization_table.heading(col, text=col)
    amortization_table.column(col, anchor="center", width=80)

amortization_table.pack(fill="both", expand=True)

monthly_profits_listbox_frame = tk.LabelFrame(root, text="Monthly Profits", font=("Helvetica", 12, "bold"), bg="#f0f0f0", padx=10, pady=10)
monthly_profits_listbox_frame.grid(row=3, column=2, padx=10, pady=10, sticky="n")
monthly_profits_listbox_frame.grid_remove()

scrollbar = tk.Scrollbar(monthly_profits_listbox_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

monthly_profits_listbox = tk.Listbox(monthly_profits_listbox_frame, font=("Helvetica", 10), yscrollcommand=scrollbar.set)
monthly_profits_listbox.pack(pady=10, fill=tk.BOTH, expand=True)
scrollbar.config(command=monthly_profits_listbox.yview)

for widget in client_frame.winfo_children():
    widget.grid_configure(padx=5, pady=5)

root.mainloop()
