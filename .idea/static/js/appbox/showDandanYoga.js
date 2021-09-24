function showDandanYoga(){

    $("#div_main").hide();

    $("#data").show();
    $("#feedback").show();
    $("#realvideo").show();
    $("#exerciselist").hide();
    $("#div_calendar").hide();
    $("#div_subway").hide();
    $("#div_dandan_squat").hide();

    page_yoga();

    <!--21.04.15 speech test start-->
    $("#div_speech").hide();
    <!--21.04.15 speech test end-->
}


function page_yoga(){
    location.href="/my-link/요가";
}