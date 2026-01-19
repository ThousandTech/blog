document.addEventListener('click', function (event) {
    var trigger = event.target.closest('[data-action="user-delete"]');
    if (!trigger) {
        return;
    }
    event.preventDefault();
    if (typeof layer === 'undefined') {
        return;
    }
    layer.open({
        title: '确认删除',
        content: '确认删除用户资料吗？',
        btn: ['确认', '取消'],
        yes: function (index) {
            var button = document.querySelector('form#user_delete button');
            if (button) {
                button.click();
            }
            layer.close(index);
        },
        no: function (index) {
            layer.close(index);
        }
    });
});
