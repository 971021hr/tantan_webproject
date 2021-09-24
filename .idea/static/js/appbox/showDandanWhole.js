function showDandanWhole(){

    $("#div_main").hide();

    $("#emoticon").show();
    $("#step").show();
    $("#data").show();
    $("#feedback").show();
    $("#realvideo").show();
    $("#exerciselist").hide();
    $("#div_calendar").hide();
    $("#div_subway").hide();
    $("#div_dandan_squat").hide();

    page_whole();

    <!--21.04.15 speech test start-->
    $("#div_speech").hide();
    <!--21.04.15 speech test end-->
}


function page_whole(){
    location.href="/my-link/전신";
}