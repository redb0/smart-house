/**
 * Created by Владимир on 06.08.2018.
 */
document.getElementById("submenu_active").addEventListener('click', function(e){
  	document.getElementById("submenu_active").querySelectorAll('.active, .bd-sidenav-active')[0].removeAttribute("class");
    e.target.setAttribute("class", "active bd-sidenav-active");
});