const SCROLL_SAVE_SPACE = 100 

// Хотфикс от загораживания бутстрапной fixed-top навигационной панелью контента страницы 
// Попросту делаем скролл через "animete" и отнимаем SCROLL_SAVE_SPACE, где предполагаем 
// наличие контента.
// А чтобы понять, куда скроллить получаем href, ведущий к якорю, очищаем и используем
// якорь уже как id для запроса к DOM и получению offset
$(function(){
    $('#toc-info').on('click','a',function(e){
        e.preventDefault();
      let section = this.href;
      let sectionClean = section.substring(section.indexOf("#"));
      
      // alert("jQuery alert box example !");
      $("html, body").animate({
        scrollTop: $(sectionClean).offset().top - SCROLL_SAVE_SPACE
      }, 500, function () {
        //window.location.hash = sectionClean;
      });
    });
});