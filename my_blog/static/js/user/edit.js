document.addEventListener('DOMContentLoaded', function () {
    var avatarInput = document.getElementById('avatar');
    if (!avatarInput) {
        return;
    }
    avatarInput.addEventListener('change', function (e) {
        var file = e.target.files[0];
        if (!file) {
            return;
        }
        var reader = new FileReader();
        reader.onload = function (ev) {
            var img = document.querySelector('.avatar-wrapper img');
            if (img) {
                img.src = ev.target.result;
            } else {
                var wrapper = document.querySelector('.avatar-wrapper');
                var placeholder = wrapper ? wrapper.querySelector('div.d-flex') : null;
                if (wrapper && placeholder) {
                    var newImg = document.createElement('img');
                    newImg.src = ev.target.result;
                    newImg.alt = '头像';
                    newImg.className = 'rounded-circle border w-100 h-100 avatar-image';
                    wrapper.insertBefore(newImg, placeholder);
                    wrapper.removeChild(placeholder);
                }
            }
            var tip = document.getElementById('avatar-tip');
            if (tip) {
                tip.style.display = 'block';
            }
        };
        reader.readAsDataURL(file);
    });
});
