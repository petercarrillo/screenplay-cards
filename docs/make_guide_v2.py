from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

OUT = '/mnt/user-data/outputs/screenplay-cards-guide.pdf'

# ── Colors ────────────────────────────────────────────────────────────────────
INK       = colors.HexColor('#1a1a18')
MUTED     = colors.HexColor('#888780')
ACCENT    = colors.HexColor('#4a6fa5')
RULE      = colors.HexColor('#d3d1c7')
BG_CHIP   = colors.HexColor('#f0eeea')
NEW_BG    = colors.HexColor('#eaf2fb')
NEW_BORDER= colors.HexColor('#4a6fa5')
TIP_BG    = colors.HexColor('#f5f4f0')
TIP_BORDER= colors.HexColor('#b4b2a9')

# ── Styles ────────────────────────────────────────────────────────────────────
base = getSampleStyleSheet()

def S(name, **kw):
    return ParagraphStyle(name, **kw)

sTitle = S('sTitle',
    fontName='Helvetica-Bold', fontSize=28, leading=34,
    textColor=INK, spaceAfter=6)

sSub = S('sSub',
    fontName='Helvetica', fontSize=13, leading=17,
    textColor=MUTED, spaceAfter=20)

sH1 = S('sH1',
    fontName='Helvetica-Bold', fontSize=16, leading=20,
    textColor=INK, spaceBefore=24, spaceAfter=6)

sH2 = S('sH2',
    fontName='Helvetica-Bold', fontSize=12, leading=16,
    textColor=INK, spaceBefore=14, spaceAfter=4)

sH3 = S('sH3',
    fontName='Helvetica-Bold', fontSize=10, leading=14,
    textColor=MUTED, spaceBefore=10, spaceAfter=2)

sBody = S('sBody',
    fontName='Helvetica', fontSize=10, leading=15,
    textColor=INK, spaceAfter=7)

sBullet = S('sBullet',
    fontName='Helvetica', fontSize=10, leading=15,
    textColor=INK, spaceAfter=3,
    leftIndent=14, firstLineIndent=-8)

sCode = S('sCode',
    fontName='Courier', fontSize=9, leading=13,
    textColor=INK, spaceAfter=4,
    leftIndent=14, backColor=BG_CHIP)

sCaption = S('sCaption',
    fontName='Helvetica-Oblique', fontSize=9, leading=12,
    textColor=MUTED, spaceAfter=6)

sFooter = S('sFooter',
    fontName='Helvetica', fontSize=8, leading=10,
    textColor=MUTED, alignment=TA_CENTER)

sNew = S('sNew',
    fontName='Helvetica-Bold', fontSize=8, leading=10,
    textColor=ACCENT)

# ── Helpers ───────────────────────────────────────────────────────────────────
W = 6.5 * inch  # usable width

def rule():
    return HRFlowable(width='100%', thickness=0.5, color=RULE, spaceAfter=10, spaceBefore=4)

def h1(text):
    return Paragraph(text, sH1)

def h2(text):
    return Paragraph(text, sH2)

def h3(text):
    return Paragraph(text, sH3)

def body(text):
    return Paragraph(text, sBody)

def bullet(text):
    return Paragraph(u'\u2013\u2002' + text, sBullet)

def code(text):
    return Paragraph(text, sCode)

def sp(n=6):
    return Spacer(1, n)

def new_badge():
    return Paragraph('NEW IN 2.0', sNew)

def tip_box(text):
    data = [[Paragraph('<b>Tip:</b> ' + text, sBody)]]
    t = Table(data, colWidths=[W])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), TIP_BG),
        ('LINEAFTER',  (0,0), (-1,-1), 1, TIP_BORDER),
        ('LINEBEFORE', (0,0), (-1,-1), 2.5, TIP_BORDER),
        ('TOPPADDING',    (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
        ('RIGHTPADDING',  (0,0), (-1,-1), 10),
    ]))
    return t

def new_box(label, text):
    data = [[Paragraph('<b>' + label + '</b><br/>' + text, sBody)]]
    t = Table(data, colWidths=[W])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), NEW_BG),
        ('LINEBEFORE',  (0,0), (-1,-1), 3, NEW_BORDER),
        ('TOPPADDING',    (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
        ('RIGHTPADDING',  (0,0), (-1,-1), 10),
    ]))
    return t

def kv_table(rows):
    """Two-column key/value table."""
    data = [[Paragraph('<b>' + k + '</b>', sBody), Paragraph(v, sBody)] for k, v in rows]
    t = Table(data, colWidths=[1.6*inch, W - 1.6*inch])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING',    (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING',   (0,0), (-1,-1), 0),
        ('RIGHTPADDING',  (0,0), (-1,-1), 6),
        ('LINEBELOW', (0,0), (-1,-2), 0.3, RULE),
    ]))
    return t

# ── Page template (header/footer) ─────────────────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(MUTED)
    if doc.page > 1:
        canvas.drawString(inch, 0.6*inch, 'Screenplay Cards — User Guide')
        canvas.drawRightString(7.5*inch, 0.6*inch, str(doc.page))
    canvas.restoreState()

# ── Build story ───────────────────────────────────────────────────────────────
story = []

# ── Cover ──────────────────────────────────────────────────────────────────────
story += [
    sp(72),
    Paragraph('Screenplay Cards', sTitle),
    Paragraph('User Guide &mdash; Version 2.0', sSub),
    rule(),
    sp(8),
    body('A free, open-source Mac app for organizing your screenplay\'s structure '
         'using digital index cards. Write beats, arrange acts, rearrange ideas, '
         'and export when you\'re ready.'),
    sp(4),
    body('petercarrillo.github.io/screenplay-cards'),
    PageBreak(),
]

# ── Table of Contents ──────────────────────────────────────────────────────────
story += [
    h1('Contents'),
    rule(),
    sp(4),
]
toc_items = [
    ('1.', 'Getting Started'),
    ('2.', 'The Interface'),
    ('3.', 'Cards'),
    ('4.', 'Acts'),
    ('5.', 'Colors'),
    ('6.', 'Views & Zoom'),
    ('7.', 'Limbo Panel'),
    ('8.', 'Multi-Select'),
    ('9.', 'Card Linking'),
    ('10.', 'Exporting'),
    ('11.', 'Spellcheck & Formatting'),
    ('12.', 'Files & Auto-Update'),
    ('13.', 'Keyboard Shortcuts'),
]
for num, title in toc_items:
    story.append(Paragraph(
        f'<font color="#888780">{num}</font>&nbsp;&nbsp;{title}',
        sBody))
story += [PageBreak()]

# ══════════════════════════════════════════════════════════════════════════════
# 1. Getting Started
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h1('1. Getting Started'),
    rule(),
    body('Download the DMG for your Mac from the website (arm64 for Apple Silicon, '
         'x64 for Intel), open it, and drag Screenplay Cards to your Applications folder. '
         'On first launch, macOS may ask you to confirm opening an app from the internet — '
         'click Open.'),
    sp(4),
    h2('Welcome Panel'),
    body('When you launch the app with no file open, a welcome panel appears. From here '
         'you can start a new project, open a file, or pick from your recent files. '
         'Check "Don\'t show on launch" if you\'d rather open straight to a blank board.'),
    sp(4),
    h2('Your First Project'),
    body('Click <b>New Project</b> (or use <b>File &gt; New Project</b>) to create a project. '
         'You can have multiple projects open at once — they appear as tabs at the top of '
         'the window. Click the + button to add another project, or close one with the ✕ '
         'on its tab.'),
    sp(4),
    tip_box('The Hamlet sample project (included with the app) is a great way to explore '
            'the features before starting your own. Open it from File > Open and poke around.'),
    PageBreak(),
]

# ══════════════════════════════════════════════════════════════════════════════
# 2. The Interface
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h1('2. The Interface'),
    rule(),
    body('The window has three main areas: the <b>project bar</b> at the very top '
         '(your project tabs), the <b>toolbar</b> just below it (your controls), '
         'and the <b>board</b> where your cards live.'),
    sp(8),
    h2('The Toolbar'),
    body('Left to right, the toolbar contains:'),
    sp(4),
    kv_table([
        ('Grid / List',     'Switch between grid view and list view.'),
        ('&#8595; cols / &#8594; rows', 'Toggle whether cards flow in columns or rows in grid view.'),
        ('Flip',            'Flip all cards to show their back (notes) side.'),
        ('Filter',          'Open the color filter panel to spotlight cards by accent color.'),
        ('Preview',         'Show a text preview of each card\'s notes on the card front.'),
        ('Select',          'Enter multi-select mode to batch delete or move cards to Limbo.'),
        ('Limbo',           'Open or close the Limbo panel on the right side of the board.'),
        ('Beats / Outline / Summary', 'Export options.'),
        ('+ Add Card',      'Add a new card to the end of the board.'),
        ('Scene count',     'Shows the total number of scenes in the current act filter.'),
        ('Zoom slider',     'Drag to zoom the board from 40% to 150%.'),
    ]),
    PageBreak(),
]

# ══════════════════════════════════════════════════════════════════════════════
# 3. Cards
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h1('3. Cards'),
    rule(),
    h2('Adding Cards'),
    body('Click <b>+ Add Card</b> in the toolbar, or use <b>Card &gt; New Card</b> from the menu. '
         'You can also press <b>Tab</b> while a card title is focused to insert a new card '
         'immediately after it.'),
    sp(6),
    h2('The Front of the Card'),
    body('The front holds the card\'s <b>title</b> — the single-sentence beat or scene description. '
         'Click anywhere on the title text to start typing. The front also shows:'),
    bullet('<b>Scene number</b> (top left) — assigned automatically. Click it to exclude or '
           'restore a card from scene numbering.'),
    bullet('<b>Act collapse arrow</b> — appears on act header cards; click to collapse or expand '
           'the cards beneath that act.'),
    bullet('<b>Link badge</b> (&#8596;N) — shows how many cards this card is linked to. '
           'Click it to highlight linked cards on the board.'),
    bullet('<b>Duplicate button</b> (&#10064;) — creates a copy of the card and inserts it '
           'immediately after the original.'),
    bullet('<b>Accent color dot</b> — click to open the border color panel for this card.'),
    sp(6),
    h2('The Action Bar'),
    body('Hovering over a card reveals the <b>action bar</b> at the bottom of the front face. '
         'It contains:'),
    bullet('<b>&#8249; N &#8250;</b> — font size controls. Click once for a single step, '
           'or hold the arrow down to sweep through sizes quickly.'),
    bullet('<b>Fill color square</b> — opens the fill color panel (grid view only).'),
    bullet('<b>notes</b> — flip this card to its back to edit notes.'),
    bullet('<b>link</b> — open the link panel to connect this card to others.'),
    bullet('<b>&#10005;</b> — delete this card (asks for confirmation).'),
    sp(6),
    h2('The Back of the Card'),
    body('The back holds <b>notes</b> — anything from a brief reminder to a full scene breakdown. '
         'Notes support rich text: right-click anywhere in the notes field to access bold, italic, '
         'underline, and text alignment. Click <b>notes</b> in the action bar to flip to the back, '
         'and click anywhere outside the card\'s back to flip it closed, or use the <b>Flip</b> '
         'toolbar button to show all backs at once.'),
    sp(6),
    h2('Notes Preview'),
    body('Turn on <b>Preview</b> in the toolbar to see a two-line text preview of each card\'s '
         'notes directly on the card front, without having to flip the card.'),
    sp(6),
    h2('Reordering Cards'),
    body('Drag any card by its body to move it to a new position. A blue line shows where '
         'it will land. Release to drop. Works in both grid and list view.'),
    sp(6),
    h2('Deleting Cards'),
    body('Click the &#10005; button in the action bar. You\'ll be asked to confirm. '
         'To delete multiple cards at once, use multi-select mode (see section 8).'),
    sp(6),
    h2('Duplicating Cards'),
    body('Click the &#10064; button in the card\'s top row. A copy appears immediately '
         'after the original with all the same text, colors, and font size.'),
    sp(6),
    h2('Undo and Redo'),
    body('Use <b>Cmd+Z</b> to undo and <b>Cmd+Shift+Z</b> (or <b>Cmd+Y</b>) to redo. '
         'Undo works both for text edits within a card and for structural changes like '
         'drag-reordering, adding, deleting, or changing colors. When your cursor is inside '
         'a title or notes field, undo affects that card\'s text history. Outside a text '
         'field, undo affects the structural history.'),
    PageBreak(),
]

# ══════════════════════════════════════════════════════════════════════════════
# 4. Acts
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h1('4. Acts'),
    rule(),
    body('Act headers are just cards whose titles begin with the word <b>ACT</b> '
         '(all caps). The app detects them automatically — no special button required. '
         'Try typing "ACT ONE" or "ACT TWO" as a card title and it will become a full-width '
         'header that anchors that section of your outline.'),
    sp(6),
    h2('Act Filter Strip'),
    body('A row of act buttons appears above the board whenever your project has at least '
         'one act header. Click an act button to show only cards from that act. Click it '
         'again to deselect. You can have multiple acts visible at once. '
         'Exports always respect the current act filter.'),
    sp(6),
    h2('Collapsing Acts'),
    body('Click the <b>&#9660;</b> arrow on an act header card to collapse all the cards '
         'beneath it. Click again to expand. This is a view-only state — collapsed cards '
         'are still part of your project and will appear in exports.'),
    sp(6),
    tip_box('Act headers flow like normal cards in grid view — you can drag them anywhere. '
            'Cards are assigned to the act header immediately above them.'),
    PageBreak(),
]

# ══════════════════════════════════════════════════════════════════════════════
# 5. Colors
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h1('5. Colors'),
    rule(),
    body('Each card has two independent color settings: an <b>accent color</b> (the colored '
         'bar on the card edge) and a <b>fill color</b> (the card\'s background). '
         'These are set from separate panels.'),
    sp(8),
    h2('Accent Color (Border)'),
    body('Click the <b>color dot</b> (&#9679;) in the card\'s top-right corner to open the '
         'border color panel. Click a swatch to apply it. The panel stays open so you can '
         'compare colors across cards — click the dot again, press Escape, or click the close '
         'button to dismiss it.'),
    sp(4),
    body('The panel includes <b>legend labels</b>: editable text fields next to each color '
         'swatch. Use these to name your color scheme (e.g., "Protagonist", "Subplot A"). '
         'Labels appear in the color legend appendix of your step outline export.'),
    sp(6),
    h2('Fill Color'),
    body('In grid view, hover over a card to reveal the action bar, then click the '
         '<b>fill color square</b> to open the fill color panel. Fill color changes the '
         'card\'s entire background. The font size number and card title automatically '
         'switch to a readable contrast color when a fill is applied. '
         'Fill color is not available in list view.'),
    sp(6),
    h2('Color Filter'),
    body('The <b>Filter</b> button in the toolbar lets you spotlight cards by accent color '
         'without changing any card\'s color. Click Filter, then click one or more color '
         'swatches. Only cards tagged with those colors will show their color bar — '
         'all other cards go neutral. Press Escape, click Filter again, or close the panel '
         'to return every card to normal.'),
    sp(4),
    tip_box('Color filter is great for checking coverage: turn on Filter, select one color, '
            'and instantly see where that character or storyline appears across your outline.'),
    PageBreak(),
]

# ══════════════════════════════════════════════════════════════════════════════
# 6. Views & Zoom
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h1('6. Views & Zoom'),
    rule(),
    h2('Grid View'),
    body('The default view. Cards are displayed in a fixed-height grid. '
         'Use the <b>&#8595; cols / &#8594; rows</b> toggle to control whether cards '
         'flow column-first or row-first.'),
    sp(6),
    h2('List View'),
    body('A compact single-column layout with the card title on the left and notes '
         'on the right. Useful for reading through your outline quickly. '
         'Fill color and the fill color button are not available in list view.'),
    sp(6),
    h2('Zoom'),
    body('Drag the <b>zoom slider</b> in the toolbar to scale the board from 40% to 150%. '
         'This affects all cards simultaneously — useful for getting a full overview of a '
         'long outline or zooming in on a dense section.'),
    sp(4),
    tip_box('At a low zoom level with the act filter active you can get a compact bird\'s-eye '
            'view of a single act — helpful for checking beat pacing.'),
    PageBreak(),
]

# ══════════════════════════════════════════════════════════════════════════════
# 7. Limbo Panel
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h1('7. Limbo Panel'),
    rule(),
    h2('Opening Limbo'),
    body('Click the <b>Limbo</b> button in the toolbar to open a panel on the right side '
         'of the board. Click it again to close. Cards in Limbo are saved with your project.'),
    sp(6),
    h2('Moving Cards to Limbo'),
    body('To send a card to Limbo, enter <b>select mode</b> (click the Select button in '
         'the toolbar), select the card or cards you want to move, then click the '
         '<b>&#8594; Limbo</b> button that appears in the batch action bar. '
         'See section 8 for more on multi-select.'),
    sp(6),
    h2('Restoring Cards from Limbo'),
    body('In the Limbo panel, each card has a <b>&#8617; restore</b> button. '
         'Click it to move the card back to the end of the board. You can then drag it '
         'to wherever it belongs.'),
    sp(4),
    tip_box('Limbo is also useful for keeping alternate versions of scenes. Park a card there '
            'while you try a different approach, and restore it if you want to compare.'),
    PageBreak(),
]

# ══════════════════════════════════════════════════════════════════════════════
# 8. Multi-Select
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h1('8. Multi-Select'),
    rule(),
    h2('Entering Select Mode'),
    body('Click the <b>Select</b> button in the toolbar. Each card gains a checkbox in its '
         'top-left corner. Click any card (or its checkbox) to select it. Click again to '
         'deselect. Press <b>Cmd+A</b> to select all visible cards at once.'),
    sp(6),
    h2('Batch Actions'),
    body('When at least one card is selected, a batch action bar appears below the toolbar '
         'showing the number of selected cards and two actions:'),
    bullet('<b>Delete</b> — permanently removes all selected cards after confirmation.'),
    bullet('<b>&#8594; Limbo</b> — moves all selected cards to the Limbo panel.'),
    sp(6),
    h2('Exiting Select Mode'),
    body('Press <b>Escape</b> or click the Select button again to exit select mode. '
         'All selections are cleared.'),
    PageBreak(),
]

# ══════════════════════════════════════════════════════════════════════════════
# 9. Card Linking
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h1('9. Card Linking'),
    rule(),
    h2('Creating Links'),
    body('Hover over a card to reveal the action bar, then click <b>link</b>. A link panel '
         'opens showing every other card in the project. Check the cards you want to link '
         'to. Links are bidirectional — linking card A to card B automatically links B to A.'),
    sp(6),
    h2('Link Badge'),
    body('Once a card has links, a <b>&#8596;N</b> badge appears in its top row showing '
         'the number of linked cards. Click the badge to highlight all linked cards on '
         'the board. Click it again or press Escape to clear the highlight.'),
    sp(6),
    h2('Removing Links'),
    body('Open the link panel from the action bar and uncheck any cards you want to unlink.'),
    PageBreak(),
]

# ══════════════════════════════════════════════════════════════════════════════
# 10. Exporting
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h1('10. Exporting'),
    rule(),
    body('Screenplay Cards has three export types, all accessible from the toolbar or '
         'the Card menu. Every export opens in Preview, giving you the full macOS print '
         'dialog (paper size, page range, print to PDF, etc.). '
         'Exports always respect the active act filter.'),
    sp(8),
    h2('Beat Sheet'),
    body('A clean list of card titles only, one per line, with act headers and scene numbers. '
         'Use this as a quick reference or to share the bare structure with a collaborator.'),
    sp(6),
    h2('Step Outline'),
    body('Card titles plus notes, with full rich text formatting (bold, italic, underline, '
         'line breaks). Each card\'s notes appear below its title. Page numbers are included. '
         'A <b>color legend appendix</b> at the end lists every accent color used in the '
         'project alongside its label, so readers know what each color represents.'),
    sp(6),
    h2('Scene Summary'),
    body('An act-by-act breakdown showing the scene count and coverage percentage for each act. '
         'Useful for checking structural balance at a glance.'),
    sp(4),
    tip_box('To export only a single act, click that act in the filter strip before exporting. '
            'All three export formats will include only the cards from the filtered act.'),
    PageBreak(),
]

# ══════════════════════════════════════════════════════════════════════════════
# 11. Spellcheck & Formatting
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h1('11. Spellcheck & Text Formatting'),
    rule(),
    h2('Spellcheck'),
    body('Spellcheck is always on. Misspelled words are underlined in red. '
         'Right-click any underlined word for a list of suggestions. You can also '
         'select "Add to Dictionary" to teach the app a word it doesn\'t recognize — '
         'useful for character names and screenplay-specific terms.'),
    sp(6),
    h2('Rich Text in Notes'),
    body('Notes fields support basic rich text formatting. Right-click anywhere in a '
         'notes field to access:'),
    bullet('<b>Bold</b> — Cmd+B also works'),
    bullet('<b>Italic</b> — Cmd+I also works'),
    bullet('<b>Underline</b> — Cmd+U also works'),
    bullet('Text alignment: Left, Center, Right, Justify'),
    sp(4),
    body('Formatting is preserved in step outline exports.'),
    sp(6),
    h2('Font Size'),
    body('Each card has its own font size, controlled by the <b>&#8249; N &#8250;</b> '
         'arrows in the action bar (hover to reveal). Click once for a single step up or '
         'down, or hold the arrow for continuous adjustment. Range is 10–48px.'),
    PageBreak(),
]

# ══════════════════════════════════════════════════════════════════════════════
# 12. Files & Auto-Update
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h1('12. Files & Auto-Update'),
    rule(),
    h2('Saving & Opening'),
    body('Projects are saved as <b>.screenplaycards</b> files. Use <b>File &gt; Save</b> '
         '(Cmd+S) or <b>Save As</b> to choose a location. The app autosaves while you work '
         'but it\'s good practice to save explicitly before closing.'),
    sp(4),
    body('To open a project, use <b>File &gt; Open</b> (Cmd+O), or double-click a '
         '.screenplaycards file in Finder. Recent files are accessible under <b>File &gt; '
         'Open Recent</b> and in the welcome panel.'),
    sp(6),
    h2('Cloud Storage'),
    body('The .screenplaycards format works naturally with iCloud Drive, Dropbox, and '
         'Google Drive — just save your file into your synced folder. If you open a file '
         'that has been modified on disk since you last saved (e.g., synced from another '
         'machine), the app will warn you before overwriting.'),
    sp(6),
    h2('Auto-Update'),
    body('Screenplay Cards checks for updates a few seconds after launch. If a new version '
         'is available, a dialog will tell you what\'s changed and ask if you\'d like to '
         'download it. The update downloads in the background and installs the next time '
         'you quit the app.'),
    sp(4),
    tip_box('If the auto-updater ever shows an error, you can always download the latest '
            'version manually from petercarrillo.github.io/screenplay-cards.'),
    PageBreak(),
]

# ══════════════════════════════════════════════════════════════════════════════
# 13. Keyboard Shortcuts
# ══════════════════════════════════════════════════════════════════════════════
story += [
    h1('13. Keyboard Shortcuts'),
    rule(),
    sp(4),
    kv_table([
        ('Cmd+S',         'Save'),
        ('Cmd+Shift+S',   'Save As'),
        ('Cmd+O',         'Open'),
        ('Cmd+Z',         'Undo'),
        ('Cmd+Shift+Z',   'Redo'),
        ('Cmd+Y',         'Redo (alternate)'),
        ('Cmd+B',         'Bold (notes field)'),
        ('Cmd+I',         'Italic (notes field)'),
        ('Cmd+U',         'Underline (notes field)'),
        ('Tab',           'Insert new card after current card (title focused)'),
        ('Cmd+A',         'Select all cards (select mode)'),
        ('Escape',        'Close open panel / clear filter / exit select mode'),
    ]),
    sp(24),
    rule(),
    sp(6),
    Paragraph(
        'Screenplay Cards was designed and built by Peter Carrillo, a screenwriter '
        'who should have been working on his screenplay\'s structure but instead made '
        'an app no one asked for that helps screenwriters organize screenplay structure. '
        'The code was written with the assistance of AI tools.',
        sCaption),
    sp(4),
    Paragraph('screenplaycards@gmail.com &nbsp;&middot;&nbsp; '
              'petercarrillo.github.io/screenplay-cards &nbsp;&middot;&nbsp; '
              'ko-fi.com/screenplaycards', sCaption),
]

# ── Build PDF ─────────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    OUT,
    pagesize=letter,
    leftMargin=inch, rightMargin=inch,
    topMargin=inch, bottomMargin=0.75*inch,
    title='Screenplay Cards User Guide',
    author='Peter Carrillo',
)

doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f'Written: {OUT}')
