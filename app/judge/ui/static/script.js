function localStorageTest() {
    let test = 'test';
    try {
        localStorage.setItem(test, test);
        localStorage.removeItem(test);
        return true;
    } catch(e) {
        return false;
    }
}
let lsavailible = localStorageTest();

var cache = {
    set: function(name, data, expire) {
        if (lsavailible) {
            var _data = JSON.stringify({ data: data, expire: (+new Date()) + expire * 1000 });
            localStorage.setItem(name, _data);
        } else {
            return false;
        }

        return true;
    },

    get: function(name) {
        if (lsavailible) {
            var item = localStorage.getItem(name);

            if (item === null) {
                return false;
            }

            item = JSON.parse(item);

            if ( item.expire < (+new Date()) ) {
                localStorage.removeItem(name);
                return false;
            } else {
                return item.data;
            }
        } else {
            return false;
        }
    }
}


function loadHtml(name, element, how) {
    let url = '/static/html_parts/' + name;
    let html = cache.get(url);

    function insert(data, element, how) {
        switch (how) {
            case 'append':
                element.append(data);
        }
    }

    if (html !== false) {
        insert(html, element, how);
    } else {
        $.get(url, function(data) {
            cache.set(url, data, 3600 * 24);
            insert(data, element, how);
        });
    }
}

function addNewTestbox() { loadHtml('simple_test_item.html', $('#tests-box'), 'append'); }

function saveNewTask(form) {
    console.log( form.serializeArray() );
}


$(document).ready(function() {
    $('#add-test-link').on('click', function(event) {
        event.preventDefault();
        event.stopPropagation();

        addNewTestbox();
    });

    $('#newtask-form').on('submit', function(event) {
        event.preventDefault();
        event.stopPropagation();

        saveNewTask($(this));
    });
});
