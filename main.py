# ============================================================
# InstaLeads Hunter - RENDER VERSION (Backend + Frontend)
# ------------------------------------------------------------
# YE FILE RENDER.COM KE LIYE HAI (free plan).
# Is me Flask backend AUR poora tool ka page dono hain.
# Koi BACKEND_URL set nahi karna, koi alag file nahi.
#
# RENDER PAR CHALANAY KA TAREEQA:
#   1. GitHub.com par free account banayein, "instaleads-hunter"
#      naam ka naya repository banayein
#   2. Is folder ki DONO files (main.py + requirements.txt)
#      GitHub par upload karein (Add file > Upload files)
#   3. Render.com par (GitHub se sign in karein) >
#      New > Web Service > apna repo select karein
#   4. Build Command: pip install -r requirements.txt
#      Start Command: python main.py
#      Instance Type: Free
#   5. Create Web Service > 2-3 minute wait > URL mil jaye ga
#      (jaise https://instaleads-hunter.onrender.com)
#   6. Blogger gadget me iframe wali line me ye URL daal dein
#
# NOTE: Render ka free plan 15 minute idle ke baad so jata hai,
# pehli request par ~30-60 second lag sakte hain. Ye free ki
# qeemat hai - ghabrana nahi, page khud jag jata hai.
# ============================================================

import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import instaloader
from instaloader.exceptions import (
    InstaloaderException,
    LoginRequiredException,
    QueryReturnedNotFoundException,
    ConnectionException,
)

app = Flask(__name__)
CORS(app)

MAX_COMMENTS = 300  # Ek dafa me zyada se zyada 300 comments


def extract_shortcode(url):
    """Kisi bhi Instagram link (Reel / Post / Carousel) se shortcode nikalein."""
    if not url:
        return None
    url = url.strip()

    match = re.search(
        r"(?:instagram\.com|instagr\.am)/(?:reel|reels|p|tv)/([A-Za-z0-9_-]+)",
        url,
    )
    if match:
        return match.group(1)

    # Sirf shortcode paste ho to wohi use karein
    if re.fullmatch(r"[A-Za-z0-9_-]{5,}", url):
        return url

    return None


# ============================================================
# FRONTEND - poora tool ka page (HTML + CSS + JavaScript)
# Yehi page Replit par khulay ga. Is me koi BACKEND_URL
# set karne ki zaroorat nahi - request isi server par jati hai.
# ============================================================
PAGE_HTML = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>InstaLeads Hunter - All-in-One Comment Extractor</title>
<style>
  body{margin:0;background:#faf7f8;padding:18px 12px}
</style>
<!-- InstaLeads Hunter - All-in-One Comment Extractor (COMBINED) -->
<style>
  #ilh-app{font-family:'Segoe UI',Arial,Helvetica,sans-serif;color:#222;max-width:900px;margin:0 auto;box-sizing:border-box}
  #ilh-app *{box-sizing:border-box}
  .ilh-head{background:linear-gradient(135deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888);color:#fff;border-radius:16px;padding:22px 20px;text-align:center;margin-bottom:16px}
  .ilh-head h2{margin:0 0 6px;font-size:26px;letter-spacing:.3px}
  .ilh-head p{margin:0;font-size:14px;opacity:.95}
  .ilh-card{background:#fff;border:1px solid #eee;border-radius:16px;padding:18px;box-shadow:0 4px 18px rgba(0,0,0,.06);margin-bottom:16px}
  .ilh-label{font-weight:700;font-size:14px;margin:0 0 6px;display:block}
  .ilh-input,.ilh-select{width:100%;padding:12px 14px;border:1.5px solid #ddd;border-radius:10px;font-size:15px;outline:none}
  .ilh-input:focus,.ilh-select:focus{border-color:#dc2743}
  .ilh-row{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}
  .ilh-row>*{flex:1 1 200px}
  .ilh-btn{border:0;border-radius:10px;padding:13px 18px;font-size:15px;font-weight:700;cursor:pointer;transition:.15s}
  .ilh-btn-main{background:linear-gradient(135deg,#f09433,#dc2743,#bc1888);color:#fff;width:100%;margin-top:14px;font-size:16px}
  .ilh-btn-main:hover{opacity:.92}
  .ilh-btn-main:disabled{opacity:.6;cursor:not-allowed}
  .ilh-btn-tool{background:#f3f3f7;color:#333}
  .ilh-btn-tool:hover{background:#e9e9f0}
  .ilh-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
  .ilh-stat{background:linear-gradient(135deg,#fdf2f5,#fff7ed);border:1px solid #f3e2e8;border-radius:14px;padding:14px;text-align:center}
  .ilh-stat b{display:block;font-size:26px;color:#c81e5b}
  .ilh-stat span{font-size:13px;color:#666}
  .ilh-spinner{display:none;text-align:center;padding:18px;font-size:15px;color:#555}
  .ilh-spinner .ilh-ring{display:inline-block;width:26px;height:26px;border:3px solid #f3c2d3;border-top-color:#dc2743;border-radius:50%;animation:ilh-spin 1s linear infinite;vertical-align:middle;margin-right:8px}
  @keyframes ilh-spin{to{transform:rotate(360deg)}}
  .ilh-error{display:none;background:#fdecea;color:#a81e2c;border:1px solid #f5c2c7;border-radius:10px;padding:12px 14px;font-size:14px;margin-bottom:16px}
  .ilh-ok{display:none;background:#e9f8ef;color:#146c35;border:1px solid #bfe6cb;border-radius:10px;padding:10px 14px;font-size:14px;margin-bottom:16px;text-align:center}
  .ilh-table-wrap{overflow-x:auto}
  .ilh-table{width:100%;border-collapse:collapse;font-size:14px;min-width:620px}
  .ilh-table th{background:#faf7f8;text-align:left;padding:10px 8px;border-bottom:2px solid #eee;white-space:nowrap}
  .ilh-table td{padding:9px 8px;border-bottom:1px solid #f0f0f0;vertical-align:top}
  .ilh-table td.ilh-comment{white-space:pre-wrap;word-break:break-word;max-width:340px}
  .ilh-table a{color:#c81e5b;text-decoration:none;font-weight:600}
  .ilh-copy{border:0;background:#f3f3f7;border-radius:8px;padding:6px 12px;cursor:pointer;font-size:13px;font-weight:600}
  .ilh-copy:hover{background:#e9e9f0}
  .ilh-count{font-size:13px;color:#777;margin:0 0 8px}
  .ilh-empty{text-align:center;color:#888;padding:26px 10px;font-size:14px}
  @media(max-width:600px){
    .ilh-head h2{font-size:22px}
    .ilh-stats{grid-template-columns:1fr 1fr 1fr}
    .ilh-stat b{font-size:20px}
  }
</style>

<div id="ilh-app">
  <div class="ilh-head">
    <h2>📸 InstaLeads Hunter</h2>
    <p>All-in-One Comment Extractor — works for any niche</p>
  </div>

  <div class="ilh-card">
    <label class="ilh-label" for="ilh-link">Instagram Link (any Reel / Post / Carousel)</label>
    <input class="ilh-input" id="ilh-link" type="text" placeholder="https://www.instagram.com/reel/..." />
    <div class="ilh-row">
      <div>
        <label class="ilh-label" for="ilh-filter">Smart Filter</label>
        <select class="ilh-select" id="ilh-filter">
          <option value="all">All Comments</option>
          <option value="buyers">Buyers (price, buy, want, link, pp, cost, how much)</option>
          <option value="questions">Questions</option>
          <option value="custom">Custom Keywords</option>
        </select>
      </div>
      <div id="ilh-custom-wrap" style="display:none">
        <label class="ilh-label" for="ilh-custom">Custom keywords (comma separated)</label>
        <input class="ilh-input" id="ilh-custom" type="text" placeholder="e.g. discount, order, available" />
      </div>
    </div>
    <button class="ilh-btn ilh-btn-main" id="ilh-extract">🔍 Extract All Comments</button>
  </div>

  <div class="ilh-spinner" id="ilh-loading"><span class="ilh-ring"></span> Extracting comments, please wait…</div>
  <div class="ilh-error" id="ilh-error"></div>
  <div class="ilh-ok" id="ilh-done"></div>

  <div class="ilh-card" id="ilh-results" style="display:none">
    <div class="ilh-stats">
      <div class="ilh-stat"><b id="ilh-total">0</b><span>Total Comments</span></div>
      <div class="ilh-stat"><b id="ilh-filtered">0</b><span>Filtered Results</span></div>
      <div class="ilh-stat"><b id="ilh-unique">0</b><span>Unique Users</span></div>
    </div>
    <div class="ilh-row" style="margin-top:14px">
      <input class="ilh-input" id="ilh-search" type="text" placeholder="🔎 Search inside results (username or comment)…" />
    </div>
    <div class="ilh-row">
      <button class="ilh-btn ilh-btn-tool" id="ilh-csv">⬇ Download CSV</button>
      <button class="ilh-btn ilh-btn-tool" id="ilh-txt">⬇ Download TXT</button>
      <button class="ilh-btn ilh-btn-tool" id="ilh-copy-users">📋 Copy All Usernames</button>
      <button class="ilh-btn ilh-btn-tool" id="ilh-copy-filtered">📋 Copy Filtered Comments</button>
    </div>
    <p class="ilh-count" id="ilh-count" style="margin-top:14px"></p>
    <div class="ilh-table-wrap">
      <table class="ilh-table">
        <thead>
          <tr><th>No</th><th>Username</th><th>Comment</th><th>Profile Link</th><th>Action</th></tr>
        </thead>
        <tbody id="ilh-tbody"></tbody>
      </table>
    </div>
    <p class="ilh-empty" id="ilh-empty" style="display:none">No comments match this filter.</p>
  </div>
</div>

<script>
(function(){
  // COMBINED version: frontend aur backend ek hi server par hain,
  // is liye koi BACKEND_URL set karne ki zaroorat nahi.
  var BACKEND_URL = "";

  var BUYER_KEYWORDS = ["price", "buy", "want", "link", "pp", "cost", "how much"];
  var QUESTION_WORDS = ["what","how","where","when","why","who","which","can","could","is","are","do","does","did","will","would","should"];

  var allComments = [];
  var filteredComments = [];

  var $ = function(id){ return document.getElementById(id); };

  function showError(msg){ var e=$("ilh-error"); e.textContent=msg; e.style.display="block"; $("ilh-done").style.display="none"; }
  function hideError(){ $("ilh-error").style.display="none"; }
  function showDone(msg){ var d=$("ilh-done"); d.textContent=msg; d.style.display="block"; }

  function escapeHtml(s){
    return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
  }

  function copyText(text, okMsg){
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function(){ showDone(okMsg); })
      .catch(function(){ fallbackCopy(text, okMsg); });
    } else { fallbackCopy(text, okMsg); }
  }
  function fallbackCopy(text, okMsg){
    var ta = document.createElement("textarea");
    ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
    document.body.appendChild(ta); ta.select();
    try { document.execCommand("copy"); showDone(okMsg); }
    catch(e){ showError("Copy failed — please copy manually."); }
    document.body.removeChild(ta);
  }

  function isQuestion(text){
    var t = text.trim().toLowerCase();
    if (t.indexOf("?") !== -1) return true;
    var first = t.split(/\s+/)[0] || "";
    return QUESTION_WORDS.indexOf(first) !== -1;
  }

  function applyFilter(){
    var mode = $("ilh-filter").value;
    var list = allComments.slice();
    if (mode === "buyers") {
      list = list.filter(function(c){
        var t = c.text.toLowerCase();
        return BUYER_KEYWORDS.some(function(k){ return t.indexOf(k) !== -1; });
      });
    } else if (mode === "questions") {
      list = list.filter(function(c){ return isQuestion(c.text); });
    } else if (mode === "custom") {
      var keys = $("ilh-custom").value.split(",").map(function(k){ return k.trim().toLowerCase(); }).filter(Boolean);
      if (keys.length) {
        list = list.filter(function(c){
          var t = c.text.toLowerCase();
          return keys.some(function(k){ return t.indexOf(k) !== -1; });
        });
      }
    }
    filteredComments = list;

    $("ilh-total").textContent = allComments.length;
    $("ilh-filtered").textContent = filteredComments.length;
    var users = {};
    filteredComments.forEach(function(c){ users[c.username] = true; });
    $("ilh-unique").textContent = Object.keys(users).length;

    renderTable();
  }

  function renderTable(){
    var q = $("ilh-search").value.trim().toLowerCase();
    var view = filteredComments.filter(function(c){
      if (!q) return true;
      return c.username.toLowerCase().indexOf(q) !== -1 || c.text.toLowerCase().indexOf(q) !== -1;
    });
    $("ilh-count").textContent = "Showing " + view.length + " of " + filteredComments.length + " filtered results";
    $("ilh-empty").style.display = view.length ? "none" : "block";

    var html = "";
    view.forEach(function(c, i){
      html += "<tr><td>" + (i + 1) + "</td>"
        + "<td><a href='" + escapeHtml(c.profile_url) + "' target='_blank' rel='noopener'>@" + escapeHtml(c.username) + "</a></td>"
        + "<td class='ilh-comment'>" + escapeHtml(c.text) + "</td>"
        + "<td><a href='" + escapeHtml(c.profile_url) + "' target='_blank' rel='noopener'>View Profile</a></td>"
        + "<td><button class='ilh-copy' data-i='" + i + "'>Copy</button></td></tr>";
    });
    $("ilh-tbody").innerHTML = html;

    var btns = $("ilh-tbody").querySelectorAll(".ilh-copy");
    btns.forEach(function(btn){
      btn.addEventListener("click", function(){
        var c = view[parseInt(btn.getAttribute("data-i"), 10)];
        copyText("@" + c.username + ": " + c.text, "Comment copied!");
      });
    });
  }

  function csvEscape(v){
    v = String(v == null ? "" : v);
    return '"' + v.replace(/"/g, '""') + '"';
  }

  function download(filename, content, type){
    var blob = new Blob([content], { type: type });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(function(){ URL.revokeObjectURL(a.href); }, 1000);
  }

  $("ilh-filter").addEventListener("change", function(){
    $("ilh-custom-wrap").style.display = (this.value === "custom") ? "block" : "none";
    if (allComments.length) applyFilter();
  });
  $("ilh-custom").addEventListener("input", function(){ if (allComments.length) applyFilter(); });
  $("ilh-search").addEventListener("input", renderTable);

  $("ilh-extract").addEventListener("click", function(){
    var link = $("ilh-link").value.trim();
    hideError();
    if (!link) { showError("Please paste an Instagram link first."); return; }
    var btn = $("ilh-extract");
    btn.disabled = true; btn.textContent = "Extracting…";
    $("ilh-loading").style.display = "block";
    $("ilh-results").style.display = "none";

    fetch(BACKEND_URL + "/get_comments?url=" + encodeURIComponent(link))
      .then(function(res){ return res.json(); })
      .then(function(data){
        if (data.status !== "ok") throw new Error(data.message || "Backend returned an error.");
        allComments = data.comments || [];
        $("ilh-results").style.display = "block";
        applyFilter();
        showDone("Done! " + allComments.length + " comments extracted.");
      })
      .catch(function(err){
        showError("Could not extract comments: " + err.message + " (Make sure the app is running on Replit, then try again.)");
      })
      .finally(function(){
        btn.disabled = false; btn.textContent = "🔍 Extract All Comments";
        $("ilh-loading").style.display = "none";
      });
  });

  $("ilh-csv").addEventListener("click", function(){
    if (!filteredComments.length) { showError("Nothing to download — extract comments first."); return; }
    var rows = ["No,Username,Comment,Profile Link"];
    filteredComments.forEach(function(c, i){
      rows.push([i + 1, "@" + c.username, c.text, c.profile_url].map(csvEscape).join(","));
    });
    download("instaleads-comments.csv", rows.join("\r\n"), "text/csv;charset=utf-8");
    showDone("CSV downloaded!");
  });

  $("ilh-txt").addEventListener("click", function(){
    if (!filteredComments.length) { showError("Nothing to download — extract comments first."); return; }
    var txt = filteredComments.map(function(c){ return "@" + c.username + ": " + c.text; }).join("\n");
    download("instaleads-comments.txt", txt, "text/plain;charset=utf-8");
    showDone("TXT downloaded!");
  });

  $("ilh-copy-users").addEventListener("click", function(){
    if (!filteredComments.length) { showError("Nothing to copy — extract comments first."); return; }
    var users = [];
    filteredComments.forEach(function(c){
      var u = "@" + c.username;
      if (users.indexOf(u) === -1) users.push(u);
    });
    copyText(users.join("\n"), users.length + " usernames copied!");
  });

  $("ilh-copy-filtered").addEventListener("click", function(){
    if (!filteredComments.length) { showError("Nothing to copy — extract comments first."); return; }
    var txt = filteredComments.map(function(c){ return "@" + c.username + ": " + c.text; }).join("\n");
    copyText(txt, filteredComments.length + " filtered comments copied!");
  });
})();
</script>
</body>
</html>
'''


@app.route("/")
def home():
    """Tool ka page - yehi Replit par khulay ga."""
    return PAGE_HTML


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "InstaLeads Hunter (combined)"})


@app.route("/get_comments")
def get_comments():
    """Public Instagram post se zyada se zyada 300 comments layein.

    Query param: ?url=INSTAGRAM_URL
    Returns:
      {"status": "ok", "total": 42, "comments": [
          {"username": "...", "text": "...",
           "profile_url": "https://www.instagram.com/.../"}, ...]}
    """
    url = request.args.get("url", "").strip()

    if not url:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Missing 'url' parameter. Example: "
                    "/get_comments?url=https://www.instagram.com/reel/ABC123/",
                }
            ),
            400,
        )

    shortcode = extract_shortcode(url)
    if not shortcode:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Invalid Instagram link. Use a Reel, Post or "
                    "Carousel link (instagram.com/reel/... or /p/...).",
                }
            ),
            400,
        )

    try:
        loader = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            quiet=True,
        )

        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        comments = []
        for comment in post.get_comments():
            comments.append(
                {
                    "username": comment.owner.username,
                    "text": comment.text,
                    "profile_url": f"https://www.instagram.com/{comment.owner.username}/",
                }
            )
            if len(comments) >= MAX_COMMENTS:
                break

        return jsonify({"status": "ok", "total": len(comments), "comments": comments})

    except LoginRequiredException:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "This post is private or requires an Instagram login. "
                    "Only public posts can be extracted without logging in.",
                }
            ),
            403,
        )
    except QueryReturnedNotFoundException:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Post not found. The link may be wrong, or the post "
                    "was deleted or removed.",
                }
            ),
            404,
        )
    except ConnectionException:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Instagram blocked the request (rate limit). "
                    "Please wait a few minutes and try again.",
                }
            ),
            429,
        )
    except InstaloaderException as e:
        return jsonify({"status": "error", "message": f"Instagram error: {e}"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": f"Could not fetch comments: {e}"}), 500


if __name__ == "__main__":
    # Render apni marzi ka PORT deta hai (environment variable me).
    # PORT na mile to 8080 use karein.
    import os

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
