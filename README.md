# Galley

**A LaTeX editor that runs in your browser — on a phone, a tablet or a laptop. No account, no install, nothing to pay.**

Keep as many projects as you like, write LaTeX, add photos and other files, press **Compile**, and read the PDF right beside your source. Every compile is saved to the project's History on your device, so you can go back to any earlier version.

**Try it:** https://cosmicsapian.github.io/galley/

<!-- Add a screenshot here once the site is live, e.g. ![Galley on a laptop and a phone](docs/screenshot.png) -->

---

## Features

**Projects**
- Galley opens on your Projects page, with a preview of each document's first page
- Start a new project from a template (sample, article, slides, letter or blank), or open a `.zip`
- Rename, duplicate, download or delete any project
- Reloading the page keeps you in the project you were working on

**Writing**
- Code editor with LaTeX syntax highlighting, line numbers and bracket matching
- A key bar for the symbols that are hard to type on a phone: `\` `{ }` `[ ]` `$ $` `^` `_` `&`
- One-tap snippets: fractions, equations, aligned equations, lists, tables, sections, citations
- Several files per project: `.tex`, `.bib`, `.sty`, `.cls` and more, with any top-level `.tex` file set as the main one
- Each file tab has a menu to rename, move, download or delete that file

**Images and files**
- Organise files in folders; new images go into a `figures` folder automatically
- Sort by name, type, size or newest, and collapse folders you don't need
- Select several files at once to move or delete them, or drag them onto a folder
- Moving or renaming a file updates the `\includegraphics`, `\input` and `\bibliography` lines that point to it
- Files that no `.tex` file uses are marked **Not used**, so they're easy to clean up
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
- Select and copy text from the PDF
- Links work: references, citations and the table of contents jump to their place, and web links open in a new tab
- Keeps your place in the PDF when you recompile
- Open the PDF in a new tab, download it, or share it from your phone

**History**
- Each project keeps its own History; every compile is saved with its files and its PDF
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
| Copy text from the PDF | Select it, then Ctrl/⌘ + C |
| Close a panel | Esc |

---

## Host your own copy

Galley is a static site: an HTML page, a service worker, a manifest and three icons. Any static host works. The `server` folder isn't needed for hosting; it's for running your own compile server on your computer.

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

- **Compiling** happens on a server, because a full TeX Live installation is several gigabytes. By default Galley sends your files to [LaTeX-On-HTTP](https://github.com/YtoTech/latex-on-http), a free public compile service at `latex.ytotech.com`, and receives the finished PDF back. If that server doesn't answer, Galley tries again, then switches to your backup server if you've set one. `server/galley-server.py` is a small server of your own that speaks the same API.
- **Everything else** runs in your browser. Your projects, files, settings and History are stored on your device in IndexedDB. Nothing is uploaded to any account, because there isn't one.
- **The editor and PDF viewer** use [CodeMirror 5](https://codemirror.net/5/) and [PDF.js](https://mozilla.github.io/pdf.js/), loaded from cdnjs. [JSZip](https://stuk.github.io/jszip/) loads only when you open or download a `.zip`.
- **The service worker** caches the app and its libraries, so it opens instantly on later visits.

## Privacy

- Your files leave your device only when you press **Compile**, and only to the compile server.
- The default compile server is a free public service run by a third party. Avoid it for confidential documents, or run your own server (see below).
- There are no accounts, no analytics and no tracking in Galley itself.

## Your own compile server

The free public server is sometimes down for a while. `server/galley-server.py` turns any computer with TeX Live into your own compile server, so Galley keeps working and your files never leave your machine. It is one Python file with no packages to install.

### On your laptop (Ubuntu)

```bash
sudo apt install texlive-full latexmk      # once; texlive-full is about 6 GB
python3 server/galley-server.py
```

It prints an address such as `http://localhost:8080`. In Galley, open **Settings** and paste it as the **Compile server**, or as the **Backup server** if you'd rather keep the public one as your first choice. Press **Test** to check it.

Chrome may ask to let the page "access devices on your local network". Allow it: that is how the page reaches the server on your own computer.

### On your phone or tablet too

Your phone can't reach `localhost` on your laptop, so give the server a temporary public https address with a free [Cloudflare quick tunnel](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/) (no account needed):

```bash
# once: install cloudflared
curl -L -o cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb

python3 server/galley-server.py --tunnel
```

It prints a second address like `https://some-random-words.trycloudflare.com/Xy3…`. Paste the whole address, including the part after the last slash, into Galley's Settings on your phone. That last part is a secret key: without it the server refuses to compile, so only you can use it. The address changes every time you start the server, and it works only while your laptop is on.

### Options

| Option | What it does |
| --- | --- |
| `--port 8080` | Port to listen on |
| `--tunnel` | Also make a public https address with cloudflared, protected by a secret key |
| `--key auto` | Add a secret key to the address without a tunnel |
| `--timeout 120` | Seconds one compile may run |
| `--jobs 2` | Compiles that may run at the same time |

### Safety

LaTeX can read files, so the server locks it into the project: documents can't read anything outside their own folder and TeX Live (`openin_any=p`), `latexmkrc` files are refused and ignored, shell escape stays restricted, and every compile is stopped after the time limit. By default the server only listens on this computer (`127.0.0.1`).

---

## Limits

- **Projects stay on each device.** They don't sync between your phone and your laptop. To move a project, use **⋯ → Download .zip** on one device and **Open .zip** on the other.
- **PDFs are kept for the latest 40 compiles of each project.** Older versions keep their files, and you can restore and recompile them. Each project's History holds up to 300 versions.
- **The main `.tex` file stays at the top level** of the project, because the compile server builds it from there.
- **Compiling needs a compile server.** By default that's the free public one, which needs an internet connection and is sometimes down. With your own server on your laptop, you can compile offline too. You can still open the app and edit offline; your work is saved as you type.
- **The public server has a time limit** of about 100 seconds per compile, and only the packages it has installed. Its package list is at https://latex.ytotech.com/packages.

## Troubleshooting

| Problem | What to do |
| --- | --- |
| "The free public compile server isn't answering" | It's down for a while, usually during an update. Galley already tried twice. Try again later, or start your own server and set it as the backup server in **Settings**, so Galley switches automatically. |
| "Your compile server on this computer isn't answering" | Start `python3 server/galley-server.py` again in a terminal. |
| "Your tunnel address isn't answering" | The tunnel address changes every time the server starts. Copy the new one from the terminal into **Settings**. |
| A package "isn't installed" | Check the spelling. If it is correct, the public server doesn't have that package; consider running your own server. |
| A photo shows the wrong way round | Remove it and add it again through Galley; photos added this way are turned upright. |
| A character won't compile | Switch the compiler to XeLaTeX or LuaLaTeX in the menu above the editor. |
| Projects disappeared on iPhone | Safari cleared them after a week without a visit. Install Galley to your home screen to prevent this. |
| "Galley was updated" screen | Close any other tab where Galley is open; the page carries on by itself. |

---

## Credits

- [LaTeX-On-HTTP](https://github.com/YtoTech/latex-on-http) by YtoTech, for the compile service
- [CodeMirror](https://codemirror.net/), [PDF.js](https://mozilla.github.io/pdf.js/) and [JSZip](https://stuk.github.io/jszip/)
- [TeX Live](https://tug.org/texlive/) and everyone who maintains LaTeX

## License

<!-- Choose a license (for example MIT) and add a LICENSE file to this repository. -->
