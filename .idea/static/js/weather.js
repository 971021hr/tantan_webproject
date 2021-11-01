// 전역 변수 - api키 발급받아서 사용하기
const WEATHER_KEY = 'WEATHER_KEY';
// 변수
const
    //weatherIcon = document.querySelector('#weatherIcon'),
    weatherTemp = document.querySelector('#weatherTemp'),
    FeelsLike = document.querySelector('#feels-like');
weatherLocation = document.querySelector('#weatherLocation');

// 성공 시
function success(position) {

    let latitude = position.coords.latitude;
    let longitude = position.coords.longitude;

    setInterval(function(){
        // 패치 사용
        fetch(
            `https://api.openweathermap.org/data/2.5/weather?lat=${latitude}&lon=${longitude}&appid=${WEATHER_KEY}&units=metric`
        ).then(function(response){
            //network 정보 => json으로 변경
            return response.json();
        }).then(function(json){
            let icon = document.querySelector('#weatherIcon');
            let wIcon = json.weather[0].icon;

            weatherTemp.innerHTML = Math.round(json.main.temp) + '℃'; //반올림
            weatherLocation.innerHTML = `${json.name}`;
            FeelsLike.innerHTML = `${json.main.feels_like}℃`;
            icon.innerHTML = `<img src='http://openweathermap.org/img/wn/${wIcon}.png'>`;


        });
    },5000);

};

// 실패 시
function error(err) {
    notification.innerHTML = `<p> ${err.message} 정보를 불러오지 못했습니다. </p>`;
    console.warn('ERROR(' + err.code + '): ' + err.message);
};

navigator.geolocation.getCurrentPosition(success, error);