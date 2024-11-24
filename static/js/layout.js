document.querySelector('.left-top-menu-button-checkBox').addEventListener("change", function(){
    const left_vertical_menu = document.querySelector('.vertical-menu');
    const vertical_menu_checkBox = document.querySelector('.left-top-menu-button-icon')
    const left_top_web_name_icon = document.querySelector('.left-top-web-name-icon')

    if(this.checked){
        left_vertical_menu.style.transform = 'translateX(0)'

        if (window.innerWidth <= 768) {
            vertical_menu_checkBox.style.transform = 'translateX(20vw) scale(1.5)';
            left_top_web_name_icon.style.opacity = '0'
        }
        else {
            vertical_menu_checkBox.style.transform = 'translateX(20vw) scale(1.5)';
            left_top_web_name_icon.style.opacity = '0'
        }
        
    } 
    else {
        left_top_web_name_icon.style.opacity = '1'
        left_vertical_menu.style.transform = 'translateX(-100%)';
        vertical_menu_checkBox.style.transform = 'translateX(0) scale(1.5)';
    }
} );