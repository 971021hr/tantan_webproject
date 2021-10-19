function showDandan(){

    $("#div_main").show();
    $("#div_dandan").show();

    //운동 리스트 hide
    $("#exerciselist").hide();
    $("#circle1").hide();
    $("#circle2").hide();
    $("#circle3").hide();
    $("#circle4").hide();
    $("#mirror_2m").hide();

    $("#emoticon").show();
    $("#step").show();
    $("#data").show();
    $("#feedback").show();
    $("#realvideo").show();
    $("#connect").hide();
    $("#exerciselist").hide();
    $("#div_calendar").hide();
    $("#div_subway").hide();
    $("#div_dandan_squat").hide();

    page_squat();

    <!--21.04.15 speech test start-->
    $("#div_speech").hide();
    <!--21.04.15 speech test end-->
}

function page_squat(){
    location.href="/my-link/하체";
}