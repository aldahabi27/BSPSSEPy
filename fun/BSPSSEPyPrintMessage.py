
# Define the font mapping for two lines
font_map = {
    "A": ["▄▀█", "█▀█"], "B": ["█▄▄", "█▄█"], "C": ["█▀▀", "█ "], "D": ["█▀▄", "█▄▀"],
    "E": ["█▀▀", "██▄"], "F": ["█▀▀", "█▀ "], "G": ["█▀▀", "█▄█"], "H": ["█ █", "█▀█"],
    "I": ["█", "█"], "J": ["  █", "█▄█"], "K": ["█▄▀", "█▀▄"], "L": ["█ ", "██▄"],
    "M": ["█▄█▄█", "█ █ █"], "N": ["█▄ █", "█ ▀█"], "O": ["█▀█", "█▄█"], "P": ["█▀█", "█▀▀"],
    "Q": ["█▀█", "▀█▀"], "R": ["█▀█", "█▀▄"], "S": ["█▀▀", " ▀█"], "T": ["▀█▀", " █ "],
    "U": ["█ █", "█▄█"], "V": ["█ █", "▀▄▀"], "W": ["█ █ █", "▀▄▀▄▀"], "X": ["▀▄▀", "█ █"],
    "Y": ["█ █", " █ "], "Z": ["▀▀█", "█▄█"], " ": ["  ", "  "],
    "0": ["█▀█", "█▄█"], "1": [" █ ", " █ "], "2": ["█▀█", "█▄▀"], "3": ["█▀█", " ▄█"],
    "4": ["█ █", "▀▀█"], "5": ["█▀▀", " ▄█"], "6": ["█▀▀", "█▄█"], "7": ["▀▀█", " █ "],
    "8": ["█▀█", "█▄█"], "9": ["█▀█", " ▄█"], "!": ["█", "█"], "@": ["█▀▄", "█▄▀"],
    "#": ["▄█▄", "▀█▀"], "$": ["▄█▄", "▀█▀"], "%": ["█▄ ", " ▄█"], "^": ["▀▄▀", "  "],
    "&": ["█▄█", "█▄█"], "*": ["▄▀▄", "▀▄▀"], "(": [" █", " █"], ")": ["█ ", "█ "],
    "-": ["  ", "▀▀"], "_": ["  ", "▄▄"], "=": ["▀▀", "▄▄"], "+": [" █ ", "▀█▀"],
    "{": [" █▀", " █▄"], "}": ["█▀ ", "█▄ "], "[": ["▀█", "▄█"], "]": ["█▀", "█▄"],
    "\\": ["█  ", " █ "], "/": ["  █", " █ "], "|": ["█", "█"], ":": [" █ ", " █ "],
    ";": [" █ ", " ▄ "], "\"": ["█ █", "   "], "'": [" █", "  "], "<": [" █▀", " █▄"],
    ">": ["█▀ ", "█▄ "], ",": ["  ", " ▄"], ".": ["  ", " █"], "?": ["█▀█", " █ "]
}

def print_message_in_font(message):
    """Prints the given message using the custom font with a space after each character."""
    top_line = []
    bottom_line = []

    # Process each character in the message
    for char in message:
        char = char.upper()  # Ensure case-insensitivity
        if char in font_map:
            top, bottom = font_map[char]
            top_line.append(top + " ")       # Add space after each top-line character
            bottom_line.append(bottom + " ")  # Add space after each bottom-line character
        else:
            top_line.append("   ")  # Space for unsupported characters
            bottom_line.append("   ")
    
    # Join and print the two lines
    print("".join(top_line))
    print("".join(bottom_line))

# # Example usage
# print_message_in_font("Hello, World!")
