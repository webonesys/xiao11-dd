
```python
from flask import Flask, request, send_file, jsonify, session, redirect
import os
import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('APP_SECRET', 'my-secret-key')
PASSWORD = os.environ.get('APP_PASSWORD', '281003361')

UPLOAD_FOLDER = '/tmp/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'zip', 'rar', 'mp4', 'mp3', 'md'}

def check_login():
    return session.get('logged_in') == True

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == PASSWORD:
            session['logged_in'] = True
            return redirect('/')
        return '密码错误', 401
    return LOGIN_PAGE

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/login')

@app.route('/')
def index():
    if not check_login():
        return redirect('/login')
    return MAIN_PAGE

@app.route('/upload', methods=['POST'])
def upload():
    if not check_login():
        return jsonify({'error': '未登录'}), 401
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '未选择文件'})
    if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED:
        filename = secure_filename(file.filename)
        if os.path.exists(os.path.join(UPLOAD_FOLDER, filename)):
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{datetime.datetime.now().strftime('%H%M%S')}{ext}"
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return jsonify({'success': True, 'name': filename})
    return jsonify({'error': '不支持的文件类型'})

@app.route('/files')
def list_files():
    if not check_login():
        return jsonify({'error': '未登录'}), 401
    files = []
    if os.path.exists(UPLOAD_FOLDER):
        for f in sorted(os.listdir(UPLOAD_FOLDER), key=lambda x: os.path.getctime(os.path.join(UPLOAD_FOLDER, x)), reverse=True):
            fp = os.path.join(UPLOAD_FOLDER, f)
            if os.path.isfile(fp):
                files.append({'name': f, 'size': os.path.getsize(fp), 'time': datetime.datetime.fromtimestamp(os.path.getctime(fp)).strftime('%m-%d %H:%M')})
    return jsonify(files)

@app.route('/download/<name>')
def download(name):
    if not check_login():
        return '未登录', 401
    fp = os.path.join(UPLOAD_FOLDER, name)
    if os.path.exists(fp):
        return send_file(fp, as_attachment=True)
    return '文件不存在', 404

@app.route('/delete/<name>', methods=['POST'])
def delete(name):
    if not check_login():
        return jsonify({'error': '未登录'}), 401
    fp = os.path.join(UPLOAD_FOLDER, name)
    if os.path.exists(fp):
        os.remove(fp)
        return jsonify({'success': True})
    return jsonify({'error': '文件不存在'})

LOGIN_PAGE = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width">
<title>登录</title>
<style>
body{margin:0;display:flex;align-items:center;justify-content:center;height:100vh;background:linear-gradient(135deg,#667eea,#764ba2);font-family:system-ui;}
.box{background:#fff;padding:40px;border-radius:16px;box-shadow:0 10px 40px rgba(0,0,0,0.2);width:320px;text-align:center;}
h2{margin:0 0 10px;color:#333;}
p{color:#888;margin:0 0 20px;font-size:14px;}
input{width:100%;padding:12px;border:2px solid #e0e0e0;border-radius:8px;margin-bottom:15px;font-size:16px;box-sizing:border-box;text-align:center;}
input:focus{outline:none;border-color:#667eea;}
``` 

```python
button{width:100%;padding:12px;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border:none;border-radius:8px;font-size:16px;cursor:pointer;}
</style></head>
<body>
<div class="box">
<h2>🔐 私人文件空间</h2>
<p>请输入密码</p>
<form method="POST">
<input type="password" name="password" placeholder="密码" required autofocus>
<button type="submit">进入</button>
</form>
</div>
</body></html>"""

MAIN_PAGE = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width">
<title>私人文件空间</title>
<style>
{margin:0;padding:0;box-sizing:border-box;}
body{font-family:system-ui;background:#f5f5f5;padding:20px;}
.header{max-width:900px;margin:0 auto 20px;display:flex;justify-content:space-between;align-items:center;}
h1{color:#667eea;}
.logout{color:#667eea;text-decoration:none;}
.box{max-width:900px;margin:0 auto 20px;background:#fff;padding:25px;border-radius:12px;box-shadow:0 2px 10px rgba(0,0,0,0.1);}
.drop{border:2px dashed #ccc;border-radius:8px;padding:40px;text-align:center;cursor:pointer;transition:.3s;}
.drop:hover{border-color:#667eea;background:#f8f9ff;}
.drop.dragover{background:#e8ebff;border-color:#667eea;}
button{background:#667eea;color:#fff;border:none;padding:10px 20px;border-radius:6px;cursor:pointer;font-size:14px;}
button:hover{opacity:.9;}
.btn-red{background:#ff6b6b;}
.file{display:flex;align-items:center;padding:12px;background:#f8f9ff;margin:8px 0;border-radius:8px;transition:.2s;}
.file:hover{transform:translateX(5px);}
.file-icon{font-size:24px;margin-right:12px;}
.file-info{flex:1;}
.file-name{font-weight:bold;color:#333;}
.file-meta{color:#888;font-size:12px;}
.file-actions{display:flex;gap:8px;}
.empty{text-align:center;padding:40px;color:#888;}

toast{position:fixed;top:20px;right:20px;background:#333;color:#fff;padding:12px 20px;border-radius:8px;display:none;z-index:1000;}
</style></head>
<body>
<div class="header">
<h1>📁 私人文件空间</h1>
<a href="/logout" class="logout">退出</a>
</div>

<div class="box">
<div class="drop" id="dropZone" onclick="document.getElementById('fileInput').click()">
<p style="font-size:48px;margin-bottom:10px;">📤</p>
<p>点击或拖拽文件上传</p>
<p style="color:#888;font-size:14px;margin-top:8px;">支持: txt, pdf, 图片, 文档, 压缩包等</p>
<input type="file" id="fileInput" style="display:none" multiple>
</div>
</div>

<div class="box">
<h3 style="margin-bottom:15px;color:#333;">文件列表</h3>
<div id="fileList"><div class="empty">暂无文件，请上传</div></div>
</div>

<div id="toast"></div>

<script>
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');

dropZone.ondragover = (e) => { e.preventDefault(); dropZone.classList.add('dragover'); };
dropZone.ondragleave = () => dropZone.classList.remove('dragover');
dropZone.ondrop = (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if(e.dataTransfer.files.length) upload(e.dataTransfer.files[0]);
};

fileInput.onchange = (e) => { if(e.target.files[0]) upload(e.target.files[0]); };

function upload(file) {
    const d = new FormData();
    d.append('file', file);
    fetch('/upload', {method:'POST', body:d})
    .then(r => r.json())
    .then(data => {
        if(data.success) { showToast('上传成功!'); loadFiles(); }
        else showToast(data.error || '上传失败');
    });
}

function loadFiles() {
    fetch('/files').then(r => r.json()).then(files => {
        const el = document.getElementById('fileList');
        if(!files.length) { el.innerHTML = '<div class="empty">暂无文件</div>'; return; }
        el.innerHTML = files.map(f => {
            const size = f.size < 1024*1024 ? (f.size/1024).toFixed(1)+'KB' : (f.size/(1024*1024)).toFixed(1)+'MB';
            return
```
```python
`<div class="file">
                <span class="file-icon">📄</span>
                <div class="file-info">
                    <div class="file-name">${f.name}</div>
                    <div class="file-meta">${size} · ${f.time}</div>
                </div>
                <div class="file-actions">
                    <button onclick="location.href='/download/${encodeURIComponent(f.name)}'">下载</button>
                    <button class="btn-red" onclick="del('${f.name}')">删除</button>
                </div>
            </div>`;
        }).join('');
    });
}

function del(name) {
    if(!confirm('删除 '+name+'?')) return;
    fetch('/delete/'+encodeURIComponent(name), {method:'POST'})
    .then(r => r.json()).then(() => { showToast('已删除'); loadFiles(); });
}

function showToast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg; t.style.display='block';
    setTimeout(() => t.style.display='none', 2000);
}

loadFiles();
</script>
</body></html>"""
```

