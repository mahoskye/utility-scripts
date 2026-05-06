/**
 * Returns a newline-joined string of unique, unfinished task lines
 * ("- [ ] ...") found in the Tasks section of the previous daily note.
 *
 * The previous note is located by walking backward from the current
 * note's date (YYYY-MM-DD) up to 30 days, matching findPreviousNote.
 *
 * The boilerplate "Set up tasks for tomorrow" item is filtered out so
 * the daily template's own copy of that line isn't duplicated.
 *
 * @param {Object} tp - Templater object
 * @returns {Promise<string>} task lines joined by "\n", or "" if none
 */
async function rollForwardTasks(tp) {
    const currentNoteDateStr = tp.file.title;
    if (!/^\d{4}-\d{2}-\d{2}$/.test(currentNoteDateStr)) {
        return "";
    }

    let day = new Date(currentNoteDateStr);
    day.setDate(day.getDate() - 1);

    let prevFile = null;
    for (let i = 0; i < 30; i++) {
        const checkDateStr = day.toISOString().slice(0, 10);
        const noteFile = tp.file.find_tfile(`${checkDateStr}.md`);
        if (noteFile && tp.file.exists(noteFile.path)) {
            prevFile = noteFile;
            break;
        }
        day.setDate(day.getDate() - 1);
    }

    if (!prevFile) return "";

    const content = await app.vault.read(prevFile);
    const lines = content.split("\n");

    const tasksHeader = lines.findIndex(l => /^##\s+Tasks:?\s*$/.test(l));
    if (tasksHeader === -1) return "";

    let endIdx = lines.length;
    for (let i = tasksHeader + 1; i < lines.length; i++) {
        if (/^##\s+/.test(lines[i])) { endIdx = i; break; }
    }

    const seen = new Set();
    const result = [];
    const boilerplate = "set up tasks for tomorrow";
    let pendingHeading = null;
    let pendingHeadingEmitted = false;

    for (let i = tasksHeader + 1; i < endIdx; i++) {
        const line = lines[i];

        // Track sub-headings (h3+) so we can preserve them above their tasks
        if (/^#{3,}\s+/.test(line)) {
            pendingHeading = line;
            pendingHeadingEmitted = false;
            continue;
        }

        const m = line.match(/^(\s*)-\s+\[\s\]\s+(.*)$/);
        if (!m) continue;
        const indent = m[1];
        const text = m[2].trim();
        if (!text) continue;
        if (text.toLowerCase() === boilerplate) continue;
        const key = text.toLowerCase();
        if (seen.has(key)) continue;
        seen.add(key);

        if (pendingHeading && !pendingHeadingEmitted) {
            result.push(pendingHeading);
            pendingHeadingEmitted = true;
        }
        result.push(`${indent}- [ ] ${text}`);
    }

    return result.join("\n");
}

module.exports = rollForwardTasks;
