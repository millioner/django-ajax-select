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

    ///////////// Simple autocomplete ////////////////
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

    ///////// Autocomplete select (simple widget) ///////////
    /*
    Usage
    new django.autocompleteSelectSimple({
        text_el: text_input_el,
        deck_el: values_wrapper_el,
        lookup_url: "/some/url",
        default_value: [1, "Some title"],
        name: "field_name"
    });
    */
    django.autocompleteSelectSimple = function(options){
        this.options = $.extend({}, this.default_options, options || {});
        this.init();
    };

    $.extend(django.autocompleteSelectSimple.prototype, {
        default_options: {
            width: 320
        },
        // some kind of constructor
        init: function(){
            var self = this;

            self.init_autocomplete();

            if(self.options.default_value){
                self.receive_result(null, self.options.default_value);
            }
        },

        init_autocomplete: function(){
            var self = this;
            this.options.text_el.autocomplete(this.options.lookup_url, {
                width: this.options.width,
                formatItem: function(row) { return row[2]; },
                formatResult: function(row) { return row[1]; },
                dataType: "text"
            });

            self.options.text_el.result(function(event, data){ self.receive_result(event, data); });
        },

        receive_result: function(event, data) {
            var id = parseInt(data[0]),
                repr = data[1];

            this.kill_val();

            if(id){
                this.id_el = $('<input type="hidden" />').attr('name', this.get_name())
                                                         .insertAfter(this.options.text_el)
                                                         .val(id);
            } else {
                this.added_el = $('<input type="hidden" />').attr('name', this.options.get_name() + '[added]')
                                                            .insertAfter(this.options.text_el)
                                                            .val(repr);
            }

            this.add_value(repr, id);
            this.options.deck_el.trigger("added");
        },

        add_value: function(repr, id){
            var self = this,
                kill = $('<span class="iconic ajax-select-remove">X</span> ').click(function(e){
                    self.kill_val();
                    self.options.deck_el.trigger("killed");
                }),
                container = $('<div/>').html(repr).prepend(kill).appendTo(self.options.deck_el.empty());
            if(!id){
                container.addClass('added_item');
            }
        },

        kill_val: function(){
            if(this.id_el){ this.id_el.remove(); }
            if(this.added_el){ this.added_el.remove(); }
            this.options.text_el.val("");
            this.options.deck_el.children().remove();
        },

        get_name: function(){
            return this.options.text_el.attr('name').substr(0, this.options.text_el.attr('name').length - 5);
        }
    });
///////////////////////////////////////////////////////////////////////


////////////////// Multiple autocomplete select //////////////////////////
    /*
     Usage
     new django.autocompleteSelectMultipleSimple({
         text_el: text_input_el,
         deck_el: values_wrapper_el,
         lookup_url: "/some/url",
         default_values: [[1, "Some title"], ... ],
         name: "field_name"
     });
     */
    django.autocompleteSelectMultipleSimple = function(options){
        this.options = $.extend({}, this.default_options, options || {});
        this.init();
    };

    $.extend(django.autocompleteSelectMultipleSimple.prototype, {
        default_options: {
            width: 320,
            scrollHeight: 300
        },
        // some kind of constructor
        init: function(){
            var self = this;

            self.current_values = [];
            self.current_added_values = [];

            self.init_autocomplete();

            if(self.options.default_values){
                $.each(self.options.default_values, function(i, its){
                    self.receive_result(null, its);
                });
            }
        },

        init_autocomplete: function(){
            var self = this;
            this.options.text_el.autocomplete(this.options.lookup_url, {
                width: this.options.width,
                multiple: true,
                multipleSeparator: ";",
                scroll: true,
                scrollHeight:  this.options.scrollHeight,
                formatItem: function(row) { return row; },
                formatResult: function(row) { return row[1]; },
                highlight: function(row, term){
                    return row[0] != "0" && $.Autocompleter.defaults.highlight(row[2], term) || row[2].bold();
                },
                dataType: "text"
            });

            this.options.text_el.result(function(event, data){ self.receive_result(event, data); });
        },

        receive_result: function(event, data){
            var id = parseInt(data[0]),
                repr = data[1];
            if((id && this.current_values.lastIndexOf(id) == -1) ||
               (repr && this.current_added_values.lastIndexOf(repr) == -1))
            {
                this.add_item(repr, id);
                this.options.deck_el.trigger("added");
                if(id){
                    this.current_values.push(id);
                } else if(repr) {
                    this.current_added_values.push(repr);
                }
            }
            this.options.text_el.val('');
        },

        add_item: function(repr, id){
            var self = this,
                new_elem = $('<div class="autocomplete_item"></div>'),
                kill_link = $('<a class="iconic" href="#">X</a>').click(function(e){
                    self.kill_item(id, new_elem);
                    e.preventDefault();
                    return false;
                });

            if(id){
                var input = $('<input type="hidden" />').attr('name', self.get_name()).val(id);
            } else {
                var input = $('<input type="hidden" />').attr('name', self.get_name() + '[added]').val(repr);
            }

            $('<span/>').html(repr).append(kill_link).append(input).appendTo(new_elem);
            new_elem.appendTo(self.options.deck_el);
        },

        kill_item: function(id, item_elem){
            delete this.current_values[this.current_values.lastIndexOf(id)];
            item_elem.fadeOut().remove().trigger("killed");
        },

        get_name: function(){
            return this.options.text_el.attr('name').substr(0, this.options.text_el.attr('name').length - 5);
        }
    });
    /////////////////////////////////////////////////////////

    return django;

})(django || {});