const fs = require('fs');
const path = require('path');

/**
 * Function to find the most recent existing Obsidian daily note 
 * that comes before a given date.
 * 
 * @param {Object} tp - Templater object containing file and utility methods
 * @param {Object} tp.file - File utilities from Templater
 * @param {string} to.file.title - The title/filename of the current note (expected format: 'YYYY-MM-DD')
 * @returns {string} - The basename of the previous existing note found, or null if none exists within search range
 * @throws {Error} - Throws error if date format is invalid
 * 
 * @example
 * // For a note titled "2024-01-15", this might return "2024-01-14" if it exists,
 * // or "2024-01-13" if 01-14 doesn't exist but 01-13 does,
 * // or null if no previous notes exist within 30 days
 */

const noteFolder = 'daily-notes'; // Adjust this to your daily notes folder if different

function findPreviousNote(tp) {
    // Get the date string from the template parameters (current note's date)
    const currentNoteDateStr = tp.file.title; // Expected format: 'YYYY-MM-DD'

    // Validate the date format
    if (!/^\d{4}-\d{2}-\d{2}$/.test(currentNoteDateStr)) {
        throw new Error('Invalid date format. Expected YYYY-MM-DD.');
    }

    // Set initial variables for the search
    let searchAttempts = 0;
    const maxSearchDays = 30; // Limit search to the previous 30 days

    // Start searching from the day before the current note's date
    let previousDay = new Date(currentNoteDateStr);
    previousDay.setDate(previousDay.getDate() - 1);

    let foundPreviousNote = null;

    // Search backward through previous days to find an existing note
    while (searchAttempts < maxSearchDays) {
        // Create a date string in the format 'YYYY-MM-DD' for the day we're checking
        const checkDateStr = previousDay.toISOString().slice(0, 10);
        const potentialNoteFileName = `${checkDateStr}.md`;

        // Use Templater's file utilities to check if the note path exists in the vault
        const noteFile = tp.file.find_tfile(potentialNoteFileName);

        // Check if the file exists
        if (noteFile && tp.file.exists(noteFile.path)) {
            foundPreviousNote = noteFile.basename;
            break;
        }

        // Move to the previous day
        previousDay.setDate(previousDay.getDate() - 1);
        searchAttempts++;
    }

    return foundPreviousNote; // Return the found note or null if none found
}

module.exports = findPreviousNote;