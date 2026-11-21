(() => {
  const pages = [...document.querySelectorAll(".slide")];
  const previous = document.querySelector("#prev");
  const next = document.querySelector("#next");
  const counter = document.querySelector("output");
  let index = 0;
  function show(i) {
    index = Math.max(0, Math.min(pages.length - 1, i));
    pages.forEach((page, n) => page.classList.toggle("active", n === index));
    previous.disabled = index === 0;
    next.disabled = index === pages.length - 1;
    counter.value = (index + 1) + " / " + pages.length;
  }
  previous.onclick = () => show(index - 1);
  next.onclick = () => show(index + 1);
  document.addEventListener("keydown", event => {
    const keys = {ArrowRight:index+1, PageDown:index+1, ArrowLeft:index-1, PageUp:index-1, Home:0, End:pages.length-1};
    if (event.altKey || event.metaKey || event.ctrlKey || !(event.key in keys)) return;
    event.preventDefault();
    show(keys[event.key]);
  });
  show(0);
  document.documentElement.classList.add("ready");
})();
