function showConnect(){

    $("#div_main").hide();

    $("#exerciselist").hide();
    $("#div_calendar").hide();
    $("#div_subway").hide();
    $("#div_dandan_squat").hide();

    page_connect();

    <!--21.04.15 speech test start-->
    $("#div_speech").hide();
    <!--21.04.15 speech test end-->
}

function page_connect(){
    location.href="/connect";
}