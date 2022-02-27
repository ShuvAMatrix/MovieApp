$(document).ready(function() {
    var columnCount = $(".columns li").length;
    if (columnCount <= 10) {
        $(".columns").addClass("one-col");
    } else{
        $(".columns").addClass("two-col");
    }
})

    document.getElementById("releaseyear")
        .addEventListener('change', (e) => {
            $('#imdbURL').addClass("loading")
            document.getElementById("imdbURL").value = "";
            var mname = document.getElementById("moviename").value;
            var flag = 0
            var val = e.currentTarget.value;
            var url = "/googlesearch/"+ mname + " " + val
            try{
                $.get(url, function(response) {
                    if(response == ""){
                        document.getElementById("imdbURL").value = "Error! Please fill URL manually"
                    }
                    for (let i = 0; i < response["length"]; i++) {
                        if (response["results"][i].startsWith("https://www.imdb.com/title/")){
                            document.getElementById("imdbURL").value = response["results"][i];
                            flag = 1
                            break
                        }
                    }
                    if(flag == 0){
                        document.getElementById("imdbURL").value = "Error! Please fill URL manually"
                    }
                    document.getElementById("imdbURL").focus();
                    $('#imdbURL').removeClass("loading")
                    $('#moviename').addClass("loading")
                });
            }
            catch{
                document.getElementById("imdbURL").value = "Error! Please fill URL manually"
            }
        });
    
    
    function submitModalForm(){
        var moviename = document.getElementById("moviename").value
        var releaseyear = document.getElementById("releaseyear").value
        var url = document.getElementById("movieURL").value
        var imdbURL = document.getElementById("imdbURL").value
        if(moviename != "" && releaseyear != "" && url != "" && imdbURL != ""){
            document.getElementById("addMovieForm").submit()
        }
        else{
            if(moviename == ""){
                $("#addedmovienamediv").removeClass('invisible');
            }
            if(releaseyear == ""){
                $("#addedmovieyeardiv").removeClass('invisible');
            }
            if(url == ""){
                $("#addedmovieurldiv").removeClass('invisible');
            }
            if(imdbURL == ""){
                $("#addedmovieimdburldiv").removeClass('invisible');
            }
        }
    }

    $( "#moviename" ).focus(function() {
        $("#addedmovienamediv").addClass('invisible');
    });
    $( "#releaseyear" ).focus(function() {
        $("#addedmovieyeardiv").addClass('invisible');
    });
    $( "#movieURL" ).focus(function() {
        $("#addedmovieurldiv").addClass('invisible');
    });
    $( "#imdbURL" ).focus(function() {
        $("#addedmovieimdburldiv").addClass('invisible');
    });

    (function() {
        'use strict';
        window.addEventListener('load', function() {
        // Fetch all the forms we want to apply custom Bootstrap validation styles to
        var forms = document.getElementsByClassName('needs-validation');
        // Loop over them and prevent submission
        var validation = Array.prototype.filter.call(forms, function(form) {
        form.addEventListener('submit', function(event) {
        if (form.checkValidity() === false) {
        event.preventDefault();
        event.stopPropagation();
        }
        form.classList.add('was-validated');
        }, false);
        });
        }, false);
    })();

    let lilSearchBox = document.getElementById("littleSearch");
    var query = "";
    // lilSearchBox.addEventListener("keydown", function onEvent(event) {
    //     if((event.keyCode >= 48 && event.keyCode <= 59) || (event.keyCode >= 65 && event.keyCode <= 90)|| 
    //     (event.keyCode >= 96 && event.keyCode <= 105) || event.keyCode==32 || (event.keyCode >= 186 && event.keyCode <= 190)){
    //         query += event.key
    //     }
    //     if(event.keyCode == 8){
    //         query = query.slice(0, -1) 
            
    //     }
    //     if(lilSearchBox.hasAttribute("autocompleted")){
    //         query=event.key
    //     }
    //     console.log(query)
        
    // });
    var searchTimer;
    var searchInterval = 1000;

    $(() => {
        $('#littleSearch').on('input', (event) => {
            if($('#searchResults').find("span").length > 0){
                $('#searchResults').find("span").remove(); 
            }
            clearTimeout(searchTimer);
            searchTimer = setTimeout(() => {
                if(event.target.value.length >= 3){
                    searchContacts(event.target.value);
                }
            }, (event.target.value.length > 0) ? searchInterval : 0);
        });
    });

    function searchContacts(val) {
        var url = '/apisearch/' + val
        try{
            $('#littleSearch').addClass("loading")
            $.get(url, function(response) {
                var result = response["results"]
                var length = response["length"]
                var preDiv1 = '<span class="input-group-text border-0" style="background-color: #212529;"><div class="col col-6 h6 text-white text-left"><a style="font-size: 14px;" class="text-decoration-none searchLink" href="/new"><i>Detailed Search</i></a></div> <div class="col col-6 h6 text-white text-right"><a style="font-size: 14px;" class="text-decoration-none searchLink" href="/new"><i>View All</i></a></div></span>'
                var preDiv2 = '<span class="input-group-text border-0" style="background-color: #212529;"><div class="col col-12 h6 text-white text-left" style="font-size: 14px;"><i>Not found? Perform a </i><a class="text-decoration-none searchLink" href="/new"><b><i> Detailed Search</i></b></a></div></span>'
                if(length > 5){
                    $('#searchResults').prepend(preDiv1)
                }
                else{
                    $('#searchResults').prepend(preDiv2)
                }
                
                for(i=0; i<result.length; i++){
                    var results = result[i]
                    var url = "/moviedetails/"+results["id"]
                    var eachMovie = ''
                    eachMovie += '<span style="background-color: #212529;" class="border-bottom input-group-text justify-content-center align-items-center text-white border-0"><div class="m-1 container"><div class="row row-cols-2"><div class="column col-3 text-left"><a class="text-decoration-none" href="'
                    eachMovie += url
                    eachMovie += '"><img style="max-height: 100px;" src="'
                        
                    var posterPath = "https://image.tmdb.org/t/p/w500" + results["poster_path"]
                    if(posterPath=="https://image.tmdb.org/t/p/w500null"){
                        posterPath = "../../../static/img/notAvailable.jpg"
                    }
                    eachMovie += posterPath
                    eachMovie += '" alt="img" class="img-fluid"></a></div><div class="column overflow text-left justify-content-center align-items-center"><div class="row"><div class="h6 mb-1"><a class="text-white text-decoration-none" href="'
                    eachMovie += url
                    eachMovie += '">'
                    eachMovie += results["title"].substring(0,29)
                    eachMovie += '</a></div></div><div class="row"><div class="h6 mb-1" style="font-size:12px">'
                    var fullYear = results["release_date"]
                    eachMovie += fullYear.split("-")[0]
                    eachMovie += '</div><div class="h6 mb-1" style="font-size:12px">Rating : '
                    var rating = results["vote_average"]
                    if(rating == "0"){
                        rating = "NA"
                    }
                    eachMovie += rating
                    eachMovie += '</div></div></div></div></div></span>'
                    $('#searchResults').prepend(eachMovie)
                    
                }
                $('#littleSearch').removeClass("loading")
                $('#searchResults').removeAttr("hidden")
                
            });
        }
        catch{
            document.getElementById("imdbURL").value = "Error! Please fill URL manually"
        }
    }