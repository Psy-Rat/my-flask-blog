const SCROLL_SAVE_SPACE = 0 

// Хотфикс от загораживания бутстрапной fixed-top навигационной панелью контента страницы 
// Попросту делаем скролл через "animete" и отнимаем SCROLL_SAVE_SPACE, где предполагаем 
// наличие контента.
// А чтобы понять, куда скроллить получаем href, ведущий к якорю, очищаем и используем
// якорь уже как id для запроса к DOM и получению offset

//(UPD) Пофикшено :
// padding-top == ~margin-top н h (entity-header)

$(function(){
    $('#toc-info').on('click','a',function(e){
      e.preventDefault();
      let section = this.href;
      let sectionClean = section.substring(section.indexOf("#"));

      $("html, body").animate({
        scrollTop: $(sectionClean).offset().top - SCROLL_SAVE_SPACE
      }, 500, function () {
        window.location.hash = sectionClean;
      });
    });
});

$(function(){
  $('.entity-header').mouseover(function () { 
    $(this).children(".inline-anchor:first").stop()
    $(this).children(".inline-anchor:first").animate({
      opacity: 1.,
    }, 300, function(){});
  });
});


$(function(){
  $('.entity-header').mouseleave(function () { 
    $(this).children(".inline-anchor:first").stop()
    $(this).children(".inline-anchor:first").animate({
      opacity: .5,
    }, 300, function(){});
  });
});


