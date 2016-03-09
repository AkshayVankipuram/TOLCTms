$(function() {
    
    var streamer = $('#streamer');    

    var idx = 0;

    setInterval(function() {
        var long_str = stream_data[idx].title + ' ' + stream_data[idx].end + ';';
        idx = (idx + 1) % stream_data.length;
        streamer.text(long_str);
    }, 1000);

});
