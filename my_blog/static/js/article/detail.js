function confirmDeleteComment(commentId) {
    if (typeof layer === 'undefined') {
        return;
    }
    layer.open({
        title: '确认删除',
        content: '确认删除该评论吗？',
        btn: ['确认', '取消'],
        yes: function (index) {
            var button = document.querySelector('form#safe_delete_comment_' + commentId + ' button');
            if (button) {
                button.click();
            }
            layer.close(index);
        },
        no: function (index) {
            layer.close(index);
        }
    });
}

function confirmDeleteArticle() {
    if (typeof layer === 'undefined') {
        return;
    }
    layer.open({
        title: '确认删除',
        content: '确认删除这篇文章吗？',
        btn: ['确认', '取消'],
        yes: function () {
            alert('请使用安全删除功能');
        },
        no: function (index) {
            layer.close(index);
        }
    });
}

document.addEventListener('click', function (event) {
    var commentTrigger = event.target.closest('[data-action="comment-delete"]');
    if (commentTrigger) {
        event.preventDefault();
        var commentId = commentTrigger.getAttribute('data-comment-id');
        if (commentId) {
            confirmDeleteComment(commentId);
        }
        return;
    }

    var articleTrigger = event.target.closest('[data-action="article-delete"]');
    if (articleTrigger) {
        event.preventDefault();
        confirmDeleteArticle();
    }
});
