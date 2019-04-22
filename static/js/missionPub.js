$(document).ready(function() {
    $('#submit').click(function(evt) {
        evt.preventDefault();
        $.post('{{ url_for('updateMission') }}',
        {
        'mission':$('#mission-name').val(),
        'status':$('#visibility').val(),
        },
        function(resp){
          window.location.replace("{{url_for('modPanel')}}");
        });
    });
});
