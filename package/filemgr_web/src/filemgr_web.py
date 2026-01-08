import http.server
import socketserver
import os
import urllib.parse
import mimetypes
import time
import html
import shutil
import re

PORT = 8080
ROOT = "/files"
ICONS_URL = "/files/icons"
ICONS_FS = os.path.join(ROOT, "icons")

EXT_ICONS = {
    ".txt": "textfile.png",
    ".py": "textfile.png",
    ".md": "textfile.png",
    ".png": "image.png",
    ".jpg": "image.png",
    ".jpeg": "image.png",
    ".pdf": "pdf.png",
}

class Handler(http.server.SimpleHTTPRequestHandler):

    def translate_path(self, path):
        path = urllib.parse.unquote(path.split("?", 1)[0])
        return os.path.normpath(os.path.join(ROOT, path.lstrip("/")))

    # =========================
    # DIRECTORY LISTING
    # =========================
    def list_directory(self, path):
        try:
            entries = sorted(os.listdir(path), key=str.lower)
        except OSError:
            self.send_error(403)
            return

        rel = os.path.relpath(path, ROOT)
        url_path = "/" if rel == "." else "/" + rel.replace(os.sep, "/")
        parent_url = "/" if path == ROOT else "/" + os.path.relpath(os.path.dirname(path), ROOT).replace(os.sep, "/")

        html_out = f"""
<html>
<head>
<meta charset="utf-8">
<title>Files</title>
<style>
body {{ font-family: sans-serif; }}
table {{ width: 100%; border-collapse: collapse; }}
th, td {{ padding: 4px; text-align: left; }}
tr.selected {{ background: #ffd; }}
a {{ text-decoration: none; color: black; }}
.toolbar button {{ margin-right: 5px; }}
.toolbar img.button {{
    width: 20px;
    vertical-align: middle;
    cursor: pointer;
    margin-left: 5px;
}}
#context {{
    position: fixed;
    display: none;
    background: #fff;
    border: 1px solid #888;
    box-shadow: 2px 2px 6px rgba(0,0,0,.2);
    z-index: 1000;
}}
#context button {{
    display: block;
    width: 100%;
    border: none;
    background: none;
    padding: 6px 12px;
    text-align: left;
}}
#context button:hover {{ background: #eee; }}
</style>
</head>
<body>

<div class="toolbar">
<button onclick="location.href='{parent_url}'" {'disabled' if path == ROOT else ''}>⬅ Parent</button>
<button onclick="location.reload()">⟳ Refresh</button>
<img src="{ICONS_URL}/textfile.png" title="New file" class="button" onclick="createFile()">
<img src="{ICONS_URL}/folder.png" title="New folder" class="button" onclick="createFolder()">

<form method="POST" enctype="multipart/form-data" style="display:inline;" id="uploadForm">
  <input type="file" name="uploadfile" id="uploadInput" style="display:none"
         onchange="document.getElementById('uploadForm').submit()">
  <button type="button" onclick="document.getElementById('uploadInput').click()">Upload</button>
</form>
</div>

<h3>Index of {html.escape(url_path)}</h3>

<table>
<tr><th></th><th>Name</th><th>Size</th><th>Modified</th></tr>
"""

        rows = []
        for name in entries:
            full = os.path.join(path, name)
            is_dir = os.path.isdir(full)
            ext = os.path.splitext(name)[1].lower()
            icon = "folder.png" if is_dir else EXT_ICONS.get(ext, "textfile.png")

            size = "-" if is_dir else str(os.path.getsize(full))
            mtime = time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(full)))

            href = urllib.parse.quote(url_path.rstrip("/") + "/" + name)
            if is_dir:
                href += "/"

            rows.append(f"""
<tr data-name="{html.escape(name)}" data-href="{href}">
<td><img src="{ICONS_URL}/{icon}" width="16"></td>
<td><a href="{href}">{html.escape(name)}</a></td>
<td>{size}</td>
<td>{mtime}</td>
</tr>
""")

        html_out += "".join(rows) + """
</table>

<div id="context">
<button onclick="ctxRename()">Rename</button>
<button onclick="ctxEdit()">Modify</button>
<button onclick="ctxDelete()">Delete</button>
</div>

<script>
let current = null;

// Context menu
document.querySelectorAll("tr[data-name]").forEach(row => {
  row.oncontextmenu = e => {
    e.preventDefault();
    current = row.dataset.name;
    let c = document.getElementById("context");
    c.style.left = e.pageX + "px";
    c.style.top = e.pageY + "px";
    c.style.display = "block";
  };
});

document.onclick = () => document.getElementById("context").style.display = "none";

function post(action, data) {
  let f = document.createElement("form");
  f.method = "POST";
  for (let k in data) {
    let i = document.createElement("input");
    i.type = "hidden";
    i.name = k;
    i.value = data[k];
    f.appendChild(i);
  }
  let a = document.createElement("input");
  a.type = "hidden";
  a.name = "action";
  a.value = action;
  f.appendChild(a);
  document.body.appendChild(f);
  f.submit();
}

function ctxRename() {
  let n = prompt("New name:", current);
  if (n) post("rename", { old: current, new: n });
}

function ctxDelete() {
  if (confirm("Delete " + current + "?"))
    post("delete", { target: current });
}

function ctxEdit() {
  let row = document.querySelector(`tr[data-name="${current}"]`);
  if (row) location.href = row.dataset.href + "?edit=1";
}

function createFile() {
  let name = prompt("File name:");
  if (!name) return;
  let content = prompt("Initial content:", "") || "";
  post("create", { name: name, content: content });
}

function createFolder() {
  let name = prompt("Folder name:");
  if (!name) return;
  post("mkdir", { name: name });
}
</script>

</body></html>
"""

        data = html_out.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    # =========================
    # FILE VIEW / EDIT
    # =========================
    def serve_file(self, path):
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        edit = "edit" in qs

        rel = os.path.relpath(path, ROOT)
        parent = "/" + os.path.relpath(os.path.dirname(path), ROOT).replace(os.sep, "/")

        ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"

        html_out = f"<html><body><button onclick=\"location.href='{parent}'\">⬅ Back</button><hr>"

        if edit and ctype.startswith("text"):
            with open(path, "r", errors="replace") as f:
                content = f.read()
            html_out += f"""
<form method="POST">
<input type="hidden" name="action" value="save">
<textarea name="content" style="width:100%;height:80vh">{html.escape(content)}</textarea><br>
<button type="submit">Save</button>
</form>
"""
        elif ctype.startswith("text"):
            with open(path, "r", errors="replace") as f:
                html_out += "<pre>" + html.escape(f.read()) + "</pre>"
        elif ctype.startswith("image"):
            html_out += f'<img src="{self.path}">'
        else:
            html_out += "<p>Binary file — preview not supported.</p>"

        html_out += "</body></html>"

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html_out.encode())

    # =========================
    # UPLOAD SUPPORT
    # =========================
    def save_uploaded_file(self, path):
        boundary = self.headers.get_boundary()
        if not boundary:
            return False
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        parts = body.split(b"--" + boundary.encode())
        for part in parts:
            if b'filename=' in part:
                name = re.search(b'filename="([^"]+)"', part)
                if not name:
                    continue
                filename = name.group(1).decode()
                data = part.split(b"\r\n\r\n", 1)[1].rsplit(b"\r\n", 1)[0]
                with open(os.path.join(path, filename), "wb") as f:
                    f.write(data)
                return True
        return False

    # =========================
    # POST
    # =========================
    def do_POST(self):
        path = self.translate_path(self.path)

        if self.headers.get_content_type().startswith("multipart/form-data"):
            if self.save_uploaded_file(path):
                self.send_response(303)
                self.send_header("Location", self.path.split("?")[0])
                self.end_headers()
                return

        length = int(self.headers.get("Content-Length", 0))
        params = urllib.parse.parse_qs(self.rfile.read(length).decode())
        action = params.get("action", [""])[0]

        try:
            if action == "create":
                with open(os.path.join(path, params["name"][0]), "w") as f:
                    f.write(params.get("content", [""])[0])
            elif action == "mkdir":
                os.mkdir(os.path.join(path, params["name"][0]))
            elif action == "rename":
                os.rename(os.path.join(path, params["old"][0]),
                          os.path.join(path, params["new"][0]))
            elif action == "delete":
                t = os.path.join(path, params["target"][0])
                shutil.rmtree(t) if os.path.isdir(t) else os.remove(t)
            elif action == "save":
                with open(path, "w") as f:
                    f.write(params["content"][0])
        except Exception as e:
            self.send_error(500, str(e))
            return

        self.send_response(303)
        self.send_header("Location", self.path.split("?")[0])
        self.end_headers()

    # =========================
    # GET
    # =========================
    def do_GET(self):
        if self.path.startswith("/files/icons/"):
            fs = os.path.join(ROOT, self.path[len("/files/"):])
            if os.path.isfile(fs):
                with open(fs, "rb") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", mimetypes.guess_type(fs)[0])
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return

        path = self.translate_path(self.path)
        
        if os.path.isfile(path) and mimetypes.guess_type(path)[0] and mimetypes.guess_type(path)[0].startswith("image"):
            with open(path, "rb") as f:
                data = f.read()
            ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        if os.path.isdir(path):
            self.list_directory(path)
        elif os.path.isfile(path):
            self.serve_file(path)
        else:
            self.send_error(404)

os.makedirs(ROOT, exist_ok=True)
os.makedirs(ICONS_FS, exist_ok=True)

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving {ROOT} at http://0.0.0.0:{PORT}")
    httpd.serve_forever()

