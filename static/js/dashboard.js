document.getElementById('inputForm').addEventListener('submit', function (event) {
    event.preventDefault();
    var accessToken = document.getElementById('accessToken').value;
    var username = document.getElementById('username').value;
    var timezone = document.getElementById('timezone').value;
    var year = document.getElementById('year').value;

    // Hide the form
    document.getElementById('inputForm').style.display = 'none';
    // Show the loader and loading text
    document.querySelector('.loader').style.display = 'block';
    document.querySelector('.loading-text').style.display = 'block';

    // Messages to display
    var messages = [
        "Loading data, please sit down and relax",
        "数据加载中，请坐和放宽",
        "Chargement des données, veuillez vous asseoir et vous détendre",
        "Cargando datos, por favor siéntese y relájese",
        "データを読み込んでいます、座ってリラックスしてください",
        "데이터를로드 중입니다. 앉아서 편안하게하세요",
        "Загрузка данных, пожалуйста, сядьте и расслабьтесь",
    ];
    var messageIndex = 0;

    // Function to change the loading text
    function changeLoadingText() {
        document.querySelector('.loading-text').textContent = messages[messageIndex];
        messageIndex = (messageIndex + 1) % messages.length;
    }

    // Change the loading text every 1.5 seconds
    setInterval(changeLoadingText, 1500);

    fetch("/load", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            access_token: accessToken,
            username: username,
            timezone: timezone,
            year: year
        })
    })
        .then(response => response.json())
        .then(data => {
            window.location.href = data.redirect_url;
        })
        .catch(error => {
            document.querySelector('.loader').style.display = 'none';
            messages = [
                "An error occurred while loading data, check your python console for more information",
            ];
            console.error('Error:', error);
        });
});