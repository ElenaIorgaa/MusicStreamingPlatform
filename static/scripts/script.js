fetch('/colors')
    .then(response => response.json())
    .then(colors => {
        document.documentElement.style.setProperty('--home_background', colors.home_backround);
        document.documentElement.style.setProperty('--text_colour', colors.text_color);
        document.documentElement.style.setProperty('--list_colour', colors.list_color);
        document.documentElement.style.setProperty('--navbar_background', colors.navbar_background)
        document.documentElement.style.setProperty('--logo_first_color', colors.logo_first_color)
        document.documentElement.style.setProperty('--logo_second_color', colors.logo_second_color)
        document.documentElement.style.setProperty('--sidebar_background', colors.sidebar_background)
        document.documentElement.style.setProperty('--navbar_text_color', colors.navbar_text_color)
        document.documentElement.style.setProperty('--sidebar_text_color', colors.sidebar_text_color)
        document.documentElement.style.setProperty('--song_background', colors.song_background)
        document.documentElement.style.setProperty('--song-text', colors.song_text)
        document.documentElement.style.setProperty('--nav_text_hover', colors.nav_text_hover)
        document.documentElement.style.setProperty('--navbar_hover', colors.navbar_hover)
        document.documentElement.style.setProperty('--playlist_item_hover', colors.playlist_item_hover)
        document.documentElement.style.setProperty('--item_color', colors.item_color)
        document.documentElement.style.setProperty('--playlist_description_text_color', colors.playlist_description_text_color)
        document.documentElement.style.setProperty('--play_icon_color', colors.play_icon_color)
        document.documentElement.style.setProperty('--color_splash_color', colors.color_splash_color)
        document.documentElement.style.setProperty('--icon_text_color', colors.icon_text_color)
        document.documentElement.style.setProperty('--icon_color', colors.icon_color)
        document.documentElement.style.setProperty('--page_text_color', colors.page_text_color)
        document.documentElement.style.setProperty('--scrollbar_color', colors.scrollbar_color)
        document.documentElement.style.setProperty('--scrollbar_background_color', colors.scrollbar_background_color)
        document.documentElement.style.setProperty('--scrollbar_color_active', colors.scrollbar_color_active)
        document.documentElement.style.setProperty('--table_header_color', colors.table_header_color)
        document.documentElement.style.setProperty('--table_item_color', colors.table_item_color)
        document.documentElement.style.setProperty('--table_item_color_hover', colors.table_item_color_hover)
        document.documentElement.style.setProperty('--play_icon_not_playing_color', colors.play_icon_not_playing_color)
        document.documentElement.style.setProperty('--play_icon_playing_color', colors.play_icon_playing_color)
        document.documentElement.style.setProperty('--slice_ten_color', colors.slice_ten_color)
        document.documentElement.style.setProperty('--slice_nine_color', colors.slice_nine_color)
        document.documentElement.style.setProperty('--slice_eight_color', colors.slice_eight_color)
        document.documentElement.style.setProperty('--slice_seven_color', colors.slice_seven_color)
        document.documentElement.style.setProperty('--slice_six_color', colors.slice_six_color)
        document.documentElement.style.setProperty('--slice_five_color', colors.slice_five_color)
        document.documentElement.style.setProperty('--slice_four_color', colors.slice_four_color)
        document.documentElement.style.setProperty('--slice_three_color', colors.slice_three_color)
        document.documentElement.style.setProperty('--slice_two_color', colors.slice_two_color)
        document.documentElement.style.setProperty('--slice_one_color', colors.slice_one_color)
        document.documentElement.style.setProperty('--slices_background', colors.slices_background)
        document.documentElement.style.setProperty('--shazam_button_background', colors.shazam_button_background)
        document.documentElement.style.setProperty('--shazam_button_span_c', colors.shazam_button_span_c)
        document.documentElement.style.setProperty('--shazam_button_gradient_first_color', colors.shazam_button_gradient_first_color)
        document.documentElement.style.setProperty('--shazam_button_gradient_second_color', colors.shazam_button_gradient_second_color)
        document.documentElement.style.setProperty('--shazam_button_background_color', colors.shazam_button_background_color)
        document.documentElement.style.setProperty('--shazam_color_h1', colors.shazam_color_h1)
        document.documentElement.style.setProperty('--topbar_border_bottom', colors.topbar_border_bottom)
        document.documentElement.style.setProperty('--spotify_playlist_item_hover', colors.spotify_playlist_item_hover)
        document.documentElement.style.setProperty('--music_player_background', colors.music_player_background)
        document.documentElement.style.setProperty('--details_border', colors.details_border)
        document.documentElement.style.setProperty('--button-border', colors.button-border)
        document.documentElement.style.setProperty('--box_shadow', colors.box_shadow)
    });

// $(document).ready(function () {
function updateNavbarSong(song) {
    // if (song !== null) {
    $('#id').text(song[0]);
    const currentSrc = $('#audio-player source').attr('src');
    if (song[1] !== currentSrc) {
        $('#audio-player source').attr('src', song[1]);
        $('#audio-player')[0].load();
        $('#audio-player').on('loadedmetadata', function () {
            // Play the new song
            $('#audio-player')[0].play();
        });
    }

    // }
}

// function to get the current song from the server and update the navbar
function updateSong() {
    $.ajax({
        type: 'GET',
        url: '/current_song?' + new Date().getTime(),  // add a cache-busting query parameter
        success: function (song) {
            console.log('Current song: ' + song);
            updateNavbarSong(song);
        },
        error: function () {
            console.log('Error getting current song');
        }
    });
}

// call updateSong() once when the page is loaded
updateSong();

// call updateSong() every 5 seconds to check for updates
setInterval(updateSong, 400);
// });