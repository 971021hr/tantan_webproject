// 전역 변수 - api키 발급받아서 사용하기
const WEATHER_KEY = '2b158b5fc703abf1e0b455e7d5100f13';
// 변수
const weatherIcon = document.querySelector('#weatherIcon'),
    weatherTemp = document.querySelector('#weatherTemp'),
    FeelsLike = document.querySelector('#feels-like');
weatherLocation = document.querySelector('#weatherLocation');

// 옵션
var options = {
    enableHighAccuracy: true,
    timeout: 3000,
    maximumAge: 0
};

// 성공 시
function success(position) {
    let latitude = position.coords.latitude;
    let longitude = position.coords.longitude;
    let weatherIcon = {
        '01' : 'fas fa-sun fa-3x',
        '02' : 'fas fa-cloud-sun fa-3x',
        '03' : 'fas fa-cloud fa-3x',
        '04' : 'fas fa-cloud-meatball fa-3x',
        '09' : 'fas fa-cloud-sun-rain fa-3x',
        '10' : 'fas fa-cloud-showers-heavy fa-3x',
        '11' : 'fas fa-poo-storm fa-3x' ,
        '13' : 'far fa-snowflake fa-3x',
        '50' : 'fas fa-smog fa-3x'
    };

    // 패치 사용
    fetch(
        `https://api.openweathermap.org/data/2.5/weather?lat=${latitude}&lon=${longitude}&appid=${WEATHER_KEY}&units=metric`
    ).then(function(response){
        //network 정보 => json으로 변경
        return response.json();
    }).then(function(json){
        // 출력
        var $Icon = (json.weather[0].icon).substr(0,2);
        //weatherIcon.innerHTML = `<img src="http://openweathermap.org/img/wn/${weatherIcon}.png"/>`;
        weatherTemp.innerHTML = Math.round(json.main.temp) + '℃'; //반올림
        // weatherLocation.innerHTML = `${json.sys.country}, ${json.name}`;
        weatherLocation.innerHTML = `${json.name}`;
        // icon.innerHTML = '<img src="http://openweathermap.org/img/wn/${weatherIcon}.png">';
        FeelsLike.append(`${json.main.feels_like}℃`);
        $('#weatherIcon').append('<i class="' + weatherIcon[$Icon] + '"></i>');
    });
};

// 실패 시
function error(err) {
    notification.innerHTML = `<p> ${err.message} 정보를 불러오지 못했습니다. </p>`;
    console.warn('ERROR(' + err.code + '): ' + err.message);
};

navigator.geolocation.getCurrentPosition(success, error, options);