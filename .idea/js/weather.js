// 전역 변수 - api키 발급받아서 사용하기
const API_KEY = '2b158b5fc703abf1e0b455e7d5100f13';
// 변수
const weatherIcon = document.querySelector('#weatherIcon'),
    weatherTemp = document.querySelector('#weatherTemp'),
    weatherMain = document.querySelector('#weatherMain'),
    weatherDesc = document.querySelector('#weatherDesc'),
    weatherLocation = document.querySelector('#weatherLocation'),
    notification = document.querySelector('.notification');
// 옵션
var options = {
    enableHighAccuracy: true,
    timeout: 8000,
    maximumAge: 0
};

// 성공 시
function success(position) {
    let latitude = position.coords.latitude;
    let longitude = position.coords.longitude;
    // 패치 사용
    fetch(
        `https://api.openweathermap.org/data/2.5/weather?lat=${latitude}&lon=${longitude}&appid=${API_KEY}&units=metric`
    ).then(function(response){
        //network 정보 => json으로 변경
        return response.json();
    }).then(function(json){
        // 출력
        /*weatherIcon.innerHTML = `<img src="img/icon-${json.weather[0].icon}.svg"/>`;*/
        weatherTemp.innerHTML = Math.round(json.main.temp) + '℃'; //반올림
        weatherLocation.innerHTML = `${json.sys.country}, ${json.name}`;
    });
};

// 실패 시
function error(err) {
    notification.innerHTML = `<p> ${err.message} 정보를 불러오지 못했습니다. </p>`;
    console.warn('ERROR(' + err.code + '): ' + err.message);
};

navigator.geolocation.getCurrentPosition(success, error, options);
