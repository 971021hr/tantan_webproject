
const SUBWAY_KEY = '6441514e666872393130375077635a49';
const TYPE = 'json';
const SERVICE = 'realtimeStationArrival';
const START_INDEX = 0;
const END_INDEX = 5;
const STATION = '솔밭공원';
const url = 'http://swopenapi.seoul.go.kr/api/subway/';

var SUBWAY_INFO1= '';
var SUBWAY_INFO1 = '';
var SUBWAY_INFO2 = '';
var SUBWAY_INFO3 = '';

const subway_url = url + SUBWAY_KEY + '/' + TYPE + '/' + SERVICE + '/' + START_INDEX + '/'+END_INDEX + '/' + STATION;
//http://swopenapi.seoul.go.kr/api/subway/6441514e666872393130375077635a49/json/realtimeStationArrival/0/5/솔밭공원


//setInterval(function(){
    fetch(subway_url,{
        headers:{
            'Accept': 'application/json'
        }
    })
        .then(function (res) {
            return res.json();
        })
        .then(function (data){
            $('#subway_name').text(STATION+ ' 역');

            SUBWAY_INFO0 = '방향 : ' + data.realtimeArrivalList[0].trainLineNm + ' 열차 위치 : ' + data.realtimeArrivalList[0].arvlMsg2;
            $('#arr00_div').text(SUBWAY_INFO0);

            SUBWAY_INFO1 = '방향 : ' + data.realtimeArrivalList[1].trainLineNm + ' 열차 위치 : ' + data.realtimeArrivalList[1].arvlMsg2;
            $('#arr01_div').text(SUBWAY_INFO1);

            SUBWAY_INFO2 = '방향 : ' + data.realtimeArrivalList[2].trainLineNm + ' 열차 위치 : ' + data.realtimeArrivalList[2].arvlMsg2;
            $('#arr02_div').text(SUBWAY_INFO2);

            SUBWAY_INFO3 = '방향 : ' + data.realtimeArrivalList[3].trainLineNm + ' 열차 위치 : ' + data.realtimeArrivalList[3].arvlMsg2;
            $('#arr03_div').text(SUBWAY_INFO3);




        })
        .catch(err => {
            console.log('Fetch Error',err);
        });
//},5000);

function showSubway(){

    $("#div_main").hide();

    $("#div_subway").show();
    $("#div_calendar").hide();
    $("#div_dandan").hide();
    $("#div_speech").hide();
    $("#div_dandan_squat").hide();

    //운동 리스트 hide
    $("#exerciselist").hide();
    $("#circle1").hide();
    $("#circle2").hide();
    $("#circle3").hide();
    $("#circle4").hide();
    $("#mirror_2m").hide();
}