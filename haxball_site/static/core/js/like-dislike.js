function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        // Настройка AJAX
        $(function () {
            $.ajaxSetup({
                headers: {"X-CSRFToken": getCookie("csrftoken")}
            });
        });

        var elClass = '.vote';

        function like() {
            var like = $(this);
            var type = like.data('type');
            var pk = like.data('id');
            var action = like.data('action');
            var dislike = like.next();

            var l_id = 'l' + type + pk
            var d_id = 'd' + type + pk
            $('#' + l_id).toggleClass('text-success');
            $('#' + d_id).removeClass('text-danger');

            $.ajax({
                url: "/api/" + type + "/" + pk + "/" + action + "/",
                type: 'POST',
                data: {'obj': pk},

                success: function (json) {
                    like.find("[data-count='like']").text(json.like_count);
                    dislike.find("[data-count='dislike']").text(json.dislike_count);
                }
            });

            return false;

        }


        function dislike() {
            var dislike = $(this);
            var type = dislike.data('type');
            var pk = dislike.data('id');
            var action = dislike.data('action');
            var like = dislike.prev();

            var l_id = 'l' + type + pk
            var d_id = 'd' + type + pk
            $('#' + d_id).toggleClass('text-danger');
            $('#' + l_id).removeClass('text-success');


            $.ajax({
                url: "/api/" + type + "/" + pk + "/" + action + "/",
                type: 'POST',
                data: {'obj': pk},

                success: function (json) {
                    dislike.find("[data-count='dislike']").text(json.dislike_count);
                    like.find("[data-count='like']").text(json.like_count);
                }
            });

            return false;
        }



        // Подключение обработчиков
        $(function () {
            $('[data-action="like"]').click(like);
            $('[data-action="dislike"]').click(dislike);


        });





