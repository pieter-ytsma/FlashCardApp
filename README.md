Flashcards App

A minimal, offline flashcard application built with Python and PySide6.

This project focuses on simplicity. No accounts, no syncing, no algorithms running in the background. Just create cards, save a deck, and practice.

What this is

This is a lightweight desktop flashcard app for people who want a straightforward study tool without complexity.

It is designed to:

Create simple question/answer cards

Save and load decks locally

Practice cards manually

Switch interface language

What this is not

This app does not include:

Cloud synchronization

User accounts

Spaced repetition algorithms

Learning statistics or analytics

Collaboration features

It is intentionally minimal.

Who this is for

Students who want a distraction-free study tool

Users who prefer offline software

People who find larger tools like Anki too heavy for simple use cases

Developers looking for a clean example of a small PySide6 desktop project

Features

Create and edit flashcards

Save decks to file

Load existing decks

Manual practice mode

Language switching

Standalone Windows executable build

How to use

Create a new deck or load an existing one.

Add question and answer pairs.

Save the deck locally.

Click “Practice” to start reviewing cards.

Move through cards manually.

Build (for developers)

The standalone Windows executable is built using PyInstaller:

pyinstaller app.py --onefile --noconsole --icon=icon.ico

Make sure the icon file is in the correct directory before building.

Versioning

Versions follow a simple semantic pattern:

Major changes: 1.0.0 → 2.0.0

New features: 1.0.0 → 1.1.0

Bug fixes: 1.0.0 → 1.0.1