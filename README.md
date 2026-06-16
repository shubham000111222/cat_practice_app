# CAT Practice Platform

An offline, fully functional CAT preparation platform built with Streamlit and SQLite.

## Features

- **Practice Mode**: Filter questions by Section, Topic, and Difficulty.
- **Quiz Mode**: Timed quizzes.
- **Mock Tests**: Generate Mini Mocks and Full CAT-style mock tests.
- **Calculator**: Authentic CAT-style on-screen calculator available in all test modes.
- **Analytics**: Detailed performance tracking with Plotly charts.
- **Bookmarks & Revision**: Save questions for later and review weak areas using spaced repetition.
- **Exports**: Download your performance data as CSV or PDF reports.
- **Offline First**: Runs entirely locally using SQLite, requiring no internet connection.

## Setup Instructions

### Quick Start (Windows)
If you have the compiled executable:
1. Open the `dist/CAT_Practice_Platform/` folder.
2. Double-click `CAT_Practice_Platform.exe`.

### Manual Setup (Python)
1. Ensure you have Python installed.
2. Navigate to this directory (`cat_practice_app`).
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   - **For Windows Users**: Simply double-click the `Launch_CAT_Practice.bat` file!
   - **For Mac/Linux Users** (or via terminal):
     ```bash
     python -m streamlit run app.py
     ```

### Building the Executable
If you modify the code and want to compile a new `.exe`:
1. Ensure `pyinstaller` is installed (`pip install pyinstaller`).
2. Run the `build_exe.bat` script.
3. Your new `.exe` will be generated in the `dist/CAT_Practice_Platform/` folder.

## Database

The application uses an existing `cat_question_bank.db` stored in the `database/` folder. On the first launch, the app will automatically run a migration script to add missing tables required for the platform (such as attempts, bookmarks, revision_queue, user_settings).
