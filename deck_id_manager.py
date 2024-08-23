
"""
Anki Add-on: Auto Deck ID Manager

This script automatically manages Deck IDs for notes within Anki. The Deck IDs
are assigned in the format 'Deck_Name@00000' and ensure each note in a deck has
a unique identifier. The script provides functionalities to:

1. Automatically assign a Deck ID to new notes when they are added.
2. Reorder existing Deck IDs in a deck to ensure continuity and correct ordering.
3. Verify and correct missing or malformed Deck IDs upon Anki startup.
4. Update Deck IDs for notes in a deck based on the highest existing index.

Functions:
- reorder_deck_ids(deck_id): Reorders Deck IDs within a specified deck.
- get_max_deck_index(deck_id): Retrieves the highest Deck ID in a deck.
- add_deck_index_field(note, deck_id): Assigns a new Deck ID to a note.
- add_deck_on_profile(note, deck_id): Adds or replaces the Deck ID in a note.
- verify_and_add_deck_ids(): Verifies and adds missing Deck IDs at startup.
- on_note_will_be_added(col, note, deck_id): Hook to add Deck ID when a note is created.
- on_profile_did_open(): Hook to verify and add Deck IDs when Anki starts.

Hooks:
- note_will_be_added: Triggers before a new note is added to Anki, ensuring it has a Deck ID.
- profile_did_open: Triggers when Anki starts, verifying all notes have valid Deck IDs.

Author: Matheus Bento de Souza
Date: August 2024
"""

from aqt import mw, gui_hooks
from aqt.qt import QAction
from anki.notes import Note
from anki.hooks import note_will_be_added
from aqt.utils import QMessageBox

# Function to display a message after a delay
def show_message_later(message):
    msg_box = QMessageBox()
    msg_box.setText(message)
    msg_box.setWindowTitle("Warning")
    msg_box.exec()

# Function to reorder the Deck IDs within a specific deck
def reorder_deck_ids(deck_id):
    print(f"Reordering Deck IDs for deck_id: {deck_id}")
    
    all_cards = mw.col.decks.cids(deck_id, children=False)
    print(f"Total cards found: {len(all_cards)}")
    
    try:
        sorted_cards = sorted(
            all_cards, 
            key=lambda cid: int(mw.col.get_card(cid).note()['Deck ID'].split('@')[-1])
        )
        print("Cards sorted successfully.")
        
        for i, card_id in enumerate(sorted_cards, start=1):
            card = mw.col.get_card(card_id)
            note = card.note()
            deck_id_field = note['Deck ID'] if 'Deck ID' in note else None
            if deck_id_field:
                print(f"Updating Deck ID for Card ID: {card_id}, Current Deck ID: {deck_id_field}")
                
                prefix = deck_id_field.rsplit('@', 1)[0]
                new_deck_id = f"{prefix}@{str(i).zfill(5)}"
                note['Deck ID'] = new_deck_id
                mw.col.update_note(note)
                print(f"New Deck ID for Card ID: {card_id} is {new_deck_id}")
            
    except Exception as e:
        print(f"Error reordering Deck IDs: {str(e)}")

# Function to find the highest Deck ID in the format Deck_Name@00000, excluding subdecks
def get_max_deck_index(deck_id) -> int:
    # Reorder Deck IDs before continuing
    reorder_deck_ids(deck_id)
    
    # Get all notes that may potentially be in the deck and its subdecks
    note_deck_name = mw.col.decks.get(deck_id)['name']
    all_cards = mw.col.decks.cids(deck_id, children=False)
    max_index = 0

    for card_id in all_cards:
        card = mw.col.get_card(card_id)
        note = card.note()  # Get the note associated with the card
        index_field = note['Deck ID'] if 'Deck ID' in note else None
        
        # Check if the Deck ID field is not empty and is in the correct format
        if index_field and '@' in index_field:
            index_part = index_field.split('@')[-1]
            if index_part.isdigit():
                index_part = int(index_part)
                print(f"Index part: {index_part}")
                max_index = max(max_index, index_part)
        else:
            print(f"Invalid or empty Deck ID for Card ID: {card_id}")
            # Can proceed without modifying max_index, which starts at 0

    return max_index

# Function to add or replace the Deck ID in a note
def add_deck_index_field(note: Note, deck_id):
    deck_name = mw.col.decks.get(deck_id)['name']
    
    # Get the highest existing index or start at 1 if there are no valid indices
    next_index = get_max_deck_index(deck_id) + 1
    if next_index == 1:  # This means max_index was 0 and there were no valid indices
        print("No valid Deck ID found, starting at 00001")
    
    new_deck_id = f"{deck_name}@{str(next_index).zfill(5)}"
    
    note['Deck ID'] = new_deck_id
    print(f"Assigned Deck ID: {new_deck_id}")

# Function to add or replace the Deck ID in a note
def add_deck_on_profile(note: Note, deck_id):
    deck_name = mw.col.decks.get(deck_id)['name']
    
    # Get the highest existing index or start at 1 if there are no valid indices
    next_index = get_max_deck_index(deck_id) + 1
    if next_index == 1:  # This means max_index was 0 and there were no valid indices
        print("No valid Deck ID found, starting at 00001")
    
    new_deck_id = f"{deck_name}@{str(next_index).zfill(5)}"
    
    note['Deck ID'] = new_deck_id
    print(f"Assigned Deck ID: {new_deck_id}")
    mw.col.update_note(note)

# Function to verify, reorder, and reset Deck IDs during startup
def verify_and_add_deck_ids():
    all_notes = mw.col.find_notes("")
    
    # Sort notes by the value in the 'Deck ID' field
    sorted_notes = sorted(all_notes, key=lambda note_id: mw.col.get_note(note_id)['Deck ID'] if 'Deck ID' in mw.col.get_note(note_id) else '')
    
    # Dictionary to track the current index for each deck
    deck_counters = {}

    for note_id in sorted_notes:
        note = mw.col.get_note(note_id)
        if 'Deck ID' not in note:
            continue  # Skip notes without the 'Deck ID' field
        
        card = note.cards()[0]
        deck_id = card.current_deck_id()
        deck_name = mw.col.decks.get(deck_id)['name']

        # Initialize the counter for this deck if not already done
        if deck_name not in deck_counters:
            deck_counters[deck_name] = 1
        else:
            deck_counters[deck_name] += 1

        deck_id_field = note['Deck ID']
        expected_deck_id = f"{deck_name}@{str(deck_counters[deck_name]).zfill(5)}"
        
        # Check if the current Deck ID matches the expected format
        if deck_id_field != expected_deck_id:
            note['Deck ID'] = expected_deck_id  # Assign the correct Deck ID
            mw.col.update_note(note)
            print(f"Updated Deck ID for Note ID {note_id}: {expected_deck_id}")

    print("All Deck IDs have been verified and updated if necessary.")


# Callback that is called before a note is added
def on_note_will_be_added(col, note: Note, deck_id):
    if 'Deck ID' in note:
        add_deck_index_field(note, deck_id)

# Callback when Anki starts up
def on_profile_did_open():
    verify_and_add_deck_ids()

# Add the hook for note addition
note_will_be_added.append(on_note_will_be_added)

# Add the hook to verify and add Deck IDs during startup
gui_hooks.profile_did_open.append(on_profile_did_open)

