function showDandanWhole(){

    $("#div_main").hide();

    $("#data").show();
    $("#name").show();
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