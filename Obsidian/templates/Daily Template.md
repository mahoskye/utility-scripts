<%*
// Capture existing content before clearing the file
const existingContent = tp.file.content;

// Clear the entire file contents first
await app.vault.modify(tp.file.find_tfile(tp.file.title), "");
-%>
# <% tp.date.now("dddd, MMMM Do, YYYY",0,tp.file.title, "YYYY-MM-DD") %>
---
Tags:

## Tasks:
---
- [ ] <% tp.file.cursor() %>
- [ ] Set up tasks for tomorrow

## Notes:
---

## Daily Log:
---
<% existingContent %>

---
← [[<% tp.user.findPreviousNote(tp) %>]] | [[<% tp.user.findNextNote(tp) %>]] →