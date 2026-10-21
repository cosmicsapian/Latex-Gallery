# Latex-Galley

**A LaTeX editor that runs in your browser — on a phone, a tablet or a laptop. No account, no install, nothing to pay.**

Write LaTeX, add photos and other files, press **Compile**, and read the PDF right beside your source. Every compile is saved to a History on your device, so you can go back to any earlier version.

**Try it:** https://YOUR-USERNAME.github.io/galley/

<!-- Add a screenshot here once the site is live, e.g. ![Galley on a laptop and a phone](docs/screenshot.png) -->

---

## Features

**Writing**
- Code editor with LaTeX syntax highlighting, line numbers and bracket matching
- A key bar for the symbols that are hard to type on a phone: `\` `{ }` `[ ]` `$ $` `^` `_` `&`
- One-tap snippets: fractions, equations, aligned equations, lists, tables, sections, citations
- Projects with several files: `.tex`, `.bib`, `.sty`, `.cls` and more, with any `.tex` file set as the main one

**Images and files**
- Add photos straight from your phone's camera or gallery
- Large photos are resized and turned upright automatically, so they don't appear sideways in the PDF
- Adding an image inserts the `figure` code at your cursor, and adds `\usepackage{graphicx}` if it's missing
- Paste a screenshot into the editor to add it as a figure
- Open and download whole projects as `.zip`, including projects exported from Overleaf

**Compiling**
- Full TeX Live with **pdfLaTeX**, **XeLaTeX** and **LuaLaTeX**
- BibTeX and Biber run automatically
- Errors are listed with their line numbers and a plain-English hint; tap one to jump to that line
- An optional strict mode gives no PDF if LaTeX reports any error

**PDF viewer**
- Sharp rendering on any screen, with pinch-to-zoom on touch screens and Ctrl + scroll on a laptop
- Keeps your place in the PDF when you recompile
- Open the PDF in a new tab, download it, or share it from your phone

**History**
- Every compile is saved with its files and its PDF
- View any earlier version and restore its files with one tap
- Search past versions by document name

**Works everywhere**
- Installs to the home screen on iPhone, iPad and Android, and opens like an app
- Loads instantly after the first visit, even on a slow connection
- Light and dark themes that follow your device

---

## Use it on your phone or tablet

1. Open the link above.
2. Install it:
   - **iPhone / iPad:** in Safari, tap **Share → Add to Home Screen**.
   - **Android:** in Chrome, tap **⋮ → Install app**.

Installing is worth it on iPhone and iPad. Safari may clear a website's saved data after a week without a visit, but it keeps an installed app's data.

## Keyboard shortcuts

| Action | Shortcut |
| --- | --- |
| Compile | Ctrl/⌘ + Enter, or Ctrl/⌘ + S |
| Add a screenshot as a figure | Paste into the editor |
| Close a panel | Esc |

---

## Host your own copy

Galley is a static site: an HTML page, a service worker, a manifest and three icons. Any static host works.

### GitHub Pages (free)

1. Fork this repository, or create a new public repository and upload these files.
2. Go to **Settings → Pages**.
3. Under **Branch**, choose `main` and the `/ (root)` folder, then click **Save**.
4. After about a minute, the site is live at `https://YOUR-USERNAME.github.io/REPOSITORY-NAME/`.

### Other options

- **Netlify, Cloudflare Pages or Vercel:** deploy the folder as-is; there is no build step.
- **On your computer:** open `index.html` directly, or serve the folder with any web server, for example `python3 -m http.server`.

---

## How it works

- **Compiling** happens on a server, because a full TeX Live installation is several gigabytes. By default Galley sends your files to [LaTeX-On-HTTP](https://github.com/YtoTech/latex-on-http), a free public compile service at `latex.ytotech.com`, and receives the finished PDF back.
- **Everything else** runs in your browser. Your files, settings and History are stored on your device in IndexedDB. Nothing is uploaded to any account, because there isn't one.
- **The editor and PDF viewer** use [CodeMirror 5](https://codemirror.net/5/) and [PDF.js](https://mozilla.github.io/pdf.js/), loaded from cdnjs. [JSZip](https://stuk.github.io/jszip/) loads only when you open or download a `.zip`.
- **The service worker** caches the app and its libraries, so it opens instantly on later visits.

## Privacy

- Your files leave your device only when you press **Compile**, and only to the compile server.
- The default compile server is a free public service run by a third party. Avoid it for confidential documents, or run your own server (see below).
- There are no accounts, no analytics and no tracking in Galley itself.

## Use your own compile server

To keep your files entirely under your control, run your own copy of LaTeX-On-HTTP by following the Docker instructions in [its repository](https://github.com/YtoTech/latex-on-http). Then, in Galley, open **⋯ → Compile server** and enter its address.

If Galley is served over `https` (as on GitHub Pages), the compile server must be reachable over `https` too, or the browser will block the request.

---

## Limits

- **History stays on each device.** It doesn't sync between your phone and your laptop. To move a project, use **Files → Download .zip** on one device and **Open .zip** on the other.
- **PDFs are kept for your latest 40 compiles.** Older versions keep their files, and you can restore and recompile them. History holds up to 300 versions.
- **Compiling needs an internet connection.** You can still open the app and edit offline; your work is saved as you type.
- **The public server has a time limit** of about 100 seconds per compile, and only the packages it has installed. Its package list is at https://latex.ytotech.com/packages.

## Troubleshooting

| Problem | What to do |
| --- | --- |
| "Couldn't reach the compile server" | Check your connection and try again. If you changed the server address, check it under **⋯ → Compile server**, or tap **Reset**. |
| A package "isn't installed" | Check the spelling. If it is correct, the public server doesn't have that package; consider running your own server. |
| A photo shows the wrong way round | Remove it and add it again through Galley; photos added this way are turned upright. |
| A character won't compile | Switch the compiler to XeLaTeX or LuaLaTeX in the menu above the editor. |
| History disappeared on iPhone | Safari cleared it after a week without a visit. Install Galley to your home screen to prevent this. |

---

## Credits

- [LaTeX-On-HTTP](https://github.com/YtoTech/latex-on-http) by YtoTech, for the compile service
- [CodeMirror](https://codemirror.net/), [PDF.js](https://mozilla.github.io/pdf.js/) and [JSZip](https://stuk.github.io/jszip/)
- [TeX Live](https://tug.org/texlive/) and everyone who maintains LaTeX

## License

<!-- Choose a license (for example MIT) and add a LICENSE file to this repository. -->
