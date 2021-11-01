var DUST_INFO0 = '';
var DUST_INFO1 = '';
var DUST_INFO2 = '';
var DUST_INFO3 = '';

//ajax코드 적기
$.ajax({
    type: "GET",
    url: "http://openapi.seoul.go.kr:8088/개인키번호/json/RealtimeCityAir/1/99",
    data: {},
    success: function(response){
        // 도봉구의 미세먼지 값만 가져와보기
        setInterval(function(){

            let dobong = response["RealtimeCityAir"]["row"][11];
            let guName = dobong['MSRSTE_NM'];
            let guMise = dobong['PM10'];

            if(guMise < 50) {
                //DUST_INFO0 =  guName + " 미세먼지 : " + guMise + ' 좋음' + '<i className="fa fa-camera"></i>';
                DUST_INFO0 =  "미세먼지 : 좋음(" + guMise + ')';
                $('#dust_dobong').text(DUST_INFO0);

            }else if(50 < guMise < 75) {
                DUST_INFO1 =  "미세먼지 : 나쁨(" + guMise + ')';
                $('#dust_dobong').text(DUST_INFO1);

            }else if(75 < guMise < 100) {
                DUST_INFO2 =  "미세먼지 : 상당히 나쁨(" + guMise + ')';
                $('#dust_dobong').text(DUST_INFO2);

            }else if(guMise > 100) {

                DUST_INFO3 =  "미세먼지 : 최악(" + guMise + ')';
                $('#dust_dobong').text(DUST_INFO3);

            }
        },5000);
    }
})