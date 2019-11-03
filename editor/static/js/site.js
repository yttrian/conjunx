function Editor() {
    this.init()
}

Editor.prototype.init = function () {
    this.getClipBrowser();
};

Editor.prototype.getClipBrowser = function () {
    var clipBrowser = $('#clip-browser');

    $.get('./clip', function (data) {
        clipBrowser.innerText = data;
    });
};

var editor = new Editor();