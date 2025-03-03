    //ADMIN.JS
    // Toggle sidebar visibility
    function toggleSidebar() {
        document.getElementById('sidebar').classList.toggle('active');
        document.querySelector('.content').classList.toggle('active');
    }

    document.addEventListener('DOMContentLoaded', () => {
        // Handle search suggestions
        $('#search').autocomplete({
            source: function(request, response) {
                $.ajax({
                    url: "{{ url_for('search_autocomplete') }}",
                    data: { term: request.term },
                    success: function(data) {
                        response(data);
                    }
                });
            },
            minLength: 2
        });
    });
