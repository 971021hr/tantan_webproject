function showDandanList(){

    $("#div_main").hide();
    $("#div_dandan").hide();

    $("#connect").hide();
    $("#div_calendar").hide();
    $("#div_subway").hide();
    $("#div_dandan_squat").hide();

    page_list();

    //connect
    $("#connect").hide();

    <!--21.04.15 speech test start-->
    $("#div_speech").hide();
    <!--21.04.15 speech test end-->
}

function page_list(){
    location.href="/list";
}