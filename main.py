"""
Main Script for Anki Add-on: Auto Deck ID Manager

This is the main entry point for the Auto Deck ID Manager. It initializes the
necessary hooks and ensures the Deck IDs for notes in Anki are properly managed.

Modules:
- deck_id_manager: Contains all functions related to Deck ID management, including
  reordering, assigning, and verifying Deck IDs.
- browser_id_manager: Manages the interaction with the Anki browser, including 
  reordering and displaying visible cards with their Deck IDs.

Initialization:
- Hooks are initialized during the startup of Anki to manage Deck IDs when notes are
  added or when Anki starts.

Author: Matheus Bento de Souza
Date: August 2024
"""

# Import necessary functions and hooks from the deck_id_manager module
from .deck_id_manager import (
    reorder_deck_ids,
    get_max_deck_index,
    add_deck_index_field,
    add_deck_on_profile,
    verify_and_add_deck_ids,
    on_note_will_be_added,
    on_profile_did_open
)

# Import browser management functions from browser_id_manager module
from .browser_id_manager import (
    on_browser_will_show_context_menu,
)

from aqt import gui_hooks
from anki.hooks import note_will_be_added

# Initialize hooks to manage Deck IDs in Anki
def initialize_hooks():
    # Hook to ensure Deck IDs are added when a new note is created
    note_will_be_added.append(on_note_will_be_added)

    # Hook to verify and add missing Deck IDs when Anki starts
    gui_hooks.profile_did_open.append(on_profile_did_open)

    # Hook to manage context menu in the browser
    gui_hooks.browser_will_show_context_menu.append(on_browser_will_show_context_menu)

    print("Auto Deck ID Manager hooks initialized.")

# Main entry point for the script
if __name__ == "__main__":
    initialize_hooks()
