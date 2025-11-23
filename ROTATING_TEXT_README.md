# Rotating Text Feature

## Overview
The homepage features a rotating text paragraph that smoothly transitions between multiple quotes with a fade-in/fade-out effect.

## How It Works
1. **JavaScript File** (`static/js/text_rotator.js`): Handles the rotation logic and fade transitions
2. **Configuration File** (`static/rotating_texts.json`): Stores all the text paragraphs and configuration
3. **HTML Element**: The paragraph with id `hero-rotating-text` in `templates/index.html`

## How to Update the Rotating Texts

### Simple Method (Recommended)
Edit the file `mySite/static/rotating_texts.json`:

```json
{
  "paragraphs": [
    {
      "text": "Your quote text here",
      "author": "Author Name"
    }
  ],
  "rotationInterval": 5000,
  "fadeTransitionDuration": 800
}
```

### Configuration Options

- **paragraphs**: Array of text objects to rotate through
  - `text`: The actual quote or paragraph text
  - `author`: The author name (currently for reference, not displayed)
  
- **rotationInterval**: Time in milliseconds to display each paragraph (default: 5000 = 5 seconds)

- **fadeTransitionDuration**: Duration of the fade effect in milliseconds (default: 800ms)

### Adding New Quotes
1. Open `mySite/static/rotating_texts.json`
2. Add a new object to the `paragraphs` array:
   ```json
   {
     "text": "Your new quote here",
     "author": "Author Name"
   }
   ```
3. Save the file
4. Refresh your browser to see the changes

### Example
```json
{
  "paragraphs": [
    {
      "text": "Shall I compare thee to a summer's day? Thou art more lovely and more temperate.",
      "author": "William Shakespeare"
    },
    {
      "text": "Two roads diverged in a wood, and I took the one less traveled by.",
      "author": "Robert Frost"
    },
    {
      "text": "The only way to do great work is to love what you do.",
      "author": "Steve Jobs"
    }
  ],
  "rotationInterval": 5000,
  "fadeTransitionDuration": 800
}
```

## Customization

### Change Rotation Speed
Adjust the `rotationInterval` value (in milliseconds):
- `5000` = 5 seconds (default)
- `10000` = 10 seconds
- `3000` = 3 seconds

### Change Fade Speed
Adjust the `fadeTransitionDuration` value (in milliseconds):
- `800` = 0.8 seconds (default)
- `1000` = 1 second
- `500` = 0.5 seconds (faster)

## Technical Details

The rotation system works by:
1. Loading the JSON configuration on page load
2. Fading out the current text
3. Updating the text content
4. Fading in the new text
5. Repeating after the specified interval

The JavaScript class `TextRotator` is globally accessible via `window.textRotator` if you need to control it programmatically.

## Files Involved
- `mySite/static/js/text_rotator.js` - The rotation logic
- `mySite/static/rotating_texts.json` - The text content and configuration
- `mySite/templates/index.html` - The HTML template (lines 8-9 and line 25)
