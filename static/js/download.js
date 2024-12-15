function download() {
    html2canvas(document.querySelector('main'))
        .then(function (canvas) {
            var link = document.createElement('a');
            link.download = 'main-section.png';
            link.href = canvas.toDataURL();
            link.hidden = true;
            link.click();
        });
}