"""
Anki Add-on: Auto Deck ID Manager

This add-on provides functionality to manage and reorder Deck IDs within Anki's browser. 
Users can view all visible cards, and move them up or down within the same deck, while 
ensuring that cards from different decks cannot be reordered relative to each other.

Functions:
- get_visible_card_ids(browser):
    Selects all visible cards in the Anki browser and returns their IDs.
    
- reorder_deck_ids(visible_card_ids):
    Reorders the Deck IDs for the given list of card IDs, ensuring each card has a unique 
    and correctly ordered Deck ID.
    
- update_deck_ids_after_swap(card_a, card_b):
    Swaps the Deck IDs between two cards, but only if they belong to the same deck. 
    If the cards are from different decks, no changes are made, and the function returns False.
    
- move_card_up(browser, selected_card_id, visible_card_ids):
    Moves the selected card up in the list of visible cards, but only if the card above it 
    belongs to the same deck. Returns True if the move was successful, otherwise False.
    
- move_card_down(browser, selected_card_id, visible_card_ids):
    Moves the selected card down in the list of visible cards, but only if the card below it 
    belongs to the same deck. Returns True if the move was successful, otherwise False.
    
- show_all_visible_cards(browser):
    Displays a dialog showing all visible cards in the browser along with their Deck IDs 
    and front field contents. Allows the user to move cards up or down within the list.
    
- update_list_widget(list_widget, visible_card_ids):
    Updates the QListWidget with the current list of visible cards, reflecting any changes 
    in the order of the cards.
    
- on_browser_will_show_context_menu(browser, menu):
    Adds an option to the context menu in Anki's browser to display the "Deck IDs and Fronts" 
    dialog, where the user can view and reorder cards.
    
Hooks:
- gui_hooks.browser_will_show_context_menu.append(on_browser_will_show_context_menu):
    Attaches the on_browser_will_show_context_menu function to the browser's context menu 
    display event, allowing users to access the add-on's functionality.
    
Usage:
- Once installed, right-click in the Anki browser to access the "Show Deck IDs and Visible Fronts" option.
- Use the up and down buttons to reorder cards within the same deck.
- The add-on ensures that cards from different decks cannot be reordered relative to each other.

Author: Matheus Bento de Souza
Date: August 2024
"""
from aqt import mw, gui_hooks
from aqt.qt import QAction, QDialog, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QHBoxLayout, Qt
from aqt.utils import showInfo

# Function to select all visible cards and get their IDs
def get_visible_card_ids(browser):
    browser.table.select_all()
    visible_card_ids = browser.table.get_selected_card_ids()
    browser.table.clear_selection()
    return visible_card_ids

def reorder_deck_ids(visible_card_ids):
    for i, card_id in enumerate(visible_card_ids):
        card = mw.col.get_card(card_id)
        note = card.note()
        deck_id_field = note["Deck ID"]

        # Extract the prefix from the Deck ID (everything before the number)
        prefix = deck_id_field.rsplit('@', 1)[0]

        # Update the Deck ID field with the new position
        new_deck_id = f"{prefix}@{str(i + 1).zfill(5)}"
        note["Deck ID"] = new_deck_id
        mw.col.update_note(note)

def update_deck_ids_after_swap(card_a, card_b):
    note_a = card_a.note()
    note_b = card_b.note()

    # Correctly extract the prefix and suffix
    prefix_a = note_a["Deck ID"].rsplit('@', 1)[0]
    prefix_b = note_b["Deck ID"].rsplit('@', 1)[0]
    
    # Check if the Deck ID prefixes are equal
    if prefix_a != prefix_b:
        return False  # Do not allow swapping between different decks
    
    # Extract the numeric part of the Deck ID (assuming it comes after '@')
    suffix_b = note_b["Deck ID"].rsplit('@', 1)[-1]
    suffix_a = note_a["Deck ID"].rsplit('@', 1)[-1]

    # Update Deck ID of card A
    new_deck_id_a = f"{prefix_a}@{suffix_b}"
    note_a["Deck ID"] = new_deck_id_a
    mw.col.update_note(note_a)

    # Update Deck ID of card B
    new_deck_id_b = f"{prefix_b}@{suffix_a}"
    note_b["Deck ID"] = new_deck_id_b
    mw.col.update_note(note_b)
    
    return True

def move_card_up(browser, selected_card_id, visible_card_ids):
    index = visible_card_ids.index(selected_card_id)
    if index > 0:  # Check if the swap is valid
        upper_card_id = visible_card_ids[index - 1]
        upper_card = mw.col.get_card(upper_card_id)
        selected_card = mw.col.get_card(selected_card_id)

        # Try to update the Deck IDs after the swap
        if update_deck_ids_after_swap(selected_card, upper_card):
            # Swap the selected card with the one above
            visible_card_ids[index], visible_card_ids[index - 1] = visible_card_ids[index - 1], visible_card_ids[index]
            return True
        
    return False

def move_card_down(browser, selected_card_id, visible_card_ids):
    index = visible_card_ids.index(selected_card_id)
    if index < len(visible_card_ids) - 1:  # Check if the swap is valid
        lower_card_id = visible_card_ids[index + 1]
        lower_card = mw.col.get_card(lower_card_id)
        selected_card = mw.col.get_card(selected_card_id)

        # Try to update the Deck IDs after the swap
        if update_deck_ids_after_swap(selected_card, lower_card):
            # Swap the selected card with the one below
            visible_card_ids[index], visible_card_ids[index + 1] = visible_card_ids[index + 1], visible_card_ids[index]
            return True
        
    return False

def show_all_visible_cards(browser):
    visible_card_ids = get_visible_card_ids(browser)

    if not visible_card_ids:
        showInfo("No cards found.")
        return

    dialog = QDialog(browser)
    dialog.setWindowTitle("Deck IDs and Visible Fronts")

    layout = QVBoxLayout()

    list_widget = QListWidget()
    for card_id in visible_card_ids:
        card = mw.col.get_card(card_id)
        note = card.note()
        deck_id_field = note["Deck ID"]
        front_field = note.fields[0]
        display_text = f"{deck_id_field} - {front_field}"
        item = QListWidgetItem(display_text)
        item.setData(Qt.ItemDataRole.UserRole, card_id)
        list_widget.addItem(item)
    
    layout.addWidget(list_widget)

    # Add buttons to move up and down
    button_layout = QHBoxLayout()
    move_up_button = QPushButton("Move Up")
    move_down_button = QPushButton("Move Down")

    def move_selected_card_up():
        selected_item = list_widget.currentItem()
        if selected_item:
            selected_card_id = selected_item.data(Qt.ItemDataRole.UserRole)
            if move_card_up(browser, selected_card_id, visible_card_ids):
                update_list_widget(list_widget, visible_card_ids)

    def move_selected_card_down():
        selected_item = list_widget.currentItem()
        if selected_item:
            selected_card_id = selected_item.data(Qt.ItemDataRole.UserRole)
            if move_card_down(browser, selected_card_id, visible_card_ids):
                update_list_widget(list_widget, visible_card_ids)

    move_up_button.clicked.connect(move_selected_card_up)
    move_down_button.clicked.connect(move_selected_card_down)
    
    button_layout.addWidget(move_up_button)
    button_layout.addWidget(move_down_button)
    layout.addLayout(button_layout)

    dialog.setLayout(layout)
    dialog.exec()

def update_list_widget(list_widget, visible_card_ids):
    list_widget.clear()
    for card_id in visible_card_ids:
        card = mw.col.get_card(card_id)
        note = card.note()
        deck_id_field = note["Deck ID"]
        front_field = note.fields[0]
        display_text = f"{deck_id_field} - {front_field}"
        item = QListWidgetItem(display_text)
        item.setData(Qt.ItemDataRole.UserRole, card_id)
        list_widget.addItem(item)

def on_browser_will_show_context_menu(browser, menu):
    action = QAction("Show Deck IDs and Visible Fronts", browser)
    action.triggered.connect(lambda: show_all_visible_cards(browser))
    menu.addAction(action)

gui_hooks.browser_will_show_context_menu.append(on_browser_will_show_context_menu)
