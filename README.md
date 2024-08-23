# Auto Deck ID Manager for Anki

## Overview

**Auto Deck ID Manager** is an Anki add-on designed to automatically manage Deck IDs for notes. It ensures that each note has a unique Deck ID, which helps in maintaining an organized and efficient flow during the creation and review process. This add-on is particularly useful for users who want to maintain a specific order of cards within a deck, allowing for better management.

## Features

- **Automatic Deck ID Assignment**: Automatically assigns a unique Deck ID to notes when they are created.
- **Deck ID Reordering**: Reorders Deck IDs to ensure a logical sequence is maintained.
- **Deck ID Verification**: Verifies the existence of Deck IDs upon Anki startup and adds missing IDs.

## Installation

1. Download the add-on from the repository.
2. Place the add-on in your Anki add-ons directory.
3. Restart Anki to initialize the add-on.

## Usage

1. **Automatic Deck ID Assignment**: When you create a new note, the add-on automatically assigns a Deck ID based on the existing IDs within that deck.
2. **Startup Verification**: Upon launching Anki, the add-on will verify all notes for missing Deck IDs and automatically add them if necessary.
3. **Reordering Deck IDs**: You can reorder Deck IDs via the Anki browser context menu.

## Development

### Modules

- **deck_id_manager**: Handles all functions related to Deck ID management, including reordering, assigning, and verifying Deck IDs.
- **browser_id_manager**: Manages interactions within the Anki browser, including reordering and displaying cards with their Deck IDs.

### Initialization

Hooks are initialized during the startup of Anki to manage Deck IDs when notes are added or when Anki starts.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add some feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## Author

**Matheus Bento de Souza**

For any questions or support, feel free to contact me.

