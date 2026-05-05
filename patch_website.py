with open('docs/index.html', 'r', encoding='utf-8') as f:
    src = f.read()

old = """  <div class="features">
    <div class="feat"><h3>Two-sided cards</h3><p>Beat or scene title on the front, notes on the back. Rich text formatting in notes. Flip individual cards or all at once.</p></div>
    <div class="feat"><h3>Color coding</h3><p>Multi-color accent bars and fill colors with a per-project legend. Spotlight any color to see where it falls across your script.</p></div>
    <div class="feat"><h3>Act filtering</h3><p>Name a card ACT ONE and the app detects it as a structural divider and builds a filter strip automatically.</p></div>
    <div class="feat"><h3>Native file saving</h3><p>Each project saves as a <code>.screenplaycards</code> file anywhere on your Mac. Open, close, and manage projects like any other document.</p></div>
    <div class="feat"><h3>Fit all view</h3><p>Scale every card to fit the screen at once &mdash; a true bird&rsquo;s eye view of your whole structure.</p></div>
    <div class="feat"><h3>Outline &amp; beat sheet</h3><p>Generate a numbered step outline with notes, or a clean beat sheet with titles only. Both respect active act filters.</p></div>
  </div>"""

new = """  <div class="features">
    <div class="feat"><h3>Two-sided cards</h3><p>Beat or scene title on the front, notes on the back. Rich text formatting in notes. Flip individual cards or all at once.</p></div>
    <div class="feat"><h3>Color coding</h3><p>Accent color bars and fill colors per card, with a per-project legend. Spotlight any color to see where it falls across your outline.</p></div>
    <div class="feat"><h3>Act headers &amp; filtering</h3><p>Name a card ACT ONE and the app detects it automatically. A filter strip lets you isolate any act. Collapse acts to declutter the board.</p></div>
    <div class="feat"><h3>Limbo panel</h3><p>A holding area for cards you&rsquo;ve cut but aren&rsquo;t ready to delete. Park them on the right side of the board and restore anytime.</p></div>
    <div class="feat"><h3>Multi-select</h3><p>Select any number of cards at once to batch delete or move them to Limbo. Cmd+A selects all visible cards.</p></div>
    <div class="feat"><h3>Card linking</h3><p>Connect cards bidirectionally to track relationships across your outline &mdash; parallel storylines, callbacks, cause and effect.</p></div>
    <div class="feat"><h3>Zoom &amp; views</h3><p>Grid or list view. Drag the zoom slider from 40% to 150%. Toggle column or row flow. Notes preview on card fronts without flipping.</p></div>
    <div class="feat"><h3>Exports</h3><p>Step outline with notes and color legend, beat sheet, or scene summary by act. All exports open in Preview with the full macOS print dialog.</p></div>
    <div class="feat"><h3>Native file saving</h3><p>Projects save as <code>.screenplaycards</code> files. Works with iCloud, Dropbox, and Google Drive. Auto-saves while you work.</p></div>
  </div>"""

assert old in src, "features section not found"
src = src.replace(old, new, 1)

with open('docs/index.html', 'w', encoding='utf-8') as f:
    f.write(src)

print("Done")
