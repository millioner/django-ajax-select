/*
 * jQuery Autocomplete plugin 1.1
 *
 * Copyright (c) 2009 Jörn Zaefferer
 *
 * Dual licensed under the MIT and GPL licenses:
 *   http://www.opensource.org/licenses/mit-license.php
 *   http://www.gnu.org/licenses/gpl.html
 *
 * Revision: $Id: jquery.autocomplete.js 15 2009-08-22 10:30:27Z joern.zaefferer $
 */

var django = (function(django) {
    var $ = null;
    if(typeof jQuery == 'function'){
        $ = jQuery;
    } else if(typeof django == 'object' && typeof django.jQuery == 'function'){
        $ = django.jQuery;
    }

    django.init_autocomplete = function(el){
        el.autocomplete(el.data('lookup_url'), {
            width: 320,
            formatItem: function(row) { return row[2]; },
            formatResult: function(row) { return row[1]; },
            dataType: "text"
        });
        el.result(function(event, data, formatted) {
            el.val(data[1]);
            el.trigger("added");
        });
    };

    django.init_autocomplete_select = function(wrapper){
        var text_el = wrapper.find('.autocomplete_text'),
            id_el = wrapper.find('.autocomplete_id'),
            deck_el = wrapper.find('.autocomplete_on_deck');

        text_el.autocomplete(text_el.data('lookup_url'), {
            width: 320,
            formatItem: function(row) { return row[2]; },
            formatResult: function(row) { return row[1]; },
            dataType: "text"
        });

        function receiveResult(event, data) {
            var prev = id_el.val(),
                id = parseInt(data[0]),
                idv = id || '"' + data[1].replace('|', '').replace('"', '') + '"';
            if(prev) {
                kill_val(prev);
            }
            id_el.val(idv);
            text_el.val("");
            add_killer(data[1], data[0]);
            deck_el.trigger("added");
        }

        text_el.result(receiveResult);

        function add_killer(repr, id){
            var kill = $('<span class="iconic ajax-select-remove">X</span> ').click(function(e){
                kill_val();
                deck_el.trigger("killed");
            });
            if(repr){
                deck_el.empty().append($("<div>" + repr + "</div>"));
            }
            deck_el.children("div").prepend(kill);
        }

        function kill_val(){
            id_el.val('');
            deck_el.children().remove();
        }

        id_el.bind('didAddPopup', function(event, id, repr) {
            receiveResult(null, [id, repr]);
        });

        deck_el.find('.ajax-select-remove').click(function(e){
            kill_val();
            deck_el.trigger("killed");
            e.preventDefault();
            return false;
        });
    };

    django.init_multiple_autocomplete_select = function(wrapper, default_values){

        var id_el = wrapper.find(".autocomplete_id"),
            text_el = wrapper.find(".autocomplete_text"),
            deck_el = wrapper.find('.results_on_deck').empty(),
            new_django_ajax_items_count = 0;

        text_el.autocomplete(text_el.data('lookup_url'), {
            width: 320,
            multiple: true,
            multipleSeparator: ";",
            scroll: true,
            scrollHeight:  300,
            formatItem: function(row) { return row; },
            formatResult: function(row) { return row[1]; },
            highlight: function(row, term){
                return row[0] != "0" && $.Autocompleter.defaults.highlight(row[2], term) || row[2].bold();
            },
            dataType: "text"
        });

        function receiveResult(event, data){
            var id = parseInt(data[0]),
                idv = id || '"' + data[1].replace('|', '').replace('"', '') + '"';
            if(id_el.val().indexOf("|" + idv + "|") == -1){
                if(id_el.val() == '') {
                    id_el.val('|');
                }
                id_el.val(id_el.val() + idv + "|");
                add_killer(data[1], id);
                text_el.val('');
                deck_el.trigger("added");
            }
        }

        text_el.result(receiveResult);

        function add_killer(repr, id){
            if(id){
                var killer_id = "kill_" + id_el.attr('id') + id,
                    new_elem_id = id_el.attr('id') + '_on_deck_' + id;
            } else {
                var killer_id = "kill_" + id_el.attr('id') + "_new" + new_django_ajax_items_count,
                    new_elem_id = id_el.attr('id') + '_new_' + new_django_ajax_items_count;
                new_django_ajax_items_count ++;
            }
            var kill = '<a class="iconic" href="#" id="' + killer_id + '">X</a> ',
                new_elem = $('<div id="' + new_elem_id +'"><span>' + kill + repr + '</span></div>')
                           .appendTo(deck_el);

            if(!id){
                new_elem.addClass('new_django_ajax_item');
            }

            $("#" + killer_id).click(function(e){
                if(id){
                    id_el.val(id_el.val().replace( "|" + id + "|", "|" ));
                } else {
                    id_el.val(id_el.val().replace( "|" + repr.replace('|', '') + "|", "|" ));
                }
                $("#" + new_elem_id).fadeOut().remove()
                    // send signal to enclosing p, you may register for this event
                    .trigger("killed");
                e.preventDefault();
                return false;
            });
        }

        $.each(default_values, function(i, its){
            add_killer(its[0], its[1]);
        });

        id_el.bind('didAddPopup', function(event, id, repr) {
            receiveResult(null, [id, repr]);
        });
    };

    return django;

})(django || {});