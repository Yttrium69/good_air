$(document).ready(function () {
    $(".big_religion").on("change", fill_up_middle_religion);
    $(".middle_religion").on("click", fill_up_small_religion);
})

function toggle_near_plant(target) {
    target_obj = $(target);
    target_obj.hasClass("selected") ? target_obj.removeClass("selected") : target_obj.addClass("selected");
}

function clicked_near_plant(target) {
    toggle_near_plant(target);
    target = $(target);
    $.getJSON({
        url: "/click_near_plant", data: { 'plant' : $(target).text() }, success: function (result) {
            Plotly.newPlot('chart', result, {staticPlot: true});;
        }
    });
    // console.log(get_selected_plants());
}

function clicked_axis(target) {
    toggle_axis_selection(target);
}

function toggle_axis_selection(target) {
    target = $(target);
    let axis_selection;
    if (target.hasClass("left_axis")) {
        axis_selection = $(".left_axis_selection");
    }
    else {
        axis_selection = $(".right_axis_selection");
    }
    axis_selection.hasClass("hide") ? axis_selection.removeClass("hide") : axis_selection.addClass("hide");
}

function clicked_axis_matter_left(target) {
    target = $(target);
    target.hasClass("selected") ? target.removeClass("selected") : target.addClass("selected");
    $.getJSON({
        url: "/matter_click_left", data: { 'matter' : $(target).text() }, success: function (result) {
            Plotly.newPlot('chart', result, {staticPlot: true});;
        }
    });
}

function clicked_check_btn(target){
    fetch(`/check_rule?checked=${$(target).data("rule")}`)

    if($(target).prev().is(':checked')){
        $(target).removeClass("selected")
        $(target).css("background", "url('../static/img/icons/icon_check_false.svg')");
    }
    else{
        $(target).addClass("selected");
        $(target).css("background", `url('../static/img/icons/icon_check_true_${$('.div_rulebase .selected').length}.svg')`);
    }
}

function clicked_axis_matter_right(target) {
    target = $(target);
    target.hasClass("selected") ? target.removeClass("selected") : target.addClass("selected");
    $.getJSON({
        url: "/matter_click_right", data: { 'matter' : $(target).text() }, success: function (result) {
            Plotly.newPlot('chart', result, {staticPlot: true});;
        }
    });
}

function clicked_search_btn() {
    pop_search_modal();
}

function pop_search_modal() {
    $("body").css("overflow", "hidden");
    modal_page = $(".page_search_modal");
    modal_page.removeClass("hide");
}

function hide_parent_of(target) {
    $("body").css("overflow", "scroll");
    $(target).parent().addClass("hide");
    console.log($(target).parent())
}

function  fill_up_middle_religion() {
    let gogo_json = JSON.parse(JSON.stringify(rel_json()));
    let big_religion = $(".big_religion").val();
    let middle_religions = gogo_json[big_religion];
    let middle_religion_list = keys_of(middle_religions);
    $(".middle_religion").empty();
    
    fetch(`/get_same_value?big_religion=${big_religion}`).
    then(response=>response.json())
    .then(gogo_json=>{
        console.log(gogo_json)
    })
    .then(final_value=>{
        console.log(final_value)
        $(".gogogo").val(final_value);
    })


    middle_religion_list.map(function (religion) { $(".middle_religion").append(`<option  value="${religion}">${religion}</option>`) })

    $(".pre_middle_religion").val(religion);
    $(".pre_middle_religion").innerText(religion);



    fetch(`/change_religion?big_religion=${big_religion}`)
    .then(function(response){console.log("GOGOGOGO")})
    .then(function(){
    })
    .catch(error=>{console.log(error)})


}


function fill_up_small_religion() {
    let gogo_json = JSON.parse(JSON.stringify(rel_json()));

    let big_religion = $(".big_religion").val();
    let middle_religion = $(".middle_religion").val();
    let small_religions = gogo_json[big_religion][middle_religion];
    $(".small_religion").empty();
    small_religions.map(function (religion) { $(".small_religion").append(`<option value="${keys_of(religion)} (${Object.values(religion).toString()})">${keys_of(religion)} (${Object.values(religion).toString()})</option>`) });

    // $(".pre_small_religion").val(religion);
    // $(".pre_small_religion").innerText(religion);
}

function keys_of(json) {
    return Object.keys(json).map(function (key) { return key.toString() })
}

function fill_up_graphs() {
    plants = get_selected_plants();
    fetch(`/get_graph_data?plants= ${plants}`).then
        (function (response) {
            JSON.parse(JSON.stringify(response))
        }).then
        (function (result) {
            console.log(result);
        }).error
        (function () {
            console.log("something wrong")
        })
}

function get_selected_plants() {
    let selected_near_plants = $(".container_plant_element .selected p");
    console.log(selected_near_plants[0].text)
    let now_plant = $(".this_plant").text();
    return selected_near_plants;
}

function clicked_check_option_standard(self) {
    if ($(".small_religion").val() == null) {
        alert("지역을 먼저 선택하세요.");
    }
    else {
        let rule_id = $(self).data("rule_id");
        let inputs = $(self).parent().children("input");
        let standards = $.makeArray(inputs).map(function (input) {
            return (`{${$(input).data("key")}:${$(input).val()}}`)
        })
        let religion_id = $(".big_religion").val();
        fetch(
            `/set_rulebase?rule_id=${rule_id}&standards=${standards}&religion_id=${religion_id}`
        )
            .then(res => alert("성공적으로 반영되었습니다."))
            .catch(error => alert("문제가 발생했습니다."));
    }
}

function changed_multiple_of_matter(self){
    let matter = $(self).data("matter")
    let multiple_factor = self.value;
    let gogo_json = {
        'matter':matter,
        'multiple_factor':multiple_factor
    }
    // $(`.multiple_of_${matter}`).val(multiple_factor);

    fetch('/change_multiple_factor_of_matter', {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(gogo_json)
    })
    .then(response=>{console.log(response)});
    
}