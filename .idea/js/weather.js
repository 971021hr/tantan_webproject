// 전역 변수 - api키 발급받아서 사용하기
const WEATHER_KEY = '2b158b5fc703abf1e0b455e7d5100f13';
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
    // let wIcon = {
    //     '01' : 'fas fa-sun fa-3x',
    //     '02' : 'fas fa-cloud-sun fa-3x',
    //     '03' : 'fas fa-cloud fa-3x',
    //     '04' : 'fas fa-cloud-meatball fa-3x',
    //     '09' : 'fas fa-cloud-sun-rain fa-3x',
    //     '10' : 'fas fa-cloud-showers-heavy fa-3x',
    //     '11' : 'fas fa-poo-storm fa-3x' ,
    //     '13' : 'far fa-snowflake fa-3x',
    //     '50' : 'fas fa-smog fa-3x'
    // };
    setInterval(function(){
        console.log('semi & minhyun');
        // 패치 사용
        fetch(
            `https://api.openweathermap.org/data/2.5/weather?lat=${latitude}&lon=${longitude}&appid=${WEATHER_KEY}&units=metric`
        ).then(function(response){
            //network 정보 => json으로 변경
            return response.json();
        }).then(function(json){
            let icon = document.querySelector('#weatherIcon');
            let wIcon = json.weather[0].icon;
            // 출력
            //var $Icon = (json.weather[0].icon).substr(0,2);
            //var semi = wIcon[$icon];
            //weatherIcon.innerHTML = wIcon[$Icon];
            weatherTemp.innerHTML = Math.round(json.main.temp) + '℃'; //반올림
            // weatherLocation.innerHTML = `${json.sys.country}, ${json.name}`;
            weatherLocation.innerHTML = `${json.name}`;
            FeelsLike.innerHTML = `${json.main.feels_like}℃`;
            //$('#weatherIcon').innerHTML = `${wIcon[$Icon]}`;
            //$('#icon').innerHTML = `<i class="' + weatherIcon[$Icon] + '"></i>`;
            icon.innerHTML = `<img src='http://openweathermap.org/img/wn/${wIcon}.png'>`;

            //FeelsLike.append(`${json.main.feels_like}℃`);
            //$('#icon').append('<i class="' + wIcon[$Icon] + '"></i>');
            ///$('#weatherIcon').append('<i class="' + wIcon[$Icon] + '"></i>');

        });
    },5000);
    // $('#weatherIcon').append('<i class="' + weatherIcon[$Icon] + '"></i>');
};

// 실패 시
function error(err) {
    notification.innerHTML = `<p> ${err.message} 정보를 불러오지 못했습니다. </p>`;
    console.warn('ERROR(' + err.code + '): ' + err.message);
};

navigator.geolocation.getCurrentPosition(success, error);