import ast
from pathlib import Path


# to register a new complaint
def register_complaint():

    while True:
        name = input("Enter your Name: ")
        div = input("Enter your class and div: ")
        complaint = input("Enter your Complaint: ")

        t1 = str((name, div, complaint))
        with open('Complaints.txt', "a") as file:
            file.write(t1 + '\n')

        # complaints.append(t1)  # add complaint to the list
        print("\nComplaint registered successfully!\n")

        # Ask if the user wants to add another
        more = input("Do you want to register another complaint? (yes/no): ").strip().lower()
        if more != "yes":
            break

    # Show all complaints at the end
    print("\nAll Registered Complaints:")
    for c in complaints:
        print(c)

# to show existing complaints
def show_complaints(path="Complaints.txt"):
    text = Path(path).read_text(encoding="utf-8").strip()
    if not text:
        return []

    # Normalize: ensure commas between back-to-back tuples, then parse as a list
    normalized = text.replace(')\n(', '),(').replace(')(', '),(')
    try:
        data = ast.literal_eval('[' + normalized + ']')  # parse as list of tuples
    except (SyntaxError, ValueError) as e:
        raise RuntimeError(f"File not in expected tuple format: {e}")

    # Make sure items are tuples of strings
    complaints = [tuple(map(str, t)) for t in data]
    return complaints

complaints = show_complaints()


# Run the function
# register_complaint()
print(complaints)