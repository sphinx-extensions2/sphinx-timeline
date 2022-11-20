// On page load,
// look for all divs with class "tl-item" and attribute "data-dt"
// and a "dt-future" or "dt-past" class to each div, based on the current date.
document.addEventListener("DOMContentLoaded", function () {
  const now = new Date();
  const nodes = document.querySelectorAll("div.tl-item[data-dt]");
  for (var i = 0, len = nodes.length; i < len; i++) {
    try {
      var dt = new Date(nodes[i].getAttribute("data-dt"));
    } catch (e) {
      console.warn(`Error parsing date: ${dt}`);
      continue;
    }
    if (dt > now) {
      nodes[i].classList.add("dt-future");
    } else {
      nodes[i].classList.add("dt-past");
    }
  }
});
