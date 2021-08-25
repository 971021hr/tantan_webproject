function showDandanUp(){

    $("#div_main").hide();

    $("#data").show();
    $("#name").show();
    $("#realvideo").show();
    $("#exerciselist").hide();
    $("#div_calendar").hide();
    $("#div_subway").hide();
    $("#div_dandan_squat").hide();

    page_up();

    <!--21.04.15 speech test start-->
    $("#div_speech").hide();
    <!--21.04.15 speech test end-->
}


function page_up(){
    location.href="/my-link/상체";
}