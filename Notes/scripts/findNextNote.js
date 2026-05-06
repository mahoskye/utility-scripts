const fs = require('fs');
const path = require('path');

/**
 * Function to find the existing Obsidian daily note
 * that comes after a given date, or return tomorrow's filename if none exists.
 * 
 * @param {Object} tp - Templater object containing file and utility methods
 * @param {Object} tp.file - FIle utilities from Templater
 * @param {string} to.file.title - The title/filename of the current note (expected format: 'YYYY-MM-DD')
 * @returns {string} - The basename of the next existing note found, or tomorrow's filename with .md extension if none exists within search range
 * @throws {Error} - Throws error if date format is invalid
 * 
 * @example
 * // For a note titles "2024-01-15", this might return "2024-01-16" if it exists,
 * // or "2024-01-17" if 01-16 doesn't exist but 01-17 does,
 * // or "2024-01-16.md" if no future notes exist within 30 days
 */

const noteFolder = 'daily-notes'; // Adjust this to your daily notes folder if different

function findNextNote(tp) {
    // Get the date string from the template parameters (current note's date)
    const currentNoteDateStr = tp.file.title; // Expected format: 'YYYY-MM-DD'

    // Validate the date format
    if (!/^\d{4}-\d{2}-\d{2}$/.test(currentNoteDateStr)) {
        throw new Error('Invalid date format. Expected YYYY-MM-DD.');
    }

    // Set initial variables for the search
    let searchAttempts = 0;
    const maxSearchDays = 30; // Limit search to the next 30 days

    // Start searching from the day after the current note's date
    let nextDay = new Date(currentNoteDateStr);

    // Check what day today is and skip weekends accordingly
    const today = new Date();
    const dayOfWeek = today.getDay(); // 0 (Mon) to 6 (Sun)

    if (dayOfWeek === 4) { // Friday
        nextDay.setDate(today.getDate() + 3); // Skip to Monday
    } else if (dayOfWeek === 5) { // Saturday
        nextDay.setDate(today.getDate() + 2); // Skip to Monday
    } else {
        nextDay.setDate(today.getDate() + 1); // Just go to the next day
        if(nextDay.getDay() === 5) { // If next day is Saturday
            nextDay.setDate(nextDay.getDate() + 2); // Skip to Monday
        }
        else if(nextDay.getDay() === 6) { // If next day is Sunday
            nextDay.setDate(nextDay.getDate() + 1); // Skip to Monday
        }
    }

    let foundNextNote = null;

    // Search forward through future days to find an existing note
    while (searchAttempts < maxSearchDays) {
        // Create a date string in the format 'YYYY-MM-DD' for the day we're checking
        const searchDateStr = nextDay.toISOString().slice(0, 10); // 'YYYY-MM-DD'
        const potentialNoteFileName = `${searchDateStr}.md`;
        const potentialNotePath = `${noteFolder}/${potentialNoteFileName}`; // Adjust path as necessary

        // Use Templater's file utilities to check if the note exists in the daily notes folder
        const  noteFile = tp.file.find_tfile(potentialNotePath);
        if (noteFile && tp.file.exists(potentialNotePath)) {
            // Found an existing next note - return with alias syntax to show only date
            foundNextNote = `${noteFolder}/${noteFile.basename}|${noteFile.basename}`;
            break; // Exit loop if we found the next note
        }

        // Move to the next day and increment our search attepmpt counter
        nextDay.setDate(nextDay.getDate() + 1);
        searchAttempts++;
    }

    // If no existing note is found within search range, return tomorrow's date with .md extension
    if (!foundNextNote) {
        const tomorrow = new Date(currentNoteDateStr);

        // Check what day today is and skip weekends accordingly
        const today = new Date(currentNoteDateStr);
        const dayOfWeek = today.getDay(); // 0 (Mon) to 6 (Sun)

        if (dayOfWeek === 4) { // Friday
            tomorrow.setDate(today.getDate() + 3); // Skip to Monday
        } else if (dayOfWeek === 5) { // Saturday
            tomorrow.setDate(today.getDate() + 2); // Skip to Monday
        } else {
            tomorrow.setDate(today.getDate() + 1); // Just go to the next day
            if(tomorrow.getDay() === 5) { // If next day is Saturday
                tomorrow.setDate(tomorrow.getDate() + 2); // Skip to Monday
            }
            else if(tomorrow.getDay() === 6) { // If next day is Sunday
                tomorrow.setDate(tomorrow.getDate() + 1); // Skip to Monday
            }
        }

        const tomorrowStr = tomorrow.toISOString().slice(0, 10);
        return `${noteFolder}/${tomorrowStr}|${tomorrowStr}`;

    }

    // Return the found next note's basename (without .md extension)
    return foundNextNote;

}

module.exports = findNextNote;