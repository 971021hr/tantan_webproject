const BUS_KEY = 't%2FeadELVB156TD%2BnnFn1v2%2BUipLI%2FkOC%2BmZ3Bdt5jmWmdbtmOeUHizTI6Ijnlczgb8AOADE7zPP4ImfVv%2BbgJw%3D%3D';
const BusStationId = '108000021';
const BUSAPI = 'http://ws.bus.go.kr/api/rest/arrive/getLowArrInfoByStId';

//const bus_url = BUSAPI + '?ServiceKey=' + BUS_KEY + '&stId=' + BusStationId;

const bus_url = 'http://ws.bus.go.kr/api/rest/arrive/getLowArrInfoByStId?ServiceKey=t%2FeadELVB156TD%2BnnFn1v2%2BUipLI%2FkOC%2BmZ3Bdt5jmWmdbtmOeUHizTI6Ijnlczgb8AOADE7zPP4ImfVv%2BbgJw%3D%3D&stId=108000021';


var bus_array = '';

/*http://ws.bus.go.kr/api/rest/arrive/getLowArrInfoByStId?ServiceKey=${API_KEY}&stId=112000001
http://ws.bus.go.kr/api/rest/arrive/getLowArrInfoByStId?ServiceKey=t%2FeadELVB156TD%2BnnFn1v2%2BUipLI%2FkOC%2BmZ3Bdt5jmWmdbtmOeUHizTI6Ijnlczgb8AOADE7zPP4ImfVv%2BbgJw%3D%3D&stId=112000001*/

/*stId 정류소id
stNm 정류소명 bus_station_name
rtNm 버스번호
arrmsg1 첫번재 도착 예정 시각
arrmsg2 두번째 도착 예정 시각
*/

/*
var options = {
    enableHighAccuracy: true,
    timeout: 8000,
    maximumAge: 0
};

*/


/*
fetch(bus_url,{
        mode : 'no-cors',
    headers:{
        'Accept': 'application/json','Content-Type': 'application/json'
    }
})
    .then(function (res) {
        console.log(res);
        return res.json();
    })
    .then(function (data){
        console.log(data);

    })
    .catch(err => {
        console.log('Fetch Error',err);
    });
*/



function showBus(){
    alert("버스 확인 함수 실행!");

    $("#div_main").hide();

    $("#div_bus").show();
    $("#div_subway").hide();
    $("#div_youtube").hide();

    for (i=0; i<4; i++){
        bus_array += i + '번째 \n';
    }
    $('#bus_info').text(bus_array);
}