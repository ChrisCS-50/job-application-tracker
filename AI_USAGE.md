# AI Usage Documentation

This document outlines how GenAI was used to facilitate the structural development, logic implementation, and styling of the Job Application Tracker project. My own manual coding and GenAI suggestions contributed approximately 50/50 to the final product.

## Tools Used
- **Google Gemini 3.1 Pro**: Used to write the boilerplate structure of Flask routes, complex SQL query logic (especially for JOIN operations and dashboard aggregations), and generating the initial responsive CSS framework. I also wrote roughly half of the code manually, particularly debugging connections and fine-tuning the look and feel according to my preferences.

## Key Prompts
1. *"Write a Python Flask `app.py` structure and hook it up to a `JobTrackerDB` class that uses `mysql-connector-python`."*
2. *"Can you write a responsive, glassmorphism CSS UI framework suitable for an advanced dashboard?"*
3. *"Write a Python function to compare a string of comma-separated user skills against JSON arrays of job requirements and calculate the match percentage."*
4. *"Create a dashboard aggregate SQL query to count active applications vs rejected applications."*

## What Worked Well
- The AI was incredibly fast at setting up the boilerplate Create, Read, Update, Delete (CRUD) operations for the four different tables. Writing all forms manually would have been extremely tedious.
- The base Python logic for the Skill Match feature provided a great starting block, doing accurate intersections of sets in Python.
- Fast generation of the `dashboard.html` grid layout using CSS grid.

## What I Modified
- I manually rewrote the error-handling wrappers in Python's `database.py` to ensure it properly cleaned up connections and rolled back instances correctly for the specific table logic.
- The AI initially suggested generic colors and a basic UI. I heavily modified the `style.css` to introduce the dark mode palette, fix spacing arrays, and inject the interactive hover micro-animations.
- I modified the HTML structure to use FontAwesome icons across the board, matching them to my personalized dashboard aesthetics.
- I adapted the JSON parsing logic in `update_job` manually since the AI's first iteration wasn't strictly catching the comma-separated strings.

## Lessons Learned
- **AI isn't aware of data specifics**: AI works great to construct `SELECT * FROM table`, but actually defining exact Foreign Key constraints manually ensures data integrity without endless debugging with the bot.
- **Micro-managing AI CSS is harder than writing it**: Sometimes it was much faster for me to just code the CSS transitions myself rather than trying to perfectly describe them in natural language.
- **The value is in boilerplate and algorithms**: Using the AI for the raw Python match calculations and the `app.py` route skeletons saved me an incredible amount of time so I could focus on debugging and user experience.
