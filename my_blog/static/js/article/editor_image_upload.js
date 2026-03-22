(function () {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function escapeHtml(text) {
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function renderSimpleMarkdown(markdownText) {
        var escaped = escapeHtml(markdownText || '');
        escaped = escaped.replace(/!\[([^\]]*)\]\(([^)\s]+(?:\s+\"[^\"]*\")?)\)/g, function (_, alt, src) {
            var cleanSrc = src.trim().replace(/^<|>$/g, '');
            return '<img src="' + cleanSrc + '" alt="' + alt + '" style="max-width: 100%; height: auto; border-radius: 4px; margin: 8px 0;">';
        });
        return escaped.replace(/\n/g, '<br>');
    }

    function debounce(fn, wait) {
        var timer = null;
        return function () {
            var args = arguments;
            clearTimeout(timer);
            timer = setTimeout(function () {
                fn.apply(null, args);
            }, wait);
        };
    }

    function setUploadingState(hint, uploading) {
        hint.textContent = uploading ? '正在上传图片，请稍候...' : '';
    }

    function normalizeMarkdown(text) {
        var normalized = text.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
        normalized = normalized.replace(/[ \t]+\n/g, '\n');
        normalized = normalized.replace(/\n{3,}/g, '\n\n');
        return normalized.trim();
    }

    function serializeEditorToMarkdown(editor) {
        function walk(node) {
            var output = '';
            var i;
            if (node.nodeType === Node.TEXT_NODE) {
                return node.nodeValue || '';
            }
            if (node.nodeType !== Node.ELEMENT_NODE) {
                return '';
            }

            var tag = node.tagName.toLowerCase();
            if (tag === 'img') {
                var alt = node.getAttribute('alt') || '';
                var src = node.getAttribute('src') || '';
                if (!src) {
                    return '';
                }
                return '![' + alt + '](' + src + ')';
            }
            if (tag === 'br') {
                return '\n';
            }

            for (i = 0; i < node.childNodes.length; i++) {
                output += walk(node.childNodes[i]);
            }

            if (tag === 'div' || tag === 'p') {
                output += '\n';
            }
            return output;
        }

        var raw = '';
        var j;
        for (j = 0; j < editor.childNodes.length; j++) {
            raw += walk(editor.childNodes[j]);
        }
        return normalizeMarkdown(raw);
    }

    function syncEditorToTextarea(editor, textarea) {
        textarea.value = serializeEditorToMarkdown(editor);
    }

    function insertImageAtCursor(editor, url, altText) {
        editor.focus();
        var selection = window.getSelection();
        var range = null;

        if (selection && selection.rangeCount > 0) {
            var selectedRange = selection.getRangeAt(0);
            if (editor.contains(selectedRange.commonAncestorContainer)) {
                range = selectedRange;
            }
        }

        if (!range) {
            range = document.createRange();
            range.selectNodeContents(editor);
            range.collapse(false);
            if (selection) {
                selection.removeAllRanges();
                selection.addRange(range);
            }
        }

        var img = document.createElement('img');
        img.src = url;
        img.alt = altText || '';
        img.style.maxWidth = '100%';
        img.style.height = 'auto';
        img.style.borderRadius = '4px';
        img.style.margin = '8px 0';
        range.deleteContents();
        range.insertNode(img);
        var br = document.createElement('br');
        img.parentNode.insertBefore(br, img.nextSibling);
        range.setStartAfter(br);
        range.collapse(true);
        if (selection) {
            selection.removeAllRanges();
            selection.addRange(range);
        }
    }

    function uploadAndInsertImage(file, altText, uploadUrl, editor, textarea, hint, onAfterInsert) {
        if (!file || !file.type || file.type.indexOf('image/') !== 0) {
            hint.textContent = '仅支持图片文件。';
            return Promise.resolve(false);
        }

        var formData = new FormData();
        formData.append('image', file);

        setUploadingState(hint, true);
        return fetch(uploadUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            credentials: 'same-origin'
        })
            .then(function (response) {
                return response.json().then(function (data) {
                    return { ok: response.ok, data: data };
                });
            })
            .then(function (result) {
                if (!result.ok || !result.data.success) {
                    hint.textContent = (result.data && result.data.message) ? result.data.message : '上传失败，请重试。';
                    return false;
                }
                insertImageAtCursor(editor, result.data.url, altText || '');
                syncEditorToTextarea(editor, textarea);
                if (typeof onAfterInsert === 'function') {
                    onAfterInsert();
                }
                hint.textContent = '图片已插入正文。';
                return true;
            })
            .catch(function () {
                hint.textContent = '上传失败，请检查网络后重试。';
                return false;
            })
            .finally(function () {
                setUploadingState(hint, false);
            });
    }

    document.addEventListener('DOMContentLoaded', function () {
        var textarea = document.getElementById('body');
        var editor = document.getElementById('body-editor');
        var hint = document.getElementById('body-image-upload-hint');
        var dropHint = document.getElementById('body-drop-hint');
        if (!textarea || !editor || !hint || !dropHint) {
            return;
        }
        var uploadUrl = editor.getAttribute('data-upload-url');
        if (!uploadUrl) {
            return;
        }

        editor.innerHTML = renderSimpleMarkdown(textarea.value);
        if (!editor.innerHTML.trim()) {
            editor.innerHTML = '<br>';
        }

        var syncMarkdown = debounce(function () {
            syncEditorToTextarea(editor, textarea);
        }, 120);

        syncMarkdown();
        editor.addEventListener('input', syncMarkdown);

        editor.addEventListener('dragover', function (event) {
            event.preventDefault();
            dropHint.textContent = '松开鼠标即可上传并插入图片...';
        });

        editor.addEventListener('dragleave', function () {
            dropHint.textContent = '支持将图片直接拖拽到正文，也支持 Ctrl+V 粘贴截图。';
        });

        editor.addEventListener('drop', function (event) {
            event.preventDefault();
            dropHint.textContent = '支持将图片直接拖拽到正文，也支持 Ctrl+V 粘贴截图。';
            if (!event.dataTransfer || !event.dataTransfer.files || event.dataTransfer.files.length === 0) {
                return;
            }
            var file = event.dataTransfer.files[0];
            uploadAndInsertImage(file, '', uploadUrl, editor, textarea, hint, syncMarkdown);
        });

        editor.addEventListener('paste', function (event) {
            var items = event.clipboardData && event.clipboardData.items ? event.clipboardData.items : [];
            var i;
            for (var i = 0; i < items.length; i++) {
                if (items[i].type && items[i].type.indexOf('image/') === 0) {
                    var imageFile = items[i].getAsFile();
                    if (imageFile) {
                        event.preventDefault();
                        uploadAndInsertImage(imageFile, '', uploadUrl, editor, textarea, hint, syncMarkdown);
                        break;
                    }
                }
            }

            if (event.defaultPrevented) {
                return;
            }

            var plainText = event.clipboardData ? event.clipboardData.getData('text/plain') : '';
            if (plainText) {
                event.preventDefault();
                document.execCommand('insertText', false, plainText);
                syncMarkdown();
            }
        });

        editor.addEventListener('blur', function () {
            syncEditorToTextarea(editor, textarea);
        });

        var form = editor.closest('form');
        if (form) {
            form.addEventListener('submit', function () {
                syncEditorToTextarea(editor, textarea);
            });
        }
    });
})();
