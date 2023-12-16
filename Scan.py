import socket
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from scapy.layers.inet import IP, TCP
from scapy.sendrecv import sr1


class NetworkScanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Scanner")

        self.target_ip_label = ttk.Label(root, text="Target IP(s):")
        self.target_ip_entry = ttk.Entry(root, width=30)
        self.target_ip_entry.insert(0, "192.168.1.1")  # Пример: "192.168.1.1,192.168.1.2"
        self.target_ips = []

        self.scan_button = ttk.Button(root, text="Scan", command=self.scan_network)

        self.result_text = tk.Text(root, height=10, width=50, state="disabled")

        self.save_button = ttk.Button(root, text="Save Results", command=self.save_results)
        self.save_format_label = ttk.Label(root, text="Save Format:")
        self.save_format_var = tk.StringVar()
        self.save_format_var.set("Text")
        self.save_format_menu = ttk.OptionMenu(root, self.save_format_var, "Text", "JSON", "CSV")

        self.security_options_label = ttk.Label(root, text="Security Options:")
        self.use_authentication_var = tk.BooleanVar()
        self.use_authentication_var.set(False)
        self.authentication_checkbox = ttk.Checkbutton(root, text="Use Authentication",
                                                       variable=self.use_authentication_var)

        self.target_ip_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.target_ip_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.scan_button.grid(row=1, column=0, columnspan=2, pady=10)
        self.result_text.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        self.save_button.grid(row=3, column=0, pady=5)
        self.save_format_label.grid(row=3, column=1, pady=5, sticky="e")
        self.save_format_menu.grid(row=3, column=1, pady=5, sticky="w")
        self.security_options_label.grid(row=4, column=0, columnspan=2, pady=5)
        self.authentication_checkbox.grid(row=5, column=0, columnspan=2, pady=5)

    def scan_network(self):
        self.target_ips = self.target_ip_entry.get().split(",")
        security_options = {
            "use_authentication": self.use_authentication_var.get(),
            # Добавьте другие параметры безопасности по мере необходимости.
        }

        result = self.perform_scan(self.target_ips, security_options)
        self.display_results(result)

    def perform_scan(self, target_ips, security_options):
        open_ports = []
        host_info = []

        for target_ip in target_ips:
            try:
                host_info.append(socket.gethostbyaddr(target_ip))
            except socket.herror:
                host_info.append(None)

            for port in range(1, 1025):
                packet = IP(dst=target_ip) / TCP(dport=port, flags="S")
                response = sr1(packet, timeout=1, verbose=0)

                if response and response.haslayer(TCP) and response[TCP].flags == 0x12:
                    open_ports.append((target_ip, port))

        return host_info, open_ports

    def get_service_info(self, port):
        # Реализуйте определение службы для указанного порта.
        # Например, можно использовать словарь с известными портами и их службами.
        service_dict = {
            80: "HTTP",
            443: "HTTPS",
            22: "SSH",
            # Добавьте другие порты и службы по мере необходимости.
        }
        return service_dict.get(port, "Unknown")

    def display_results(self, result):
        host_info, open_ports = result
        result_text_content = ""

        for i, info in enumerate(host_info):
            if info:
                result_text_content += f"\nHost information for {info[0]}: {info}\n"
            else:
                result_text_content += f"\nUnable to retrieve host information for {self.target_ips[i]}\n"

            result_text_content += "Open ports:\n"
            for target_ip, port in open_ports:
                if target_ip == self.target_ips[i]:
                    service_info = self.get_service_info(port)
                    result_text_content += f" - Port {port}: {service_info}\n"

        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result_text_content)
        self.result_text.config(state="disabled")

    def save_results(self):
        result = self.result_text.get(1.0, tk.END)

        save_format = self.save_format_var.get()
        file_extension = {"Text": "txt", "JSON": "json", "CSV": "csv"}.get(save_format, "txt")

        file_path = filedialog.asksaveasfilename(defaultextension=file_extension,
                                                 filetypes=[(f"{save_format} Files", f"*.{file_extension}")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(result)


if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkScanner(root)
    root.mainloop()
