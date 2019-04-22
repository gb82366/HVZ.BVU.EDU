$(document).ready(function () {
	var open=true;
    $('.sidebarToggle').on('click', function () {

        if ($("#navList").children().length == 8){
          $('#sidebar').toggleClass('activeMod');
        }
        else if ($("#navList").children().length == 7){
          $('#sidebar').toggleClass('activePlayer');
        }

        else if ($('#navList').children().length == 4){
          $('#sidebar').toggleClass('activeAnon');
        }

        $('#navList').toggleClass('bgActive');
        $('#sbToggleImg').toggleClass('rotated');
        $('#c').toggleClass('left');

    });
});
