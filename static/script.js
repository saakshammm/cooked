// static/script.js
// cooked — your meanest friend who loves you

(function () {
    'use strict';

    var form = document.getElementById('roast-form');
    var fileInput = document.getElementById('chat-file');
    var uploadBox = document.getElementById('upload-box');
    var uploadTitle = document.getElementById('upload-title');
    var chatTypeRadios = document.getElementsByName('chat_type');
    var userHidden = document.getElementById('user-id-hidden');
    var uploadSection = document.getElementById('upload-section');
    var resultsSection = document.getElementById('results-section');
    var roastBtn = document.getElementById('roast-btn');
    var btnText = roastBtn.querySelector('.roast-btn-text');
    var btnLoading = roastBtn.querySelector('.roast-btn-loading');
    var errorBox = document.getElementById('error-box');
    var resetBtn = document.getElementById('reset-btn');
    var downloadBtn = document.getElementById('download-btn');

    // file selected
    fileInput.addEventListener('change', function () {
        if (fileInput.files && fileInput.files.length > 0) {
            uploadTitle.textContent = fileInput.files[0].name;
            uploadBox.classList.add('has-file');
            sniffUser();
        } else {
            uploadTitle.textContent = 'drop your exported chat here';
            uploadBox.classList.remove('has-file');
        }
    });

    // drag and drop
    uploadBox.addEventListener('dragover', function (e) { e.preventDefault(); uploadBox.classList.add('dragover'); });
    uploadBox.addEventListener('dragleave', function () { uploadBox.classList.remove('dragover'); });
    uploadBox.addEventListener('drop', function (e) {
        e.preventDefault();
        uploadBox.classList.remove('dragover');
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            fileInput.files = e.dataTransfer.files;
            uploadTitle.textContent = e.dataTransfer.files[0].name;
            uploadBox.classList.add('has-file');
            sniffUser();
        }
    });

    // auto-detect who the uploader is
    async function sniffUser() {
        var file = fileInput.files[0];
        if (!file) return;
        try {
            var chunk = file.slice(0, 20480);
            var text = await chunk.text();
            var names = pullNames(text);
            if (names.length > 0) {
                var counts = {};
                var lines = text.split('\n');
                var pat = /(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}),?\s+\d{1,2}:\d{2}(?::\d{2})?\s?[APap][Mm]\s*[-–]\s*(.+?):/;
                for (var i = 0; i < lines.length; i++) {
                    var m = lines[i].match(pat);
                    if (m) {
                        var sender = m[2].trim();
                        counts[sender] = (counts[sender] || 0) + 1;
                    }
                }
                var topSender = names[0];
                var topCount = 0;
                for (var k in counts) {
                    if (counts[k] > topCount) { topCount = counts[k]; topSender = k; }
                }
                userHidden.value = topSender;
            }
        } catch (e) {
            userHidden.value = '';
        }
    }

    function pullNames(raw) {
        var lines = raw.split('\n');
        var names = new Set();
        var pat = /(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}),?\s+\d{1,2}:\d{2}(?::\d{2})?\s?[APap][Mm]\s*[-–]\s*(.+?):/;
        for (var i = 0; i < lines.length; i++) {
            var m = lines[i].match(pat);
            if (m) names.add(m[2].trim());
        }
        return Array.from(names);
    }

    // submit
    form.addEventListener('submit', async function (e) {
        e.preventDefault();
        if (!fileInput.files || fileInput.files.length === 0) {
            errorBox.textContent = 'you forgot to drop a chat file. we need something to cook.';
            errorBox.classList.remove('hidden');
            return;
        }
        errorBox.classList.add('hidden');
        roastBtn.disabled = true;
        btnText.classList.add('hidden');
        btnLoading.classList.remove('hidden');

        var formData = new FormData(form);
        try {
            var resp = await fetch('/analyze', { method: 'POST', body: formData });
            var data = await resp.json();
            if (!resp.ok || data.error) throw new Error(data.error || 'the kitchen caught fire. try again.');
            renderResults(data);
            uploadSection.classList.add('hidden');
            resultsSection.classList.remove('hidden');
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } catch (err) {
            errorBox.textContent = err.message || 'something broke. try again.';
            errorBox.classList.remove('hidden');
        } finally {
            roastBtn.disabled = false;
            btnText.classList.remove('hidden');
            btnLoading.classList.add('hidden');
        }
    });

    // reset
    resetBtn.addEventListener('click', function () {
        resultsSection.classList.add('hidden');
        uploadSection.classList.remove('hidden');
        errorBox.classList.add('hidden');
        form.reset();
        uploadTitle.textContent = 'drop your exported chat here';
        uploadBox.classList.remove('has-file');
        userHidden.value = '';
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // download card
    downloadBtn.addEventListener('click', function () {
        var card = document.getElementById('report-card');
        html2canvas(card, { backgroundColor: '#121214', scale: 2 }).then(function (canvas) {
            var a = document.createElement('a');
            a.download = 'cooked-report-2026.png';
            a.href = canvas.toDataURL('image/png');
            a.click();
        }).catch(function () {
            errorBox.textContent = 'could not save. just screenshot it.';
            errorBox.classList.remove('hidden');
        });
    });

    // render
    function renderResults(d) {
        var score = d.delusion_score || 50;
        document.getElementById('delusion-score').innerHTML =
            '<span class="score-number">' + score + '</span><span class="score-symbol">%</span>';
        document.getElementById('meter-fill').style.width = score + '%';

        var grid = document.getElementById('stats-grid');
        grid.innerHTML = '';

        function card(label, value, cooked) {
            var el = document.createElement('div'); el.className = 'stat-card';
            var n = document.createElement('div'); n.className = 'stat-name'; n.textContent = label;
            var v = document.createElement('div'); v.className = 'stat-val' + (cooked ? ' cooked' : ''); v.textContent = value;
            el.appendChild(n); el.appendChild(v); return el;
        }

        function cardNote(label, value, note, cooked) {
            var el = card(label, value, cooked);
            if (note) {
                var p = document.createElement('div'); p.className = 'stat-note'; p.textContent = note; el.appendChild(p);
            }
            return el;
        }

        grid.appendChild(card('double texts', d.double_texts, d.double_texts > 5));

        if (d.aura_loss && d.aura_loss < 0) {
            grid.appendChild(card('aura lost', d.aura_loss, true));
            if (d.aura_reason) grid.appendChild(cardNote('how', 'fumbled', d.aura_reason, true));
        }

        grid.appendChild(card('carried by you', d.carrier_percent + '% of the energy', d.carrier_percent > 60));

        if (d.reply_gap && d.reply_gap.comment) {
            grid.appendChild(cardNote('reply gap', 'you: ' + d.reply_gap.user_avg + ' / them: ' + d.reply_gap.other_avg, d.reply_gap.comment, true));
        }

        if (d.dry_texter_meter) {
            var dryCooked = d.dry_texter_meter.indexOf('CRITICAL') === 0 || d.dry_texter_meter.indexOf('high') === 0;
            grid.appendChild(card('dry texter', d.dry_texter_meter, dryCooked));
        }

        if (d.attachment_imbalance && d.attachment_imbalance !== 'mutual effort, surprisingly.' && d.attachment_imbalance !== 'surprisingly mutual effort. rare sighting.') {
            grid.appendChild(card('who cares more', d.attachment_imbalance, true));
        }

        if (d.sleep_damage) grid.appendChild(card('sleep damage', d.sleep_damage, true));
        if (d.brainrot) grid.appendChild(card('brainrot check', d.brainrot, false));

        if (d.crashout && d.crashout.crashout) {
            grid.appendChild(cardNote('crashout', d.crashout.time, d.crashout.reason, true));
        }

        if (d.locked_in && d.locked_in.locked_in) {
            grid.appendChild(card('locked in', d.locked_in.comment, false));
        }

        if (d.group_insights) {
            var g = d.group_insights;
            grid.appendChild(card('most annoying', g.most_annoying, true));
            grid.appendChild(card('biggest yapper', g.biggest_yapper, true));
            grid.appendChild(card('ghoster', g.ghoster, true));
            grid.appendChild(card('dry texter award', g.dry_texter, true));
            grid.appendChild(card('meme dealer', g.meme_dealer, false));
            grid.appendChild(card('npc of the group', g.certified_npc, false));
            if (g.hidden_crashout && g.hidden_crashout.indexOf('none') === -1) {
                grid.appendChild(card('closet crashout', g.hidden_crashout, true));
            }
        }

        document.getElementById('verdict-block').textContent = 'final verdict: ' + (d.verdict || 'somehow unroastable');
    }
})();