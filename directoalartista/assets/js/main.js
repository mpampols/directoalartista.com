/**
 * Main JavaScript for Directo al Artista
 */

// JSON Global config object
var global_config = {
    "artistprofile_max_secondarycategories_4": 0,
    "artistprofile_max_secondarycategories_3": 1,
    "artistprofile_max_secondarycategories_2": 5,
    "artistprofile_max_secondarycategories_1": 5,
    "artistprofile_max_eventtypes_4": 2,
    "artistprofile_max_eventtypes_3": 6,
    "artistprofile_max_eventtypes_2": 6,
    "artistprofile_max_eventtypes_1": 6,
    "artistprofile_max_provinces_4": 2,
    "artistprofile_max_provinces_3": 4,
    "artistprofile_max_provinces_2": 99,
    "artistprofile_max_provinces_1": 99,
    "artistprofile_max_pictures_4": 1,
    "artistprofile_max_pictures_3": 7,
    "artistprofile_max_pictures_2": 7,
    "artistprofile_max_pictures_1": 7,
    "artistprofile_max_videos_4": 1,
    "artistprofile_max_videos_3": 7,
    "artistprofile_max_videos_2": 7,
    "artistprofile_max_videos_1": 7
}

/**
 * Gets the viewport width and height
 * @returns width and height {*[]}
 */
function getViewportData() {
    var viewportWidth;
    var viewportHeight;

    if (typeof window.innerWidth != 'undefined') {
        viewportWidth = window.innerWidth;
        viewportHeight = window.innerHeight;
    } else {
        // Unable to get properties, we'll return a legacy ones
        return [1200, 800];
    }

    return [viewportWidth, viewportHeight];
}


$(function(){

    /**
     * Cookie law plugin
     */
    $.cookieBar({
        append: true,
        policyButton: true,
        message: 'Utilizamos cookies propias y de terceros para mejorar la experiencia de navegaci&oacute;n. Al continuar navegando entendemos que se acepta nuestra política de cookies.',
        acceptText: 'Aceptar',
        policyButton: true,
        policyText: 'Pol&iacute;tica de cookies',
        policyURL: '/cookies',
    });

    /**
     * My account: disable account
     */
    if ($('#disable_account').get(0)) {
        var button ='<a class="btn btn-danger" href="disable">S&iacute;, estoy seguro</a>';
        $('#disable_account').popover({placement: 'right', content: button, html: true});
    }

    /**
     * Catalog: reset form
     */
    if ($('form[role="search"] a.reset').get(0)) {
        $('form[role="search"] a.reset').on("click", function() {
            $('form[role="search"] select').each(function() {
               this.selectedIndex = 0;
            });
            $('form[role="search"] input').each(function() {
               this.value = '';
            });
        });
    }

    /**
     * Navigation bar: various
     */
    $(".navbar-nav a.dropdown-toggle, li.navbar-nav .dropdown ul.dropdown-menu").mouseenter(function() {
        $(".navbar-nav a.dropdown-toggle").addClass("selected");
    });

    $("ul.dropdown-menu").mouseleave(function() {
        $(".navbar-nav a.dropdown-toggle").removeClass("selected");
    });

    $("a.dropdown-toggle").mouseleave(function() {
        $(".navbar-nav a.dropdown-toggle").removeClass("selected");
    });

    $("li.dropdown ul").mouseenter(function() {
        $(".navbar-nav a.dropdown-toggle").addClass("selected");
    })

    /**
     * Registration: add an empty option to select inputs
     */
    if ($('.registration-form').get(0)) {
        if ($("select#id_province").length > 0) {
            $("select#id_province").prop('selectedIndex', -1);
        }
    }

    /**
     * Artistic profile: utilities
     */
    if ($('.artistprofile-add').get(0) || $('.artistprofile-edit').get(0)) {

        /**
         * Count selected elements
         */
        var artist_plan = $("#form-artistplan").data("artistplan");
        var max_secondary_categories = global_config['artistprofile_max_secondarycategories_' + artist_plan];
        var max_event_types = global_config['artistprofile_max_eventtypes_' + artist_plan];
        var max_provinces = global_config['artistprofile_max_provinces_' + artist_plan];

        var sc_checkboxes = $('.artistprofile-add input[name="secondary_categories"],' +
            '.artistprofile-edit input[name="secondary_categories"]');
        var check_sc = function() {
            var current = sc_checkboxes.filter(':checked').length;
            
            sc_checkboxes.filter(':not(:checked)').prop(
                'disabled',
                current >= max_secondary_categories
            );

            if (current < max_secondary_categories) {
                disable_primary_category();
            }
        }
        sc_checkboxes.change(check_sc);
        sc_checkboxes.ready(check_sc);

        var et_checkboxes = $('.artistprofile-add input[name="event_type"], ' +
            '.artistprofile-edit input[name="event_type"]');
        var check_et = function() {
            var current = et_checkboxes.filter(':checked').length;
            et_checkboxes.filter(':not(:checked)').prop(
                'disabled',
                current >= max_event_types
            );
        }
        et_checkboxes.change(check_et);
        et_checkboxes.ready(check_et);

        var p_checkboxes = $('.artistprofile-add input[name="provinces"], ' +
            '.artistprofile-edit input[name="provinces"]');
        var check_p = function() {
            var current = p_checkboxes.filter(':checked').length;
            p_checkboxes.filter(':not(:checked)').prop(
                'disabled',
                current >= max_provinces
            );
        }
        p_checkboxes.change(check_p);
        p_checkboxes.ready(check_p);

        /**
         * Disable the selected main category on secondary categories listing
         */
        if ($(".checkbox.select-secondary-categories").get(0)) {
            // Disable the selected main category on form load
            disable_primary_category = function() {
                var selected_category = $('select#id_category').val();

                // Enable all options unless the selected one
                $("input[name='secondary_categories']").each(
                    function() {
                        if ($(this).val() == selected_category) {
                            $(this).prop('disabled', true);
                            $(this).prop('checked', false)
                        } else {
                            $(this).prop('disabled', false);
                        }
                    }
                );
            }

            $('select#id_category').change(disable_primary_category);
        }
    }

    /**
     * Artist profile: add new pictures
     */
    $("#profile-add-new-picture").bind("click", function(e) {
        e.preventDefault();
        var picture_number = $("#form-images-picturenumber").data("picturenumber");
        var max_pictures = global_config['artistprofile_max_pictures_' + $("#form-artistplan").data("artistplan")];
        if (picture_number < max_pictures) {
            $('<label for="id_image' + (picture_number + 1) + '" class="control-label">Fotografía ' + (picture_number + 1) + '</label>').insertAfter("input#id_image" + picture_number);
            $('<input id="id_image' + (picture_number + 1) + '" name="image' + (picture_number + 1) + '" type="file">').insertAfter('label[for="id_image' + (picture_number + 1) + '"]');
            $("#form-images-picturenumber").data("picturenumber", picture_number + 1);

            // Disable the add new picture link as the user reached it's limit
            if ((picture_number + 1) >= max_pictures) {
                $("#profile-add-new-picture").parent().hide();
            }
        }
    })

    /**
     * Artist profile: add new videos
     */
    $("#profile-add-new-video").bind("click", function(e) {
        e.preventDefault();
        var video_number = $("#form-videos-videonumber").data("videonumber");
        var max_videos = global_config['artistprofile_max_videos_' + $("#form-artistplan").data("artistplan")];
        if (video_number < max_videos) {
            $('<label for="id_video' + (video_number + 1) + '" class="control-label">Video ' + (video_number + 1) + '</label>').insertAfter("input#id_video" + video_number);
            $('<input class="form-control" id="id_video' + (video_number + 1) + '" maxlength="100" name="video' + (video_number + 1) + '" type="url">').insertAfter('label[for="id_video' + (video_number + 1) + '"]');
            $("#form-videos-videonumber").data("videonumber", video_number + 1);

            // Disable the add new picture link as the user reached it's limit
            if ((video_number + 1) >= max_videos) {
                $("#profile-add-new-video").parent().hide();
            }
        }
    })

    /**
     * Artist profile: add a "select all/none" toggle check
     */
    if ($('.checkbox.select-provinces').get(0)
        && ($("#form-artistplan").data("artistplan") == '1'
        ||  $("#form-artistplan").data("artistplan") == '2')) {
        $('.checkbox.select-provinces ul')
            .prepend('<li> \
                        <label for="provinces_all_none_toggle"> \
                            <input class="" id="provinces_all_none_toggle" name="all_none_toggle" type="checkbox" value="0"> Todas / Ninguna \
                        </label> \
                    </li>');
        $('#provinces_all_none_toggle').on("click", function() {
            var checkBoxes = $(".checkbox input[name='provinces']");
            checkBoxes.prop("checked", !checkBoxes.prop("checked"));
        })
    }

    /**
     * Artist profile: share
     */
    $('.share-bar .share-icon.facebook').parent().on('click', function(e) {
        e.preventDefault();
        window.open('https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent($(this).data('url')), 'facebook-share-dialog', 'width=626,height=436');
    });

    $('.share-bar .share-icon.twitter').parent().on('click', function(e) {
        e.preventDefault();
        window.open('https://twitter.com/intent/tweet?url=' + encodeURIComponent($(this).data('url')) + '&text=' + encodeURIComponent($(this).data('title')), 'twitter-share-dialog', 'width=550,height=420');
    });

    $('.share-bar .share-icon.google-plus').parent().on('click', function(e) {
        e.preventDefault();
        window.open('https://plus.google.com/share?url=' + encodeURIComponent($(this).data('url')), 'google-plus-share-dialog', 'width=626,height=436');
    });

    /**
     * Trigger the colorbox lightbox js
     */
    if ($('body.myaccountartist').get(0)) {
        $(function() {
            $(".gallery").colorbox(
                {
                    rel: 'gallery',
                    maxWidth: getViewportData()[0] - 50,
                    maxHeight: getViewportData()[1] - 50
                }
            );
        })
    }

    /**
     * Upload videos and pictures via ajax
     */
    if ($('body.artistprofile-edit').get(0)) {
        // Pictures uploader
        var uploadPictureMessage = "";
        var uploadPictureOptions = {
            url: 'upload/',
            dataType: "json",
            error: function(response) {
                uploadPictureMessage = '<span class="label label-error">Ha ocurrido un error, tranta de subir la foto otra vez.</span>';
                $('#fileInput').next().html(uploadPictureMessage);
                $('#fileInput').val('');
            },
            success: function(response) {
                if (response.status != 'success') {
                    uploadPictureMessage = '<span class="label label-' + response.status + '">' + response.result + '</span> ';
                    $('#fileInput').next().html(uploadPictureMessage);
                    $('#fileInput').val('');
                } else {
                    if (response.is_main == true) {
                        var highlighted = '<a href="/artistprofile/' + response.artist_profile_id +
                            '/picture/'+ response.picture_id +'/highlight" class="btn btn-success btn-block btn-sm" ' +
                            'disabled="disabled">Destacada</a>';
                    } else {
                        var highlighted = '<a href="/artistprofile/' + response.artist_profile_id +
                            '/picture/'+ response.picture_id +'/highlight" class="btn btn-success btn-block btn-sm">Destacar</a>';
                    }
                    var picture_block = '<div class="col-sm-4 col-md-2"> \
                                           <div class="thumbnail"> \
                                             <div class="wrapper" \
                                                  style="background-image:url(\'' + response.media_url + 'files/artistprofiles/' + response.picture_url + '.jpg\')"> \
                                             </div> \
                                             <div class="caption">'
                                                   + highlighted +
                                                 ' <a href="/artistprofile/' + response.artist_profile_id + '/picture/' + response.picture_id + '/delete" class="btn btn-danger btn-block btn-sm">Eliminar</a> \
                                             </div> \
                                           </div> \
                                         </div>';

                    $('#ajax-updated-block-pictures').append(picture_block);

                    message = '<span class="label label-' + response.status + '">' + response.result + '</span> ';
                    message = ( response.status == 'success' ) ? message : message;

                    if ($('.no-pictures').get(0)) {
                        $('.no-pictures').remove();
                    }

                    $('#fileInput').next().html(message);
                    $('#fileInput').val('');
                }
            }
        };

        $('#fileInput').change(function() {
            $('#fileInput').next().append('<img src="/static/img/ajax-loader.gif"/>');
            $('#uploadForm').ajaxSubmit(uploadPictureOptions);
            return false;
        });

        // Videos uploader
        var uploadVideoMessage = "";
        var uploadVideoOptions = {
            url: 'addvideo/',
            dataType: "json",
            error: function(response) {
                uploadVideoMessage = '<span class="label label-error">Ha ocurrido un error, tranta de subir el vídeo otra vez.</span>';
                $('#fileInput').next().html(uploadVideoMessage);
                $('#fileInput').val('');
            },
            success: function(response) {
                if (response.status != 'success') {
                    message = '<span class="label label-danger">' + response.result + '</span> ';
                    $('#add-video').next().html(message);
                    $('#videoInput').val('');
                } else {
                    var video_block = '<div class="col-sm-4 col-md-2"> \
                                           <div class="thumbnail"> \
                                               <img src="' + response.video_url + '" /> \
                                               <div class="caption"> \
                                                   <a href="/artistprofile/' + response.artist_profile_id + '/video/'+ response.video_id +'/delete" class="btn btn-danger btn-block btn-sm">Eliminar</a> \
                                               </div> \
                                           </div> \
                                       </div>';

                    $('#ajax-updated-block-videos').append(video_block);

                    message = '<span class="label label-' + response.status + '">' + response.result + '</span> ';
                    message = ( response.status == 'success' ) ? message : message;

                    if ($('.no-videos').get(0)) {
                        $('.no-videos').remove();
                    }

                    $('#add-video').next().html(message);
                    $('#videoInput').val('');
                }
            }
        };

        // Videos uploader
        $('#add-video').click(function() {
            $('#add-video').next().append('<img src="/static/img/ajax-loader.gif"/>');
            $('#addVideoForm').ajaxSubmit(uploadVideoOptions);
            return false;
        });
    }

});