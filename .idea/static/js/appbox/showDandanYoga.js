function showDandanYoga(){

    $("#div_main").hide();
    $("#div_dandan").show();

    $("#emoticon").show();
    $("#step").show();
    $("#data").show();
    $("#feedback").show();
    $("#yoga").show();
    $("#realvideo").hide();
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