import os
from datetime import datetime

def scan_directory(path="."):
    rows = []

    for root, dirs, files in os.walk(path):
        # 🔥 This is the key line: prevents entering .git folder
        if ".git" in dirs:
            dirs.remove(".git")

        for name in dirs + files:
            full_path = os.path.join(root, name)
            is_file = os.path.isfile(full_path)

            size = os.path.getsize(full_path) if is_file else "-"
            modified_time = datetime.fromtimestamp(
                os.path.getmtime(full_path)
            ).strftime("%Y-%m-%d %H:%M:%S")

            rows.append({
                "Name": name,
                "Type": "File" if is_file else "Folder",
                "Size (bytes)": size,
                "Modified": modified_time,
                "Path": full_path
            })

    return rows


def print_table(data):
    headers = ["Name", "Type", "Size (bytes)", "Modified", "Path"]
    
    col_widths = {
        h: max(len(str(row[h])) for row in data + [{h: h}])
        for h in headers
    }

    header_row = " | ".join(h.ljust(col_widths[h]) for h in headers)
    print(header_row)
    print("-" * len(header_row))

    for row in data:
        print(" | ".join(str(row[h]).ljust(col_widths[h]) for h in headers))


if __name__ == "__main__":
    data = scan_directory(".")
    print_table(data)