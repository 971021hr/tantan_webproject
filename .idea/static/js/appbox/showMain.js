function showMain(){

    $("#div_main").hide();

    //connect hide
    $("#connect").hide();

    //dandan hide
    $("#div_dandan").hide();
    $("#emoticon").hide();
    $("#step").hide();
    $("#data").hide();
    $("#feedback").hide();
    $("#realvideo").hide();
    $("#exerciselist").hide();

    //달력, 지하철 hide
    $("#div_calendar").hide();
    $("#div_subway").hide();
    $("#div_dandan_squat").hide();

    page_main();

    <!--21.04.15 speech test start-->
    $("#div_speech").hide();
    <!--21.04.15 speech test end-->
}

function page_main(){
    location.href="/";
}