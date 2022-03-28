function setTheme(mode) {
    button = $("#colour-mode-button")
    if (mode === "dark") {
      $("body").attr("data-theme", "dark")
      button.removeClass("fa-dragon")
      button.addClass("fa-dungeon")
      $('link[rel=stylesheet][href~="./assets/webix/skins/contrast.css"]').prop('disabled', false);
      localStorage.setItem('mode', 'dark');
    }
    else {
      $("body").attr("data-theme", "light")
      button.addClass("fa-dragon")
      button.removeClass("fa-dungeon")
      $('link[rel=stylesheet][href~="./assets/webix/skins/contrast.css"]').prop('disabled', true);
      localStorage.setItem('mode', 'light');
    }
  }
  
function toggleColourMode() {
    mode = $("body").attr("data-theme")
    if (mode === "dark") {
      setTheme("light")
    }
    else {
      setTheme("dark")
    }
  }